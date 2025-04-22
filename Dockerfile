# Use uma imagem base com suporte a Playwright
FROM mcr.microsoft.com/playwright/python:v1.39.0-focal

# Instale dependências adicionais
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg libglib2.0-0 libnss3 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libxss1 libxcomposite1 libxrandr2 \
    libasound2 libxtst6 libxdamage1 libxext6 libxfixes3 libx11-xcb1 \
    libgtk-3-0 libgbm1 libdrm2 libshm-fence1 libxrender1 libpci3 \
    libgdk-pixbuf2.0-0 libpangocairo-1.0-0 libharfbuzz-icu0 \
    fonts-liberation libappindicator3-1 lsb-release libsecret-1-0 \
    libavif15 libenchant-2-2 libmanette-0.2-0 libgraphene-1.0-0 \
    libgstgl-1.0-0 libgstcodecparsers-1.0-0 libgles2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instale Node.js (necessário para o frontend)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && npm install -g npm

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos do backend
COPY . /app

# Instale as dependências do Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install

# Configure o frontend
WORKDIR /app/web-ui
RUN npm install && npm run build

# Volte para o diretório do backend
WORKDIR /app

# Defina a porta da API
ENV PORT=10000
EXPOSE $PORT

# Comando de inicialização
CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT & python watchdog.py"]



