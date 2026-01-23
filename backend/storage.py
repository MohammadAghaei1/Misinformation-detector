import os
import pandas as pd
from datetime import datetime
import numpy as np

DATA_PATH = os.path.join("data", "news.xlsx")

'''def ensure_file_exists():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=[
            "id", "timestamp", "input_type", "url", "title", "text",
            "label", "confidence", "explanation", "reviewer_feedback"
        ])
        df.to_excel(DATA_PATH, index=False, engine='openpyxl')'''

def ensure_file_exists():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        columns = [
            "id", "timestamp", "input_type", "url", "title", "text", 
            "label", "confidence", "explanation", "reviewer_feedback"
        ]
        df = pd.DataFrame(columns=columns)
        df.to_excel(DATA_PATH, index=False, engine='openpyxl')


'''def append_record(record: dict):
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
        print(f"Error saving to Excel: {e}")  # Log error'''

def append_record(record: dict):
    ensure_file_exists()
    df_existing = pd.read_excel(DATA_PATH, engine='openpyxl')

    record = {key: (value if not isinstance(value, float) or not np.isnan(value) else None) 
              for key, value in record.items()}

    if "id" not in record or record["id"] is None:
        record["id"] = str(len(df_existing) + 1)
    
    if "timestamp" not in record:
        record["timestamp"] = datetime.now().isoformat(timespec="seconds")

    columns = [
        "id", "timestamp", "input_type", "url", "title", "text", 
        "label", "confidence", "explanation", "reviewer_feedback"
    ]
    
    record_data = pd.DataFrame([record], columns=columns)
    
    df_combined = pd.concat([record_data, df_existing], ignore_index=True)
    
    try:
        df_combined.to_excel(DATA_PATH, index=False, engine='openpyxl')
        print(f"Record {record['id']} added to the top.")
    except Exception as e:
        print(f"Error saving to Excel: {e}")


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

def update_record_feedback(record_id, feedback_text):
    ensure_file_exists()
    try:
        df = pd.read_excel(DATA_PATH, engine='openpyxl')
        df['id'] = df['id'].astype(str)
        
        target_id = str(record_id)
        
        if target_id in df['id'].values:
            df.loc[df['id'] == target_id, 'reviewer_feedback'] = feedback_text
            df.to_excel(DATA_PATH, index=False, engine='openpyxl')
            print(f"Feedback updated for ID: {target_id}")
            return True
        else:
            print(f"ID {target_id} not found in Excel.")
            return False
    except Exception as e:
        print(f"Error updating feedback: {e}")
        return False