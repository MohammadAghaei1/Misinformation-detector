import os
import pandas as pd
from datetime import datetime
import numpy as np

DATA_PATH = os.path.join("data", "news.xlsx")

def ensure_file_exists():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        columns = [
            "id", "timestamp", "input_type", "url", "title", "text", 
            "label", "confidence", "explanation", "reviewer_feedback"
        ]
        df = pd.DataFrame(columns=columns)
        df.to_excel(DATA_PATH, index=False, engine='openpyxl')


def append_record(record: dict):
    ensure_file_exists()
    df_existing = pd.read_excel(DATA_PATH, engine='openpyxl')

    record = {key: (value if not isinstance(value, float) or not np.isnan(value) else None) 
              for key, value in record.items()}

    if "id" not in record or record["id"] is None:
        record["id"] = len(df_existing) + 1
    
    if "timestamp" not in record:
        record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    columns = [
        "id", "timestamp", "input_type", "url", "title", "text", 
        "label", "confidence", "explanation", "reviewer_feedback"
    ]
    
    df_new = pd.DataFrame([record], columns=columns)
    
    # New record goes to the bottom
    df_final = pd.concat([df_existing, df_new], ignore_index=True)
    
    try:
        df_final.to_excel(DATA_PATH, index=False, engine='openpyxl')
    except Exception as e:
        print(f"Error: {e}")

def read_history(limit: int = 50):
    ensure_file_exists()
    try:
        df = pd.read_excel(DATA_PATH, engine='openpyxl')
        
        df = df.where(pd.notnull(df), None)

        return df.tail(limit) 
    except Exception as e:
        raise e

def update_record_feedback(record_id, feedback_text):
    ensure_file_exists()
    try:
        df = pd.read_excel(DATA_PATH, engine='openpyxl')
        df['id'] = df['id'].astype(str)
        
        target_id = str(record_id)
        
        if target_id in df['id'].values:
            df.loc[df['id'] == target_id, 'reviewer_feedback'] = feedback_text
            df.to_excel(DATA_PATH, index=False, engine='openpyxl')
            return True
        return False
    except Exception as e:
        return False