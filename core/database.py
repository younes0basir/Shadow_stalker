import sqlite3
import os

DB_PATH = "game_data.db"

def init_db():
    """Initialize the database and tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL
    )
    ''')
    
    # High scores table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS high_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        level_id TEXT,
        score INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, level_id)
    )
    ''')

    # Total scores table for leaderboard
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS total_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        total_score INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def get_or_create_user(username):
    """Get user ID or create new user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
    else:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        user_id = cursor.lastrowid
        
    conn.close()
    return user_id

def update_high_score(user_id, level_id, score):
    """Update high score if the new score is higher."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT score FROM high_scores WHERE user_id = ? AND level_id = ?", (user_id, level_id))
    row = cursor.fetchone()
    
    if row:
        if score > row[0]:
            cursor.execute("UPDATE high_scores SET score = ? WHERE user_id = ? AND level_id = ?", (score, user_id, level_id))
    else:
        cursor.execute("INSERT INTO high_scores (user_id, level_id, score) VALUES (?, ?, ?)", (user_id, level_id, score))
        
    conn.commit()
    conn.close()

def get_high_scores(user_id):
    """Get all high scores for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT level_id, score FROM high_scores WHERE user_id = ?", (user_id,))
    scores = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    return scores

def update_total_score(user_id, total_score):
    """Update total score for a user if the new run is higher."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT total_score FROM total_scores WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row:
        if total_score > row[0]:
            cursor.execute("UPDATE total_scores SET total_score = ? WHERE user_id = ?", (total_score, user_id))
    else:
        cursor.execute("INSERT INTO total_scores (user_id, total_score) VALUES (?, ?)", (user_id, total_score))
        
    conn.commit()
    conn.close()

def get_top_total_scores(limit=10):
    """Get overall top total scores across all users."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT users.username, total_scores.total_score 
    FROM total_scores 
    JOIN users ON total_scores.user_id = users.id 
    ORDER BY total_scores.total_score DESC 
    LIMIT ?
    ''', (limit,))
    
    top_scores = cursor.fetchall()
    conn.close()
    return top_scores
