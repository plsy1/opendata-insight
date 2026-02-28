#!/bin/bash
set -e

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
QB_KEYWORD_FILTER: "${QB_KEYWORD_FILTER:-}"
TELEGRAM_TOKEN: "${TELEGRAM_TOKEN:-}"
TELEGRAM_CHAT_ID: "${TELEGRAM_CHAT_ID:-}"
EMBY_URL: "${EMBY_URL:-}"
EMBY_API_KEY: "${EMBY_API_KEY:-}"
EOL
else
    echo "$CONFIG_FILE already exists. Skipping generation."
fi

if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ] || [ -z "$(ls -A $PLAYWRIGHT_BROWSERS_PATH)" ]; then
    echo "Installing Playwright browsers..."
    # Dependencies are already in the image, so we just need the binary
    playwright install chromium
    echo "Playwright browsers installed."
fi

exec /usr/bin/supervisord -c /app/supervisord.conf