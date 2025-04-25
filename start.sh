#!/bin/bash

echo "🚀 Iniciando DAN-XBOX Server no Render..."

# 🧠 Diretório de cache Playwright já existe no SSD (/mnt/data/ms-playwright)
# Não precisa mais criar ou linkar

# 🧠 Exporta o path explicitamente (opcional)
export PLAYWRIGHT_BROWSERS_PATH=/mnt/data/ms-playwright

# 🚀 Starta servidor FastAPI
uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
