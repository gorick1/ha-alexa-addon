#!/bin/bash
set -e

# Get options from HA add-on configuration
CONFIG_PATH=/data/options.json

# Extract credentials from config
API_USERNAME=$(jq -r '.api_username // "musicassistant"' "$CONFIG_PATH")
API_PASSWORD=$(jq -r '.api_password // ""' "$CONFIG_PATH")

# Write secrets to files for the app
echo "$API_USERNAME" > /run/secrets/APP_USERNAME
echo "$API_PASSWORD" > /run/secrets/APP_PASSWORD
chmod 600 /run/secrets/*

# Set environment variables
export SKILL_HOSTNAME="${SKILL_HOSTNAME:-home.garrettorick.com}"
export MA_HOSTNAME="${MA_HOSTNAME:-127.0.0.1:8097}"
export APP_USERNAME="/run/secrets/APP_USERNAME"
export APP_PASSWORD="/run/secrets/APP_PASSWORD"
export PORT="${PORT:-5000}"
export DEBUG_PORT="${DEBUG_PORT:-5678}"
export LOCALE="${LOCALE:-en-US}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
export TZ="${TZ:-America/Chicago}"

# Log startup info
echo "==================================================="
echo "Music Assistant Alexa Skill Prototype"
echo "==================================================="
echo "Skill Hostname: $SKILL_HOSTNAME"
echo "Music Assistant: $MA_HOSTNAME"
echo "API Username: $API_USERNAME"
echo "Port: $PORT"
echo "Locale: $LOCALE"
echo "==================================================="
echo ""

# Start the application
cd /app
python main.py
