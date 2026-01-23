from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.scraping import scrape_article
from backend.storage import append_record, read_history, update_record_feedback
from backend.llm_judge import judge_news
from dotenv import load_dotenv
load_dotenv()
import json
import uuid
import datetime


app = FastAPI()

class PredictRequest(BaseModel):
    text: str

class ScrapeRequest(BaseModel):
    url: str


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


'''@app.post("/predict")
def predict(req: PredictRequest):
    try:
        result = judge_news(req.text)
        
        print(f"Model response: {result}")  
        
        label = result.get("label", "uncertain")
        confidence = result.get("confidence", 0)
        explanation = result.get("explanation", "No explanation provided")
        
        record = {
            "input_type": "text",  
            "url": "",  
            "title": "N/A", 
            "text": req.text,
            "label": label,  
            "confidence": confidence,  
            "explanation": explanation,  
            "reviewer_feedback": "" 
        }

        append_record(record)  

        return {
            "label": label,
            "confidence": confidence,
            "explanation": explanation
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''
    

@app.post("/predict")
def predict(req: PredictRequest):
    try:
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
        
        return {
            "id": record_id,
            "label": result.get("label"),
            "confidence": result.get("confidence"),
            "explanation": result.get("explanation")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_url")
def analyze_url(req: ScrapeRequest):
    """
    URL -> scrape -> predict -> store in Excel -> return result
    """
    try:
        article = scrape_article(req.url)
        print(f"Extracted Text from URL: {article['text'][:500]}...")  

        result = judge_news(article["text"]) 
        
        record = {
            "input_type": "url",
            "url": article["url"],
            "title": article["title"],
            "text": article["text"],
            "label": result['label'],
            "confidence": result['confidence'],
            "explanation": result['explanation'],
            "reviewer_feedback": ""
        }
        append_record(record)  

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analyze URL failed: {str(e)}")


@app.get("/history")
def history(limit: int = 50):
    try:
        df = read_history(limit=limit)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No records found in history.")
        
        print(f"Loaded {len(df)} records from Excel.")
        
        return df.to_dict(orient="records")
    
    except Exception as e:
        print(f"Error loading history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

import datetime
import uuid

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
def update_feedback(data: dict):
    from backend.storage import update_record_feedback
    
    record_id = data.get("id")
    feedback = data.get("feedback")
    
    success = update_record_feedback(record_id, feedback)
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Record not found")