from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import os
import sqlite3
import requests
import time
import logging
import uvicorn
import asyncio

app = FastAPI()

@app.get("/.well-known/{filename}")
async def get_well_known_file(filename: str):
    file_path = os.path.join(".well-known", filename)
    if os.path.isfile(file_path):
        return FileResponse(path=file_path, filename=filename)
    return {"detail": "Not Found"}

@app.get("/")
def root():
    return {"status": "DAN-XBOX API com todas integracoes ativas"}
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

# === Playwright Automação ===
@app.post("/automation/playwright")
def playwright_automation(url: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
        return {"status": "ok", "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro Playwright: {e}")

# === Selenium Automação ===
@app.post("/automation/selenium")
def selenium_automation(url: str):
    try:
        options = Options()
        options.add_argument("--headless")
        service = Service("/usr/bin/chromedriver")  # Atualize se necessário
        driver = webdriver.Chrome(service=service, options=options)
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
            yield f"event: msg\ndata: Evento {i+1}\n\n"
            time.sleep(1)
        yield "event: fim\ndata: Fim da transmissão\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream")

@app.post("/zapier/trigger")
def trigger_zapier(data: dict):
    if not ZAPIER_MCP_ENABLED:
        raise HTTPException(status_code=503, detail="Zapier MCP desativado.")
    r = requests.post("https://actions.zapier.com/mcp/YOUR_ENDPOINT", json=data)
    return {"status": "enviado", "response": r.text}

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
def get_google_spec():
    return FileResponse("google-drive/google-drive-api.yaml")

@app.get("/discord/discord-api.yaml")
def get_discord_spec():
    return FileResponse("discord/discord-api.yaml")

@app.get("/health")
def health_check(): return {"status": "ok"}

# === Start server ===
if __name__ == "__main__":
    port = int(os.getenv("PORT", 7000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
