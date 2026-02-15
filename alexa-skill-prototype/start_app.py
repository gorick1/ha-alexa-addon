#!/usr/bin/env python3
"""
Custom Flask starter script that ensures proper startup.
Uses Waitress WSGI server for better container compatibility.
Bypasses app-level Basic Auth for Home Assistant ingress requests.
Rewrites absolute URL paths in HTML so they work behind HA ingress.
Overrides HTTP_HOST for ingress requests so internal self-checks
(status page) use localhost instead of the public domain (hairpin NAT fix).
"""
import os
import sys
import re
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
    funcs = app.before_request_funcs.get(None, [])
    original_auth_funcs = [f for f in funcs if f.__name__ == '_check_app_basic_auth']
    for f in original_auth_funcs:
        funcs.remove(f)
        print(f">>> Removed original auth handler: {f.__name__}", flush=True)

    # Unwrap BasicAuthMiddleware from the WSGI stack if present
    wsgi = app.wsgi_app
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

    # ---------------------------------------------------------------
    # INGRESS PATH REWRITING + HAIRPIN NAT FIX MIDDLEWARE
    # ---------------------------------------------------------------
    # HA ingress serves the add-on under /api/hassio_ingress/<token>/
    # The upstream templates use absolute paths like /setup/start which
    # would be sent to the HA root and 404.  This middleware detects
    # the X-Ingress-Path header that HA sends and rewrites absolute
    # URL references in HTML responses so they work correctly.
    #
    # HAIRPIN NAT FIX: The upstream status page uses request.host_url
    # to build self-check URLs (e.g. /ma/latest-url, /alexa/latest-url).
    # When accessed through HA ingress, request.host_url resolves to
    # the public domain (e.g. home.garrettorick.com), but the container
    # can't reach itself via that domain (hairpin NAT). We override
    # HTTP_HOST to localhost:<port> for ingress requests so the self-
    # checks work correctly.
    # ---------------------------------------------------------------

    class IngressPathRewriteMiddleware:
        """WSGI middleware that:
        1. Overrides HTTP_HOST for ingress requests (hairpin NAT fix)
        2. Rewrites absolute URL paths in HTML responses for HA ingress"""

        # Paths used by the upstream app that need rewriting in HTML
        PATHS_TO_REWRITE = [
            '/setup/start',
            '/setup/stop',
            '/setup/code',
            '/setup/logs/download',
            '/setup',
            '/status/api',
            '/status/ask',
            '/status/ma',
            '/status/alexa',
            '/status/invocations',
            '/status',
            '/invocations',
        ]

        def __init__(self, wsgi_app):
            self.wsgi_app = wsgi_app

        def __call__(self, environ, start_response):
            ingress_path = environ.get('HTTP_X_INGRESS_PATH', '')

            if not ingress_path:
                # Not coming through ingress - pass through unchanged
                return self.wsgi_app(environ, start_response)

            # --- HAIRPIN NAT FIX ---
            # Override HTTP_HOST so that request.host_url inside Flask
            # resolves to localhost:<port> instead of the public domain.
            # This makes the status page's self-HTTP-checks (requests.get)
            # hit localhost, which is always reachable from inside the container.
            port = os.environ.get('PORT', '5000')
            environ['HTTP_HOST'] = f'localhost:{port}'
            # Also update SERVER_NAME if present
            environ['SERVER_NAME'] = 'localhost'
            environ['SERVER_PORT'] = port

            # Strip trailing slash from ingress path
            ingress_path = ingress_path.rstrip('/')

            # Collect the response
            response_started = []
            response_headers = []
            write_func = [None]

            def custom_start_response(status, headers, exc_info=None):
                response_started.append(status)
                response_headers.append(headers)
                # Check content type
                content_type = ''
                for name, value in headers:
                    if name.lower() == 'content-type':
                        content_type = value
                        break

                if 'text/html' in content_type:
                    # We need to buffer this response to rewrite paths
                    def dummy_write(data):
                        pass
                    write_func[0] = dummy_write
                    return dummy_write
                else:
                    # Not HTML - pass through
                    write_func[0] = start_response(status, headers, exc_info)
                    return write_func[0]

            result = self.wsgi_app(environ, custom_start_response)

            status = response_started[0] if response_started else '500 Internal Server Error'
            headers = response_headers[0] if response_headers else []

            # Check if this is an HTML response that needs rewriting
            content_type = ''
            for name, value in headers:
                if name.lower() == 'content-type':
                    content_type = value
                    break

            if 'text/html' not in content_type:
                # Non-HTML: already started the real response, just return body
                return result

            # Buffer the full HTML body
            body_parts = []
            try:
                for chunk in result:
                    body_parts.append(chunk)
            finally:
                if hasattr(result, 'close'):
                    result.close()

            body = b''.join(body_parts)

            try:
                html = body.decode('utf-8')
            except UnicodeDecodeError:
                html = body.decode('latin-1')

            # Rewrite absolute paths in the HTML
            # Sort paths longest first so /setup/start matches before /setup
            sorted_paths = sorted(self.PATHS_TO_REWRITE, key=len, reverse=True)
            for path in sorted_paths:
                # Replace in fetch(), window.location, href, etc.
                # But only if not already prefixed
                html = html.replace(f"'{path}", f"'{ingress_path}{path}")
                html = html.replace(f'"{path}', f'"{ingress_path}{path}')

            new_body = html.encode('utf-8')

            # Update Content-Length header
            new_headers = []
            for name, value in headers:
                if name.lower() == 'content-length':
                    new_headers.append((name, str(len(new_body))))
                else:
                    new_headers.append((name, value))

            start_response(status, new_headers)
            return [new_body]

    # Wrap the Flask WSGI app with our ingress path rewriting middleware
    app.wsgi_app = IngressPathRewriteMiddleware(app.wsgi_app)
    print(">>> Installed IngressPathRewriteMiddleware (with hairpin NAT fix) for HA ingress", flush=True)

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
