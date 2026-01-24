import sqlite3
import pandas as pd
import os
from datetime import datetime
import numpy as np

# Use a data folder that will be mapped to Docker Volume
DB_PATH = os.path.join("data", "news_database.db")

def ensure_db_exists():
    "Create database and table if they don't exist"
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_history (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            input_type TEXT,
            url TEXT,
            title TEXT,
            text TEXT,
            label TEXT,
            confidence REAL,
            explanation TEXT,
            reviewer_feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

def append_record(record: dict):
    "Save record to SQLite"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    # Convert dict to DataFrame for easy SQL insertion
    df = pd.DataFrame([record])
    df.to_sql("news_history", conn, if_exists="append", index=False)
    conn.close()

def read_history(limit: int = 50):
    "Read history for Streamlit"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM news_history ORDER BY timestamp DESC LIMIT {limit}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def update_record_feedback(record_id: str, feedback_text: str):
    "Update feedback column"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE news_history SET reviewer_feedback = ? WHERE id = ?", (feedback_text, record_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def check_cache(news_text: str):
    "Normalize text and check if it exists in the database"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    # Strip whitespaces and newlines for a more robust match
    cleaned_text = news_text.strip()
    query = "SELECT id, label, confidence, explanation FROM news_history WHERE TRIM(text) = ? LIMIT 1"
    df = pd.read_sql(query, conn, params=(cleaned_text,))
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else None

def get_stats_data():
    'Calculate metrics for both Fake and Real news'
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT label FROM news_history", conn)
        total = len(df)
        if total == 0:
            return {"total": 0, "fake_percent": 0, "real_percent": 0}
        
        # Standardizing label names for calculation
        fake_count = len(df[df['label'].str.lower().str.contains('fake', na=False)])
        real_count = len(df[df['label'].str.lower().str.contains('real', na=False)])
        
        fake_p = round((fake_count / total) * 100, 1)
        real_p = round((real_count / total) * 100, 1)
        
        return {"total": total, "fake_percent": fake_p, "real_percent": real_p}
    finally:
        conn.close()

def clear_all_history():
    "Danger: This will delete all records from the database"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM news_history")
    conn.commit()
    conn.close()