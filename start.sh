#!/bin/bash

echo "Iniciando DAN-XBOX Server 🚀"
uvicorn main:app --host 0.0.0.0 --port $PORT
