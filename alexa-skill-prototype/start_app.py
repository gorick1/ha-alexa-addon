#!/usr/bin/env python3
"""
Custom Flask starter script that ensures proper startup.
Uses Waitress WSGI server for better container compatibility.
Bypasses app-level Basic Auth for Home Assistant ingress requests.
"""
import os
import sys
import traceback

# Change to the app directory first
os.chdir('/opt/music-assistant/app')

# Add both directories to path so imports work
sys.path.insert(0, '/opt/music-assistant/app')
sys.path.insert(0, '/opt/music-assistant')

# Set up environment
os.environ.setdefault('PYTHONUNBUFFERED', '1')

try:
    # Import the app
    from app import app
    print("✓ App imported successfully", flush=True)

    # ---------------------------------------------------------------
    # CRITICAL FIX: Disable the app's built-in Basic Auth for ingress
    # ---------------------------------------------------------------
    # Home Assistant ingress already authenticates users via its own
    # session system.  The upstream app enforces HTTP Basic Auth via
    # a @app.before_request handler named "_check_app_basic_auth" and
    # WSGI middleware "BasicAuthMiddleware".  When accessed through
    # ingress (source IP 172.30.32.2) there are no Basic Auth headers
    # so the app returns 401.
    #
    # Strategy: replace the before_request auth check so that requests
    # coming from the HA ingress gateway (172.30.32.2) are always
    # allowed through without credentials.
    # ---------------------------------------------------------------

    # Remove the original _check_app_basic_auth before_request handler
    # Flask stores before_request functions in app.before_request_funcs
    funcs = app.before_request_funcs.get(None, [])
    original_auth_funcs = [f for f in funcs if f.__name__ == '_check_app_basic_auth']
    for f in original_auth_funcs:
        funcs.remove(f)
        print(f">>> Removed original auth handler: {f.__name__}", flush=True)

    # Also unwrap BasicAuthMiddleware from the WSGI stack if present
    wsgi = app.wsgi_app
    # Walk the middleware chain to find and remove BasicAuthMiddleware
    if hasattr(wsgi, '__class__') and wsgi.__class__.__name__ == 'BasicAuthMiddleware':
        app.wsgi_app = wsgi.app
        print(">>> Removed BasicAuthMiddleware from main app WSGI chain", flush=True)

    # Install a new before_request that allows ingress and still
    # enforces Basic Auth for direct external access
    from flask import request, Response
    from env_secrets import get_env_secret

    @app.before_request
    def _ingress_aware_auth():
        """Allow HA ingress (172.30.32.2) without auth; require Basic Auth otherwise."""
        # Always allow health checks
        if request.path == '/health':
            return None
        # Always allow Alexa POST to /
        if request.path == '/' and request.method == 'POST':
            return None
        # Allow all requests from HA ingress gateway
        if request.remote_addr == '172.30.32.2':
            return None
        # Also check X-Forwarded-For for ingress behind proxy
        forwarded = request.headers.get('X-Forwarded-For', '')
        if '172.30.32.2' in forwarded:
            return None
        # For non-ingress requests, enforce Basic Auth if configured
        app_user = get_env_secret('APP_USERNAME')
        app_pass = get_env_secret('APP_PASSWORD')
        if not app_user and not app_pass:
            return None
        auth = request.authorization
        if not auth or auth.username != app_user or auth.password != app_pass:
            resp = Response('Access denied', 401)
            resp.headers['WWW-Authenticate'] = 'Basic realm="music-assistant-skill"'
            return resp
        return None

    print(">>> Installed ingress-aware auth handler (172.30.32.2 bypasses Basic Auth)", flush=True)

    # Add request/response logging
    @app.after_request
    def log_response(response):
        print(f">>> RESPONSE: {request.method} {request.path} -> {response.status_code}", flush=True)
        sys.stdout.flush()
        return response

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        print(">>> HEALTH CHECK HIT", flush=True)
        sys.stdout.flush()
        return {"status": "ok"}, 200

except Exception as e:
    print(f"ERROR importing app: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'

    print(f">>> Starting Flask app with Waitress WSGI server", flush=True)
    print(f">>> Listening on {host}:{port}", flush=True)

    try:
        from waitress import serve
        print(">>> Using Waitress WSGI server", flush=True)
        print(f">>> Serving on http://{host}:{port}", flush=True)
        print(f">>> Ingress requests from 172.30.32.2 will bypass Basic Auth", flush=True)
        sys.stdout.flush()

        serve(app, host=host, port=port, threads=4, _quiet=False)
    except ImportError:
        print(">>> Waitress not available, falling back to Flask dev server", flush=True)
        sys.stdout.flush()
        try:
            app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)
        except Exception as e:
            print(f"ERROR: Flask startup failed: {e}", flush=True)
            traceback.print_exc()
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Waitress startup failed: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
