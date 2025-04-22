FROM mcr.microsoft.com/playwright/python:v1.39.0-focal

# ==== Instala dependências de sistema do WebUI ====
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg xvfb x11vnc tigervnc-tools xauth dbus \
    supervisor netcat-traditional net-tools procps git \
    libgconf-2-4 libnss3 libnspr4 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libxss1 libx11-xcb1 libxext6 libxtst6 \
    libpci3 libxrender1 libshm-fence1 libgdk-pixbuf2.0-0 libpangocairo-1.0-0 \
    libharfbuzz-icu0 libsecret-1-0 libavif15 libenchant-2-2 libmanette-0.2-0 \
    libgraphene-1.0-0 libgstgl-1.0-0 libgstcodecparsers-1.0-0 libgles2 \
    fonts-liberation fonts-dejavu-core fonts-dejavu-extra fontconfig \
    && rm -rf /var/lib/apt/lists/*

# ==== Instala Node.js (para o WebUI) ====
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && npm install -g npm

# ==== Instala noVNC ====
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify \
    && ln -s /opt/novnc/vnc.html /opt/novnc/index.html

# ==== Setup App ====
WORKDIR /app

# Copia tudo
COPY . /app

# ==== Instala dependências Python ====
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install --with-deps chromium

# ==== Build do frontend ====
WORKDIR /app/web-ui
RUN npm install && npm run build

# ==== Configuração supervisor ====
WORKDIR /app
RUN mkdir -p /var/log/supervisor
COPY web-ui/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# ==== Variáveis de ambiente ====
ENV PYTHONUNBUFFERED=1
ENV BROWSER_USE_LOGGING_LEVEL=info
ENV CHROME_PATH=/ms-playwright/chromium-*/chrome-linux/chrome
ENV ANONYMIZED_TELEMETRY=false
ENV DISPLAY=:99
ENV RESOLUTION=1920x1080x24
ENV VNC_PASSWORD=vncpassword
ENV CHROME_PERSISTENT_SESSION=true
ENV RESOLUTION_WIDTH=1920
ENV RESOLUTION_HEIGHT=1080
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PORT=10000

# ==== Portas ====
EXPOSE 10000 7788 6080 5901

# ==== Start ====
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
