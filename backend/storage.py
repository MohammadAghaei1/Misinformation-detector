import os
import pandas as pd
from datetime import datetime
import numpy as np

DATA_PATH = os.path.join("data", "news.xlsx")

def ensure_file_exists():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=[
            "id", "timestamp", "input_type", "url", "title", "text",
            "label", "confidence", "explanation", "reviewer_feedback"
        ])
        df.to_excel(DATA_PATH, index=False, engine='openpyxl')


def append_record(record: dict):
    ensure_file_exists()
    df = pd.read_excel(DATA_PATH, engine='openpyxl')

    
    record = {key: (value if not isinstance(value, float) or not np.isnan(value) else None) 
              for key, value in record.items()}

    record = {
        "id": len(df) + 1,
        "timestamp": datetime.now().isoformat(timespec="seconds"),  
        **record
    }
    
    columns = [
        "id", "timestamp", "input_type", "url", "title", "text", 
        "label", "confidence", "explanation", "reviewer_feedback"
    ]
    
    record_data = pd.DataFrame([record], columns=columns)

    df = pd.concat([df, record_data], ignore_index=True)
    try:
        df.to_excel(DATA_PATH, index=False, engine='openpyxl')
        print("Data saved to Excel successfully.")  # Log success
    except Exception as e:
        print(f"Error saving to Excel: {e}")  # Log error


def read_history(limit: int = 50):
    ensure_file_exists()
    try:
        df = pd.read_excel(DATA_PATH, engine='openpyxl')

        print(f"Read {len(df)} rows from Excel.")

        df = df.applymap(lambda x: None if isinstance(x, float) and np.isnan(x) else x)
        return df.tail(limit)  
    except Exception as e:
        print(f"Error reading history from Excel: {str(e)}") 
        raise e

