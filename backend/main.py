from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.scraping import scrape_article
from backend.storage import append_record, clear_all_history, update_record_feedback, read_history, check_cache, get_stats_data
from backend.llm_judge import judge_news
from dotenv import load_dotenv
import json
import uuid
import datetime
import os
import pandas as pd

load_dotenv()

app = FastAPI()

class PredictRequest(BaseModel):
    text: str

class ScrapeRequest(BaseModel):
    url: str
    
class FeedbackRequest(BaseModel):
    id: str
    feedback: str   

# DASHBOARD ENDPOINT 
@app.get("/stats")
def get_stats():
    return get_stats_data() 


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Misinformation Detector!"}

@app.post("/scrape")
def scrape(req: ScrapeRequest):
    try:
        return scrape_article(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scraping failed: {str(e)}")


@app.post("/predict")
def predict(req: PredictRequest):
    try:
        # CHECK CACHE FIRST
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
            "reviewer_feedback": "" 
        }
        append_record(record)
        return {"id": record_id, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze_url")
def analyze_url(req: ScrapeRequest):
    try:
        # 1. First, scrape the article content
        article = scrape_article(req.url)
        
        # 2. CHECK CACHE with the scraped text before running the model
        cached = check_cache(article["text"])
        if cached:
            return {**cached, "source": "database"} # Returns instantly if found

        # 3. If not in cache, run the AI judge
        result = judge_news(article["text"]) 
        
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
            "reviewer_feedback": ""
        }
        append_record(record)
        return {"id": record_id, **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/history")
def history(limit: int = 50):
    try:
        from backend.storage import read_history
        df = read_history(limit)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class FinalRecordRequest(BaseModel):
    text: str
    label: str
    confidence: float
    explanation: str
    reviewer_feedback: str
    input_type: str = "text"
    url: str = ""
    title: str = "N/A"

@app.post("/save_with_feedback")
def save_with_feedback(req: FinalRecordRequest):
    try:
        record = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input_type": req.input_type,
            "url": req.url,
            "title": req.title,
            "text": req.text,
            "label": req.label,
            "confidence": req.confidence,
            "explanation": req.explanation,
            "reviewer_feedback": req.reviewer_feedback
        }
        append_record(record)
        return {"status": "success"} 
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
def clear_history():
    try:
        clear_all_history()
        return {"status": "success", "message": "All history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))