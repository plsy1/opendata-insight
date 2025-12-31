#!/bin/bash
set -e


check_lib() {
    if ! ldconfig -p | grep -q "$1"; then
        return 1
    fi
    return 0
}

LIBS=(
    libatspi.so.0
    libgtk-3.so
    libx11.so.6
    libnss3.so
    libxcomposite.so.1
    libxdamage.so.1
    libxrandr.so.2
    libasound.so.2
    libgbm.so.1
    libpangocairo-1.0.so.0
    libglib-2.0.so.0
)

MISSING=0
for lib in "${LIBS[@]}"; do
    if ! check_lib "$lib"; then
        echo "Missing library: $lib"
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo "Installing Chromium dependencies..."
    apt-get update && apt-get install -y --no-install-recommends \
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
        libdatrie1 \
        && apt-get clean && rm -rf /var/lib/apt/lists/*
fi

CONFIG_FILE="/app/backend/data/config.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Generating $CONFIG_FILE from environment variables..."
    cat > "$CONFIG_FILE" <<EOL
PROWLARR_URL: "${PROWLARR_URL:-}"
PROWLARR_KEY: "${PROWLARR_KEY:-}"
DOWNLOAD_PATH: "${DOWNLOAD_PATH:-}"
QB_URL: "${QB_URL:-}"
QB_USERNAME: "${QB_USERNAME:-}"
QB_PASSWORD: "${QB_PASSWORD:-}"
QB_KEYWORD_FILTER: "${QB_KEYWORD_FILTER:-游戏大全,七龍珠}"
TELEGRAM_TOKEN: "${TELEGRAM_TOKEN:-}"
TELEGRAM_CHAT_ID: "${TELEGRAM_CHAT_ID:-}"
EMBY_URL: "${EMBY_URL:-}"
EMBY_API_KEY: "${EMBY_API_KEY:-}"
EOL
else
    echo "$CONFIG_FILE already exists. Skipping generation."
fi

if [ ! -d "/app/runtime" ] || [ -z "$(ls -A /app/runtime)" ]; then
    echo "Installing Playwright browsers..."
    playwright install-deps chromium
    playwright install chromium
    echo "Playwright browsers installed."
fi

exec /usr/bin/supervisord -c /app/supervisord.conf