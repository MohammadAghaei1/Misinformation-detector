from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.scraping import scrape_article
from backend.storage import append_record, clear_all_history, update_record_feedback, read_history, check_cache, get_stats_data
# Import the new Auth functions from your storage
from backend.storage import verify_user, create_user 
from backend.llm_judge import judge_news
from dotenv import load_dotenv
import json
import uuid
import datetime
import os
import pandas as pd

load_dotenv()

app = FastAPI()

# --- NEW AUTH MODELS ---

class UserAuth(BaseModel):
    email: str
    password: str

# --- UPDATED ORIGINAL MODELS (Adding user_id) ---

class PredictRequest(BaseModel):
    text: str
    user_id: int # Added to link text analysis to user

class ScrapeRequest(BaseModel):
    url: str
    user_id: int # Added to link URL analysis to user
    
class FeedbackRequest(BaseModel):
    id: str
    feedback: str

class FinalRecordRequest(BaseModel):
    text: str
    label: str
    confidence: float
    explanation: str
    reviewer_feedback: str
    user_id: int # Added
    input_type: str = "text"
    url: str = ""
    title: str = "N/A"

# --- NEW AUTH ENDPOINTS ---

@app.post("/signup")
def signup(data: UserAuth):
    success = create_user(data.email, data.password)
    if not success:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "User created successfully"}

@app.post("/login")
def login(data: UserAuth):
    # Call the updated verify_user from storage.py
    result = verify_user(data.email, data.password)
    
    # 1. Handle case where Email is not found
    if result == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=404, 
            detail="Email not found. Please register first."
        )
    
    # 2. Handle case where Password is incorrect
    if result == "WRONG_PASSWORD":
        raise HTTPException(
            status_code=401, 
            detail="Incorrect password. Please try again."
        )
    
    # 3. If login is successful, return the user_id
    return {"user_id": result}

# --- UPDATED ORIGINAL ENDPOINTS ---

@app.get("/stats")
def get_stats(user_id: int):
    # Pass user_id to your stats function
    return get_stats_data(user_id) 

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Misinformation Detector!"}

@app.post("/predict")
def predict(req: PredictRequest):
    try:
        # Check cache (Logic remains same)
        cached = check_cache(req.text)
        if cached:
            return {**cached, "id": "CACHED", "source": "database"}
        
        result = judge_news(req.text)
        record_id = str(uuid.uuid4())[:8]
        
        record = {
            "id": record_id,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input_type": "text",
            "url": "",
            "title": "N/A",
            "text": req.text,
            "label": result.get("label"),
            "confidence": result.get("confidence"),
            "explanation": result.get("explanation"),
            "reviewer_feedback": "The user did not post a feedback."
        }
        # Updated to include user_id
        append_record(record, req.user_id)
        return {"id": record_id, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_url")
def analyze_url(req: ScrapeRequest):
    try:
        article = scrape_article(req.url)
        
        cached = check_cache(article["text"])
        if cached:
            return {**cached, "source": "database"}

        result = judge_news(article["text"], is_url=True) 
        
        record_id = str(uuid.uuid4())[:8] 
        record = {
            "id": record_id,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input_type": "url",
            "url": article["url"],
            "title": article["title"],
            "text": article["text"],
            "label": result.get('label'),
            "confidence": result.get('confidence'),
            "explanation": result.get('explanation'),
            "reviewer_feedback": "The user did not post a feedback."
        }
        # Updated to include user_id
        append_record(record, req.user_id)
        return {"id": record_id, **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/history")
def history(user_id: int, limit: int = 50):
    try:
        # Pass user_id to filter history
        df = read_history(user_id, limit)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update_feedback")
def update_feedback(req: FeedbackRequest):
    success = update_record_feedback(req.id, req.feedback)
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Record not found")
    
@app.post("/clear_history")
def clear_history(user_id: int):
    try:
        # Only clear records for this specific user
        clear_all_history(user_id)
        return {"status": "success", "message": "Your history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")