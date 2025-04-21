from fastapi import FastAPI, Request, HTTPException, Query, Path
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from flask import send_from_directory
import sqlite3
import os
import requests
import time
import logging
import uvicorn
import asyncio

from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# === Configuração ===
app = FastAPI()

# === Rota do plugin .route fallback para servir pasta .well-known ===
@fastapi.get("/.well-known/<path:filename>")
def well_known(filename):
    return send_from_directory('..well-known', filename)

# existing routes entramadas seguem ... ...