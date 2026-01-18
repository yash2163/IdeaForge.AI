import sqlite3
import json
from datetime import datetime
from src.models import BusinessIdea

DB_NAME = "ideaforge.db"

def init_db():
    """Create tables if they don't exist"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table 1: Sessions (The Battle Event)
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche TEXT,
                    timestamp TEXT
                )''')
    
    # Table 2: Ideas (The Output)
    # We store the full object as a JSON string for flexibility
    c.execute('''CREATE TABLE IF NOT EXISTS ideas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    title TEXT,
                    overall_score REAL,
                    full_data JSON,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )''')
    
    conn.commit()
    conn.close()

def save_battle(niche: str, ideas: list[BusinessIdea]):
    """Save a finished battle and its ideas"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Create Session
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO sessions (niche, timestamp) VALUES (?, ?)", (niche, timestamp))
    session_id = c.lastrowid
    
    # 2. Save Each Idea
    for idea in ideas:
        # Convert Pydantic object to JSON string
        idea_json = idea.model_dump_json()
        c.execute('''INSERT INTO ideas (session_id, title, overall_score, full_data)
                     VALUES (?, ?, ?, ?)''', 
                     (session_id, idea.title, idea.score_overall, idea_json))
        
    conn.commit()
    conn.close()
    return session_id

def get_all_sessions():
    """Get list of past battles for the sidebar"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, niche, timestamp FROM sessions ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_session_ideas(session_id):
    """Retrieve all ideas for a specific battle"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT full_data FROM ideas WHERE session_id = ?", (session_id,))
    rows = c.fetchall()
    conn.close()
    
    # Convert JSON strings back to Pydantic objects
    restored_ideas = []
    for row in rows:
        data = json.loads(row[0])
        restored_ideas.append(BusinessIdea(**data))
        
    return restored_ideas