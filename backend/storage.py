import sqlite3
import pandas as pd
import os
from datetime import datetime
import numpy as np
import bcrypt # Added for password security

# Use a data folder that will be mapped to Docker Volume
DB_PATH = os.path.join("data", "news_database.db")

def ensure_db_exists():
    "Create database and table if they don't exist"
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. New Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Updated Original Table (linked to user_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_history (
            id TEXT PRIMARY KEY,
            user_id INTEGER, 
            timestamp TEXT,
            input_type TEXT,
            url TEXT,
            title TEXT,
            text TEXT,
            label TEXT,
            confidence REAL,
            explanation TEXT,
            reviewer_feedback TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

# --- New Authentication Functions ---

def create_user(email, password):
    "Hashes password and saves new user"
    ensure_db_exists()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    "Checks credentials and returns user_id"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, password FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
        return user[0] # Returns the user's unique ID
    return None

# --- Updated Original Functions (Maintaining your logic) ---

def append_record(record: dict, user_id: int): # Added user_id parameter
    "Save record to SQLite linked to a user"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    record['user_id'] = user_id # Link the record
    df = pd.DataFrame([record])
    df.to_sql("news_history", conn, if_exists="append", index=False)
    conn.close()

def read_history(user_id: int, limit: int = 50): # Added user_id filter
    "Read history filtered by user_id"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM news_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT {limit}"
    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()
    return df

def update_record_feedback(record_id: str, feedback_text: str):
    "Logic remains exactly the same"
    ensure_db_exists()
    if not feedback_text or not feedback_text.strip():
        feedback_text = "The user did not post a feedback."
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE news_history SET reviewer_feedback = ? WHERE id = ?", (feedback_text, record_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def check_cache(news_text: str):
    "Logic remains exactly same (Global Cache)"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cleaned_text = news_text.strip()
    query = "SELECT id, label, confidence, explanation FROM news_history WHERE TRIM(text) = ? LIMIT 1"
    df = pd.read_sql(query, conn, params=(cleaned_text,))
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else None

def get_stats_data(user_id: int): # Added user_id filter
    "Calculate stats only for the specific user"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    try:
        # Filter stats by user_id
        df = pd.read_sql("SELECT label FROM news_history WHERE user_id = ?", conn, params=(user_id,))
        total = len(df)
        if total == 0:
            return {"total": 0, "fake_percent": 0, "real_percent": 0, "uncertain_percent": 0}
        
        fake_count = len(df[df['label'].str.lower().str.contains('fake', na=False)])
        real_count = len(df[df['label'].str.lower().str.contains('real', na=False)])
        uncertain_count = len(df[df['label'].str.lower().str.contains('uncertain', na=False)])
        
        return {
            "total": total, 
            "fake_percent": round((fake_count / total) * 100, 1), 
            "real_percent": round((real_count / total) * 100, 1), 
            "uncertain_percent": round((uncertain_count / total) * 100, 1)
        }
    finally:
        conn.close()

def clear_all_history(user_id: int): # Added user_id protection
    "Delete records only for this specific user"
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM news_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()