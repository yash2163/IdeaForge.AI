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
    # Added 'mode' column to track Spectator vs Gladiator
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche TEXT,
                    mode TEXT, 
                    timestamp TEXT
                )''')
    
    # Table 2: Ideas (The Output)
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

def save_battle(niche: str, ideas: list[BusinessIdea], mode: str = "Spectator"):
    """Save a finished battle with its specific mode"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if 'mode' column exists (Migration logic for existing DBs)
    try:
        c.execute("SELECT mode FROM sessions LIMIT 1")
    except sqlite3.OperationalError:
        # If column doesn't exist, add it
        c.execute("ALTER TABLE sessions ADD COLUMN mode TEXT")
    
    # 1. Create Session
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO sessions (niche, mode, timestamp) VALUES (?, ?, ?)", (niche, mode, timestamp))
    session_id = c.lastrowid
    
    # 2. Save Each Idea
    for idea in ideas:
        idea_json = idea.model_dump_json()
        c.execute('''INSERT INTO ideas (session_id, title, overall_score, full_data)
                     VALUES (?, ?, ?, ?)''', 
                     (session_id, idea.title, idea.score_overall, idea_json))
        
    conn.commit()
    conn.close()
    return session_id

def get_sessions_by_mode(mode_filter: str):
    """Get battles filtered by their mode"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Migration check (in case DB is old)
    try:
        c.execute("SELECT mode FROM sessions LIMIT 1")
    except sqlite3.OperationalError:
        return [] # Return empty if DB structure isn't updated yet

    c.execute("SELECT id, niche, timestamp FROM sessions WHERE mode = ? ORDER BY id DESC", (mode_filter,))
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
    
    restored_ideas = []
    for row in rows:
        data = json.loads(row[0])
        restored_ideas.append(BusinessIdea(**data))
        
    return restored_ideas