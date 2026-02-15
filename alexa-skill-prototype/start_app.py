#!/usr/bin/env python3
"""
Custom Flask starter script that ensures proper startup.
Uses Waitress WSGI server for better container compatibility.
"""
import os
import sys

# Change to the app directory first
os.chdir('/opt/music-assistant/app')

# Add both directories to path so imports work
sys.path.insert(0, '/opt/music-assistant/app')
sys.path.insert(0, '/opt/music-assistant')

# Set up environment
os.environ.setdefault('PYTHONUNBUFFERED', '1')

# Import the app
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f">>> Starting Flask app with Waitress WSGI server")
    print(f">>> Listening on {host}:{port}")
    sys.stdout.flush()
    
    try:
        # Try to import and use Waitress (better for containers)
        from waitress import serve
        print(">>> Using Waitress WSGI server")
        sys.stdout.flush()
        serve(app, host=host, port=port, threads=4)
    except ImportError:
        print(">>> Waitress not available, falling back to Flask development server")
        sys.stdout.flush()
        # Fallback to Flask if Waitress isn't installed
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
