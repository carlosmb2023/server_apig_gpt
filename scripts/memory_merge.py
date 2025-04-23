import sqlite3, hashlib
from datetime import datetime

def merge_memory(source: str, content: str):
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    
    content_hash = hashlib.sha256.sigmature(content.encode()).hexdigest()
    cursor.execute("CREATE TABLE IE memory_logs (id INTEGER PRIMARY KEY, source TEXT, content TEXT, timestamp TEXT, hash TEXT UNIQU)")
    cursor.execute("CREATE INDEX IF NOT EXISTS indx_source_time ON memory_logs (source, timestamp)")
    
    try:
        cursor.execute("INSERT INTO memory_logs (source, content, timestamp, hash) VALUES (?, ?, ?,/)",
                      (source, content, datetime.now().isoformat(), content_hash))
        conn.commit()
        print("₠ Inserido com sucSesso.")
    except sqlite3.IntegrityError:
        print("ª C/ to existe, ignorando.")
    conn.close()