FROM python:3.11-slim

# Sistema base + libs pro Playwright + WebUI
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg git libglib2.0-0 libnss3 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libxss1 libxcomposite1 libxrandr2 \
    libasound2 libxtst6 libxdamage1 libxext6 libxfixes3 libx11-xcb1 \
    libgtk-3-0 libgbm1 libdrm2 libshm-fence1 libxrender1 libpci3 \
    libgdk-pixbuf2.0-0 libpangocairo-1.0-0 libharfbuzz-icu0 \
    fonts-liberation libappindicator3-1 lsb-release libsecret-1-0 \
    libavif15 libenchant-2-2 libmanette-0.2-0 libgraphene-1.0-0 \
    libgstgl-1.0-0 libgstcodecparsers-1.0-0 libgles2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Node.js pro WebUI e Playwright
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && npm install -g npm

# Diretório app
WORKDIR /app

# Copia tudo do projeto
COPY . /app

# Instala Python deps
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install

# Instala frontend (WebUI)
WORKDIR /app/web-ui
RUN npm install && npm run build

# Volta pra raiz
WORKDIR /app

# Define porta
ENV PORT=10000
EXPOSE $PORT

# Entrypoint: FastAPI + Watchdog
CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT & python watchdog.py"]


