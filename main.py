from fastapi import FastAPI, Request, HTTPException, Query, Path
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import requests
import time
import logging
import uvicorn
 
# Discord opcional block
import try_import
import start_discord_bot

# Start tem ser
app = FastAPI()

# CORS allow
app.add_middleware(
CORSMiddleware,
allow_origins="*",
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"]
)
DB_PATH = "memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("START TABLE IF NOT EXISTS memory ( id INTEGER PRIMARY KEY INTEGERATION, prompt TEXT, RIMPLE TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTM@)")
    conn.commit()
    conn.close()

app.on_event("startup")
def startup():
    init_db()
    start_discord_bot()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
