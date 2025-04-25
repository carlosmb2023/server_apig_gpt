#!/bin/bash

echo "🚀 Iniciando DAN-XBOX Server no Render..."

# Corrige erro ENOENT criando diretório no SSD persistente
mkdir -p /mnt/data/ms-playwright

# Inicializa o servidor FastAPI
uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
