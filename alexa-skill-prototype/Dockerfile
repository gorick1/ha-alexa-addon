FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /opt/music-assistant

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libffi-dev \
       libssl-dev \
       git \
       curl \
       jq \
       ca-certificates \
       bash \
       xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18 from pre-built binary (much faster than NodeSource)
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then NODE_ARCH="x64"; else NODE_ARCH="$ARCH"; fi && \
    curl -fsSL "https://nodejs.org/dist/v18.20.5/node-v18.20.5-linux-${NODE_ARCH}.tar.xz" \
      -o /tmp/node.tar.xz && \
    tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1 && \
    rm /tmp/node.tar.xz && \
    node --version && npm --version

# Install ASK CLI
RUN npm install -g ask-cli && ask --version || echo "ASK CLI install warning (non-fatal)"

# Clone the upstream repo
RUN git clone https://github.com/alams154/music-assistant-alexa-skill-prototype.git /tmp/skill && \
    cp -r /tmp/skill/app /opt/music-assistant/ && \
    cp -r /tmp/skill/assets /opt/music-assistant/ && \
    cp -r /tmp/skill/scripts /opt/music-assistant/ && \
    rm -rf /tmp/skill

# Install Python dependencies + Waitress
RUN pip install --no-cache-dir -r /opt/music-assistant/app/requirements.txt && \
    pip install --no-cache-dir waitress

# Patch verifier.py for timezone-aware datetime
RUN python3 - <<'PY'
import sysconfig, os, sys
try:
    site = sysconfig.get_paths()['purelib']
except Exception:
    print('Could not determine site-packages; skipping verifier patch')
    sys.exit(0)
vp = os.path.join(site, 'ask_sdk_webservice_support', 'verifier.py')
if not os.path.exists(vp):
    print('verifier.py not found; skipping patch')
    sys.exit(0)
src = open(vp).read()
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
    open(vp, 'w').write(src.replace(needle, patch))
    print('Patched', vp)
else:
    print('No patch needed')
PY

# Make scripts executable
RUN chmod +x /opt/music-assistant/scripts/*.sh || true

# Create needed directories
RUN mkdir -p /opt/music-assistant/bin /run/secrets /root/.ask

# Copy Home Assistant startup wrapper
COPY run.sh /
RUN chmod +x /run.sh

# Copy custom Flask starter
COPY start_app.py /opt/music-assistant/bin/start_app.py

EXPOSE 5000

CMD ["/run.sh"]
