"""
Entry point for Vercel deployment.
"""

import os
from function_cloud.web import create_app

# Set environment variables
os.environ.setdefault("FC_SECRET_KEY", os.environ.get("FC_SECRET_KEY", os.urandom(24).hex()))

# Create the app
app = create_app()

# This is used by Vercel
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
