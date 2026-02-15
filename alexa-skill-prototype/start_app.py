#!/usr/bin/env python3
"""
Custom Flask starter script that ensures proper startup.
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
