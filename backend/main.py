import uuid
import datetime
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.llm_judge import judge_news
from fastapi import FastAPI, HTTPException
from backend.scraping import scrape_article
from backend.storage import append_record, clear_all_history, update_record_feedback, read_history, check_cache, get_stats_data, verify_user, create_user

load_dotenv()

app = FastAPI()

# Data model for user authentication (Login/Signup)
class UserAuth(BaseModel):
    email: str
    password: str

# Data model for news prediction requests containing text and user ID
class PredictRequest(BaseModel):
    text: str
    user_id: int 

# Data model for URL-based analysis requests, including the target URL and user ID
class ScrapeRequest(BaseModel):
    url: str
    user_id: int # Added to link URL analysis to user
    
# Data model for submitting user feedback on a specific analysis record    
class FeedbackRequest(BaseModel):
    id: str
    feedback: str

# Comprehensive data model representing a full analysis record for storage
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

# Handles new user registration by hashing passwords and storing credentials
@app.post("/signup")
def signup(data: UserAuth):
    # success is True if user was created, False if email already exists
    success = create_user(data.email, data.password)
    if not success:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "User created successfully"}

# Authenticates users and returns a unique user ID upon successful login
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

# Retrieves analysis statistics (Total, Fake, Real) for a specific user ID
@app.get("/stats")
def get_stats(user_id: int):
    # Pass user_id to your stats function
    return get_stats_data(user_id) 

# Returns the operational status of the API server
@app.get("/health")
def health():
    return {"status": "ok"}

# Simple root endpoint to verify the API is running and welcome users
@app.get("/")
def read_root():
    return {"message": "Welcome to the Misinformation Detector!"}

# Analyzes raw news text, checks for cached results, and stores the verdict
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

# Scrapes content from a provided URL and performs misinformation analysis
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

# Fetches a list of previous analysis records filtered by the user's ID    
@app.get("/history")
def history(user_id: int, limit: int = 50):
    try:
        # Pass user_id to filter history
        df = read_history(user_id, limit)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Updates the feedback field of an existing record in the database
@app.post("/update_feedback")
def update_feedback(req: FeedbackRequest):
    success = update_record_feedback(req.id, req.feedback)
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Record not found")

# Deletes all analysis history records associated with a specific user 
@app.post("/clear_history")
def clear_history(user_id: int):
    try:
        # Only clear records for this specific user
        clear_all_history(user_id)
        return {"status": "success", "message": "Your history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")