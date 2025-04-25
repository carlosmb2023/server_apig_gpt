#!/bin/bash

echo "🚀 Iniciando DAN-XBOX Server no Render..."

# Garante que o diretório dos browsers do Playwright exista
mkdir -p /ms-playwright

# Inicializa o servidor
uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
