"""
Run the Function Cloud web interface.
"""

import os
import argparse
from function_cloud.web import create_app

def main():
    """Run the Function Cloud web interface."""
    parser = argparse.ArgumentParser(description="Run the Function Cloud web interface.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run the web interface on.")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the web interface on.")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode.")
    args = parser.parse_args()
    
    # Set environment variables
    os.environ.setdefault("FC_SECRET_KEY", os.urandom(24).hex())
    
    # Create and run the app
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
