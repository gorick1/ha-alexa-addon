#!/bin/bash
set -e

# Get options from HA add-on configuration
CONFIG_PATH=/data/options.json

# Extract credentials from config (with fallback)
if [ -f "$CONFIG_PATH" ]; then
  API_USERNAME=$(jq -r '.api_username // "musicassistant"' "$CONFIG_PATH" 2>/dev/null || echo "musicassistant")
  API_PASSWORD=$(jq -r '.api_password // ""' "$CONFIG_PATH" 2>/dev/null || echo "")
else
  API_USERNAME="musicassistant"
  API_PASSWORD=""
fi

# Set environment variables from config or defaults
export SKILL_HOSTNAME="${SKILL_HOSTNAME:-home.garrettorick.com}"
export MA_HOSTNAME="${MA_HOSTNAME:-127.0.0.1:8097}"
export PORT="${PORT:-5000}"
export DEBUG_PORT="${DEBUG_PORT:-0}"
export LOCALE="${LOCALE:-en-US}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
export TZ="${TZ:-America/Chicago}"
export QUIET_HTTP="${QUIET_HTTP:-1}"

# Export basic auth credentials if provided
if [ -n "$API_USERNAME" ]; then
  export APP_USERNAME="$API_USERNAME"
fi
if [ -n "$API_PASSWORD" ]; then
  export APP_PASSWORD="$API_PASSWORD"
fi

# Log startup info
echo "==================================================="
echo "Music Assistant Alexa Skill"
echo "==================================================="
echo "Skill Hostname: $SKILL_HOSTNAME"
echo "Music Assistant: $MA_HOSTNAME"
echo "API Username: ${API_USERNAME:-none}"
echo "Port: $PORT"
echo "Locale: $LOCALE"
echo "Region: $AWS_DEFAULT_REGION"
echo "==================================================="
echo ""

# Change to app directory and start
cd /opt/music-assistant

# Ensure python is available
if ! command -v python3 &> /dev/null; then
  echo "ERROR: python3 not found!"
  exit 1
fi

# Verify the app.py exists
if [ ! -f "app/app.py" ]; then
  echo "ERROR: app/app.py not found in /opt/music-assistant"
  ls -la .
  exit 1
fi

echo "Starting app from: $(pwd)"
echo "Python version: $(python3 --version)"
echo "Available files:"
ls -la app/ | head -15
echo ""

# Try importing the app to see if there are import errors
echo "Testing app imports..."
python3 -c "import sys; sys.path.insert(0, 'app'); from app import app; print('✓ App imported successfully')" 2>&1
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to import app"
  exit 1
fi
echo ""

# Start with conditional debugging support
if [ -n "${DEBUG_PORT}" ] && [ "${DEBUG_PORT}" != "0" ]; then
  echo "Starting with debugpy on port ${DEBUG_PORT}..."
  python3 -m pip install --no-cache-dir debugpy 2>&1 | tail -3
  exec python3 -m debugpy --listen 0.0.0.0:${DEBUG_PORT} app/app.py
else
  echo "Starting Music Assistant Alexa Skill on port $PORT..."
  echo "Listening on: 0.0.0.0:$PORT"
  echo "Flask will print more details below:"
  echo "---"
  # Run with unbuffered output, explicit error handling, and timeout
  # Use stdbuf to ensure line buffering and timeout to catch hangs
  exec timeout 60 python3 -u app/app.py 2>&1 || {
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 124 ]; then
      echo "ERROR: Flask startup timed out after 60 seconds"
    fi
    exit $EXIT_CODE
  }
fi
