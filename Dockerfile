FROM python:3.11-slim

# === Variáveis de ambiente ===
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT=7000

# === Diretório ===
WORKDIR /app

# === Dependências do sistema ===
RUN apt-get update && \
    apt-get install -y curl unzip wget gnupg chromium-driver && \
    rm -rf /var/lib/apt/lists/*

# === Instalar dependências ===
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps

# === Copiar app ===
COPY . .

# === Start ===
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]
