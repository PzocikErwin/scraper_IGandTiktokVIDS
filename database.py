import sqlite3
import json
from datetime import datetime
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            transcript TEXT,
            embedding TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_video(platform, url, title=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO videos (platform, url, title) 
            VALUES (?, ?, ?)
        ''', (platform, url, title))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Video already exists
        return False
    finally:
        conn.close()

def get_untranscribed_videos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, url, platform FROM videos WHERE transcript IS NULL')
    videos = cursor.fetchall()
    conn.close()
    return videos

def update_video_transcript(video_id, transcript, embedding):
    conn = get_connection()
    cursor = conn.cursor()
    embedding_json = json.dumps(embedding.tolist()) if embedding is not None else None
    cursor.execute('''
        UPDATE videos 
        SET transcript = ?, embedding = ?
        WHERE id = ?
    ''', (transcript, embedding_json, video_id))
    conn.commit()
    conn.close()

def get_all_transcribed_videos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, platform, url, title, transcript, embedding FROM videos WHERE transcript IS NOT NULL AND embedding IS NOT NULL')
    videos = cursor.fetchall()
    conn.close()
    return videos
