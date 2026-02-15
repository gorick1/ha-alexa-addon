FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /opt/music-assistant

# Install system dependencies (including git, Node.js for ASK CLI)
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
       gnupg \
       ca-certificates \
       bash \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18 (required for ASK CLI)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install ASK CLI (Alexa Skills Kit) globally
RUN npm install -g ask-cli || true

# Clone the Music Assistant Alexa Skill repository
RUN git clone https://github.com/alams154/music-assistant-alexa-skill-prototype.git /tmp/skill && \
    cp -r /tmp/skill/app /opt/music-assistant/ && \
    cp -r /tmp/skill/assets /opt/music-assistant/ && \
    cp -r /tmp/skill/scripts /opt/music-assistant/ && \
    rm -rf /tmp/skill

# Install Python dependencies and Waitress WSGI server
RUN pip install --no-cache-dir -r /opt/music-assistant/app/requirements.txt && \
    pip install --no-cache-dir waitress

# Apply verifier.py timezone patch (upstream fix for newer cryptography libs)
RUN python3 - <<'PY'
import sysconfig, os, sys
try:
    site = sysconfig.get_paths()['purelib']
except Exception:
    print('Could not determine site-packages path; skipping verifier patch')
    sys.exit(0)
verifier_path = os.path.join(site, 'ask_sdk_webservice_support', 'verifier.py')
if not os.path.exists(verifier_path):
    print('verifier.py not found at', verifier_path, '; skipping patch')
    sys.exit(0)
with open(verifier_path, 'r', encoding='utf-8') as f:
    src = f.read()
needle = (
    '        now = datetime.utcnow()\n'
    '        if not (x509_cert.not_valid_before <= now <=\n'
    '                x509_cert.not_valid_after):\n'
    '            raise VerificationException("Signing Certificate expired")'
)
patch = (
    '        from datetime import timezone\n'
    '        now = datetime.now(timezone.utc)\n'
    "        not_valid_before = getattr(x509_cert, 'not_valid_before_utc', None) or x509_cert.not_valid_before.replace(tzinfo=timezone.utc)\n"
    "        not_valid_after = getattr(x509_cert, 'not_valid_after_utc', None) or x509_cert.not_valid_after.replace(tzinfo=timezone.utc)\n"
    '        if not (not_valid_before <= now <= not_valid_after):\n'
    '            raise VerificationException("Signing Certificate expired")'
)
if needle in src:
    new_src = src.replace(needle, patch)
    with open(verifier_path, 'w', encoding='utf-8') as f:
        f.write(new_src)
    print('Patched', verifier_path)
else:
    print('No patch needed for verifier.py')
PY

# Make scripts executable
RUN chmod +x /opt/music-assistant/scripts/*.sh || true

# Create symlinks to ensure python command works
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Create bin and secrets directories
RUN mkdir -p /opt/music-assistant/bin /run/secrets /root/.ask

# Copy Home Assistant startup wrapper
COPY run.sh /
RUN chmod +x /run.sh

# Copy and setup custom Flask starter script
COPY start_app.py /opt/music-assistant/bin/start_app.py
RUN chmod +x /opt/music-assistant/bin/start_app.py

EXPOSE 5000 5678

CMD ["/run.sh"]
