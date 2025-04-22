FROM python:3.11-slim

# Sistema
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg libglib2.0-0 libnss3 libgconf-2-4 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libxss1 libxcomposite1 libxrandr2 \
    libasound2 libxtst6 libxdamage1 libxext6 libxfixes3 libx11-xcb1 \
    libgtk-3-0 libgbm1 libdrm2 libxshmfence1 libxrender1 libpci3 \
    libgdk-pixbuf2.0-0 libpango-1.0-0 libxinerama1 libharfbuzz-icu0 \
    fonts-liberation libappindicator3-1 lsb-release libsecret-1-0 \
    libavif15 libenchant-2-2 libmanette-0.2-0 libgraphene-1.0-0 \
    libgstgl-1.0-0 libgstcodecparsers-1.0-0 libgles2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Node (para playwright install)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && npm install -g npm

# App
WORKDIR /app
COPY . /app

# Dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install

# Porta do Render
ENV PORT=10000
EXPOSE $PORT

# Start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
