FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /opt/music-assistant

# Install system dependencies (including git to clone the repo)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3 \
       python3-pip \
       build-essential \
       libffi-dev \
       libssl-dev \
       git \
       curl \
       jq \
    && rm -rf /var/lib/apt/lists/*

# Clone the Music Assistant Alexa Skill repository
RUN git clone https://github.com/alams154/music-assistant-alexa-skill-prototype.git /tmp/skill && \
    cp -r /tmp/skill/app /opt/music-assistant/ && \
    cp -r /tmp/skill/assets /opt/music-assistant/ && \
    cp -r /tmp/skill/scripts /opt/music-assistant/ && \
    rm -rf /tmp/skill

# Install Python dependencies
RUN pip install --no-cache-dir -r /opt/music-assistant/app/requirements.txt

# Create symlinks to ensure python command works
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Create bin and secrets directories
RUN mkdir -p /opt/music-assistant/bin /run/secrets

# Copy Home Assistant startup wrapper
COPY run.sh /
RUN chmod +x /run.sh

# Copy and setup custom Flask starter script
COPY start_app.py /opt/music-assistant/bin/start_app.py
RUN chmod +x /opt/music-assistant/bin/start_app.py

EXPOSE 5000 5678

# Run the HA wrapper script which sets up environment and starts the app
CMD ["/run.sh"]
