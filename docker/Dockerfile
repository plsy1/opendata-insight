FROM node:22 AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend .
RUN npx ng build --configuration production

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/app/runtime

WORKDIR /app

# Install system dependencies, nginx, and supervisor in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install Playwright dependencies (optional but recommended for stability)
# If you want a strictly minimal image, you can remove this and run install-deps in start.sh
RUN playwright install-deps chromium && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Copy frontend build
COPY --from=frontend /app/frontend/dist/frontend/browser /app/frontend

# Copy application code
COPY backend /app/backend
COPY VERSION /app/VERSION
COPY docker/start.sh /app/start.sh
COPY docker/supervisord.conf /app/supervisord.conf
COPY docker/nginx.conf /etc/nginx/nginx.conf

RUN chmod +x /app/start.sh

EXPOSE 80
ENTRYPOINT ["bash", "/app/start.sh"]