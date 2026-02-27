FROM node:22 AS frontend
COPY frontend /app/frontend
WORKDIR /app/frontend
RUN npm install && npx ng build --configuration production

FROM python:3.11-slim

COPY --from=frontend /app/frontend/dist/frontend/browser /app/frontend

WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    fonts-liberation \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxi6 \
    libxrender1 \
    libxshmfence1 \
    libasound2 \
    libatspi2.0-0 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libx11-xcb1 \
    libxkbfile1 \
    libxcb1 \
    libxmu6 \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    fonts-noto-color-emoji \
    fontconfig \
    libfontconfig1 \
    libfreetype6 \
    libfribidi0 \
    libgraphite2-3 \
    libharfbuzz0b \
    libdatrie1

ENV PLAYWRIGHT_BROWSERS_PATH=/app/runtime

COPY backend /app/backend
COPY VERSION /app/VERSION

RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx supervisor && \
    apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/*

COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh
COPY docker/supervisord.conf /app/supervisord.conf
COPY docker/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
ENTRYPOINT ["bash", "/app/start.sh"]