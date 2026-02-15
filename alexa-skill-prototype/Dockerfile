FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone the Alexa skill prototype repository
RUN git clone https://github.com/alams154/music-assistant-alexa-skill-prototype.git .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create secrets directory
RUN mkdir -p /run/secrets

# Copy run script
COPY run.sh /
RUN chmod +x /run.sh

# Expose ports
EXPOSE 5000 5678

# Run the application
CMD ["/run.sh"]
