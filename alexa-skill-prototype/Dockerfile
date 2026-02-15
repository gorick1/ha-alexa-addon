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

# Create secrets directory for Home Assistant configuration
RUN mkdir -p /run/secrets

# Copy Home Assistant startup wrapper
COPY run.sh /
RUN chmod +x /run.sh

# Create a simple Flask starter script that doesn't hang
RUN mkdir -p /opt/music-assistant/bin && cat > /opt/music-assistant/bin/start_app.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/opt/music-assistant')

# Set up environment
os.environ.setdefault('PYTHONUNBUFFERED', '1')

# Import and start the app
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f">>> Starting Flask app on 0.0.0.0:{port}")
    sys.stdout.flush()
    
    # Use threaded mode to prevent hanging
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True,
        use_reloader=False
    )
EOF
chmod +x /opt/music-assistant/bin/start_app.py

EXPOSE 5000 5678

# Run the HA wrapper script which sets up environment and starts the app
CMD ["/run.sh"]
