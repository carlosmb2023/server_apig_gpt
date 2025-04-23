FROM mcr.microsoft.com/playwright/python:v1.39.0-focal

# ==== Dependências de sistema ====
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg xvfb x11vnc x11-utils xauth dbus \
    supervisor netcat-traditional net-tools procps git \
    libgconf-2-4 libnss3 libnspr4 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libxss1 libx11-xcb1 libxext6 libxtst6 \
    libpci3 libxrender1 libgdk-pixbuf2.0-0 libpangocairo-1.0-0 \
    libharfbuzz-icu0 libsecret-1-0 libenchant-2-2 libmanette-0.2-0 \
    libgraphene-1.0-0 libgles2 fonts-liberation fonts-dejavu-core \
    fonts-dejavu-extra fontconfig && \
    rm -rf /var/lib/apt/lists/*

# ==== Node.js (caso precise rodar algum script JS) ====
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && npm install -g npm

# ==== noVNC ====
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc && \
    git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify && \
    ln -s /opt/novnc/vnc.html /opt/novnc/index.html

# ==== Diretório da aplicação ====
WORKDIR /app
COPY . /app

# ==== Instala Rust (necessário para alguns pacotes Python) ====
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    . "$HOME/.cargo/env"

# ==== Instala dependências Python ====
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install --with-deps chromium

# ==== Config supervisor ====
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# ==== Variáveis de ambiente ====
ENV PYTHONUNBUFFERED=1 \
    BROWSER_USE_LOGGING_LEVEL=info \
    CHROME_PATH=/ms-playwright/chromium-*/chrome-linux/chrome \
    ANONYMIZED_TELEMETRY=false \
    DISPLAY=:99 \
    RESOLUTION=1920x1080x24 \
    VNC_PASSWORD=vncpassword \
    CHROME_PERSISTENT_SESSION=true \
    RESOLUTION_WIDTH=1920 \
    RESOLUTION_HEIGHT=1080 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PORT=10000

# ==== Portas expostas ====
EXPOSE 10000 7788 6080 5901

# ==== Start ====
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
