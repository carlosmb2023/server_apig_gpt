#!/bin/bash

echo "🚀 Iniciando DAN-XBOX Server no Render..."
uvicorn main:app --host 0.0.0.0 --port $PORT
