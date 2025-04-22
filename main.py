from fastapi import FastAPI, Request, HTTPException, Query, Path
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import requests
import time
import logging
import uvicorn

from playwright.async_api import async_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Discord opcional
try:
    try:
        try:
            from discord_bot import start_discord_bot
        except ImportError:
            logging.warning("discord_bot module not found. Discord bot functionality will be disabled.")
            start_discord_bot = lambda: None
    except ImportError:
        logging.warning("discord_bot module not found. Discord bot functionality will be disabled.")
        start_discord_bot = lambda: None
except ImportError:
    start_discord_bot = lambda: None

# === Configuração ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "memory.db"
logging.basicConfig(level=logging.INFO)

GOOGLE_API_BASE = "https://www.googleapis.com/drive/v3"
GITHUB_API_BASE = "https://api.github.com"
AZURE_API_BASE = "https://dev.azure.com"

GOOGLE_API_TOKEN = os.getenv("GOOGLE_DRIVE_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
AZURE_DEVOPS_TOKEN = os.getenv("AZURE_DEVOPS_TOKEN")
ZAPIER_MCP_ENABLED = os.getenv("ZAPIER_MCP_ENABLED", "true").lower() == "true"
ZAPIER_SECRET = os.getenv("ZAPIER_SECRET", "zapier123")
ZAPIER_ACTION_URL = "https://server-apig-gpt-1.onrender.com/zapier/trigger"
ZAPIER_TRIGGER_WEBHOOK = "https://server-apig-gpt-1.onrender.com/zapier/webhook-trigger"

# === Banco local de memória ===
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()
    start_discord_bot()

@app.get("/")
def root():
    return {"status": "✅ DAN-XBOX API com todas integrações ativas"}

@app.get("/.well-known/api-config")
def api_config():
    return {
        "zapier_trigger": ZAPIER_TRIGGER_WEBHOOK,
        "zapier_action": ZAPIER_ACTION_URL,
        "github_spec": "/github/github-api.yaml",
        "drive_spec": "/google-drive/google-drive-api.yaml",
        "plugin_version": "1.0.0"
    }

@app.post("/v1/completions")
async def completions(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="Campo 'prompt' é obrigatório.")
    response = f"[DAN-XBOX] Simulação de resposta para: {prompt}"
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO memory (prompt, response) VALUES (?, ?)", (prompt, response))
        conn.commit()
    return {"response": response}

@app.get("/memory/export")
def export_memory():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT * FROM memory ORDER BY id DESC").fetchall()
    return {"logs": [{"id": r[0], "prompt": r[1], "response": r[2], "timestamp": r[3]} for r in rows]}

# === Google Drive ===
@app.get("/drive/list")
def list_drive_files(page_size: int = 10):
    headers = {"Authorization": f"Bearer {GOOGLE_API_TOKEN}"}
    params = {"pageSize": page_size, "fields": "files(id,name,mimeType)"}
    r = requests.get(f"{GOOGLE_API_BASE}/files", headers=headers, params=params)
    return r.json()

@app.get("/drive/file/{file_id}")
def get_file_metadata(file_id: str):
    headers = {"Authorization": f"Bearer {GOOGLE_API_TOKEN}"}
    r = requests.get(f"{GOOGLE_API_BASE}/files/{file_id}", headers=headers, params={"fields": "id,name,mimeType"})
    return r.json()

@app.get("/drive/file/{file_id}/download")
def download_file(file_id: str):
    headers = {"Authorization": f"Bearer {GOOGLE_API_TOKEN}"}
    r = requests.get(f"{GOOGLE_API_BASE}/files/{file_id}?alt=media", headers=headers, stream=True)
    return StreamingResponse(r.raw, media_type="application/octet-stream")

@app.delete("/drive/file/{file_id}/delete")
def delete_file(file_id: str):
    headers = {"Authorization": f"Bearer {GOOGLE_API_TOKEN}"}
    r = requests.delete(f"{GOOGLE_API_BASE}/files/{file_id}", headers=headers)
    return {"status": "Arquivo deletado", "code": r.status_code}

# === GitHub ===
@app.get("/github/repos")
def list_github_repos():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    r = requests.get(f"{GITHUB_API_BASE}/user/repos", headers=headers)
    return r.json()

@app.post("/github/repos/{owner}/{repo}/issues")
def create_issue(owner: str, repo: str, title: str = "Título padrão", body: str = "Criado via FastAPI"):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    payload = {"title": title, "body": body}
    r = requests.post(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues", headers=headers, json=payload)
    return r.json()

# === Azure DevOps ===
@app.get("/azure/repos/{organization}/{project}")
def list_azure_repos(organization: str, project: str):
    headers = {"Authorization": f"Basic {AZURE_DEVOPS_TOKEN}"}
    url = f"{AZURE_API_BASE}/{organization}/{project}/_apis/git/repositories?api-version=7.0"
    r = requests.get(url, headers=headers)
    return r.json()

@app.get("/azure/builds/{organization}/{project}")
def list_azure_builds(organization: str, project: str):
    headers = {"Authorization": f"Basic {AZURE_DEVOPS_TOKEN}"}
    url = f"{AZURE_API_BASE}/{organization}/{project}/_apis/build/builds?api-version=7.0"
    r = requests.get(url, headers=headers)
    return r.json()

# === Automação Playwright ===
@app.post("/automation/playwright")
async def playwright_automation(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Campo 'url' é obrigatório.")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            content = await page.content()
            await browser.close()
        return {"status": "ok", "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro Playwright: {e}")

# === Automação Selenium ===
@app.post("/automation/selenium")
async def selenium_automation(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Campo 'url' é obrigatório.")
    try:
        import chromedriver_autoinstaller
        chromedriver_autoinstaller.install()

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        content = driver.page_source
        driver.quit()
        return {"status": "ok", "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro Selenium: {e}")

# === Zapier Mock SSE + Trigger ===
@app.get("/mcp/sse")
def zapier_sse():
    def stream():
        yield "retry: 5000\n"
        yield "event: ping\n"
        yield "data: 🧠 Conexão com Zapier\n\n"
        for i in range(3):
            yield f"event: msg\ndata: Evento {i+1} enviado\n\n"
            time.sleep(1)
        yield "event: fim\ndata: Fim da transmissão\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
    }
    return StreamingResponse(stream(), headers=headers)

@app.post("/zapier/trigger")
def trigger_zapier(data: dict):
    if not ZAPIER_MCP_ENABLED:
        raise HTTPException(status_code=503, detail="Zapier MCP desativado.")

    if not data:
        raise HTTPException(status_code=400, detail="Dados ausentes na requisição.")

    try:
        r = requests.post(ZAPIER_ACTION_URL, json=data, timeout=10)
        r.raise_for_status()
        return {"status": "enviado", "code": r.status_code, "zapier_response": r.text}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao enviar para Zapier: {e}")

@app.post("/zapier/webhook-trigger")
async def zapier_webhook_trigger(request: Request):
    headers = request.headers
    token = headers.get("X-Zapier-Token")

    if token != ZAPIER_SECRET:
        raise HTTPException(status_code=403, detail="Token inválido")

    payload = await request.json()
    logging.info(f"[ZAPIER] Trigger recebido: {payload}")

    return JSONResponse(
        content=[
            {
                "id": str(int(time.time())),
                "mensagem": "Novo evento do DAN recebido 🔥",
                "dados": payload
            }
        ]
    )

# === Arquivos plugin ===
@app.get("/github/github-api.yaml")
def github_yaml(): return FileResponse("github/github-api.yaml")

@app.get("/github/github-ai-plugin.json")
def github_json(): return FileResponse("github/github-ai-plugin.json")

@app.get("/azure-devops/azure-devops-api.yaml")
def azure_yaml(): return FileResponse("azure-devops/azure-devops-api.yaml")

@app.get("/azure-devops/azure-ai-plugin.json")
def azure_json(): return FileResponse("azure-devops/azure-ai-plugin.json")

@app.get("/google-drive/google-drive-api.yaml")
def get_google_spec(): return FileResponse("google-drive/google-drive-api.yaml")

@app.get("/discord/discord-api.yaml")
def get_discord_spec(): return FileResponse("discord/discord-api.yaml")

@app.get("/health")
def health_check(): return {"status": "ok"}

# === Start server ===
if __name__ == "__main__":
    port = int(os.getenv("PORT", 7000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
