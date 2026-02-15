FROM ghcr.io/alams154/music-assistant-skill:latest

# Install jq for JSON parsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Create secrets directory for Home Assistant
RUN mkdir -p /run/secrets

# Copy run script
COPY run.sh /
RUN chmod +x /run.sh

# Override entrypoint with our HA-specific run script
ENTRYPOINT []
CMD ["/run.sh"]
