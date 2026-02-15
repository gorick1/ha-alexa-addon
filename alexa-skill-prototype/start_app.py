#!/usr/bin/env python3
"""
Custom Flask starter script that ensures proper startup.
Uses Waitress WSGI server for better container compatibility.
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
    
    # Add request logging middleware
    @app.before_request
    def log_request():
        import sys
        from flask import request
        print(f">>> REQUEST: {request.method} {request.path} from {request.remote_addr}", flush=True)
        sys.stdout.flush()
    
    @app.after_request
    def log_response(response):
        import sys
        from flask import request
        print(f">>> RESPONSE: {request.method} {request.path} -> {response.status_code}", flush=True)
        sys.stdout.flush()
        return response
    
    # Add a simple health check route that always responds
    @app.route('/health', methods=['GET'])
    def health():
        import sys
        print(f">>> HEALTH CHECK HIT", flush=True)
        sys.stdout.flush()
        return {"status": "ok"}, 200
    
    @app.route('/', methods=['GET'])
    def root():
        import sys
        print(f">>> ROOT PATH HIT", flush=True)
        sys.stdout.flush()
        return {"message": "Music Assistant Alexa Skill is running"}, 200
        
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
        # Try to import and use Waitress (better for containers)
        from waitress import serve
        print(">>> Using Waitress WSGI server", flush=True)
        print(f">>> Serving on http://{host}:{port}", flush=True)
        print(f">>> This add-on is ready for Home Assistant ingress requests", flush=True)
        print(f">>> Test with: curl http://{host}:{port}/health", flush=True)
        sys.stdout.flush()
        
        # Serve with explicit error handling
        serve(app, host=host, port=port, threads=4, _quiet=False)
    except ImportError:
        print(">>> Waitress not available, falling back to Flask development server", flush=True)
        sys.stdout.flush()
        try:
            # Fallback to Flask if Waitress isn't installed
            app.run(
                host=host,
                port=port,
                debug=False,
                threaded=True,
                use_reloader=False
            )
        except Exception as e:
            print(f"ERROR: Flask startup failed: {e}", flush=True)
            traceback.print_exc()
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Waitress startup failed: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
