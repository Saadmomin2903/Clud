"""
Flask application for Function Cloud (FC) web interface.
"""

import os
import json
from typing import Optional

# Optional imports for web interface
try:
    from flask import Flask, render_template, redirect, request, url_for, session, jsonify
    from flask_login import LoginManager, login_user, logout_user, login_required, current_user
    import oauthlib.oauth2
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

from function_cloud.auth import FCAuth
from function_cloud.web.models import User


def create_app(config_dir: Optional[str] = None) -> "Flask":
    """
    Create a Flask application for the Function Cloud web interface.
    """
    if not HAS_FLASK:
        raise ImportError("Flask dependencies not installed. Install with 'pip install function-cloud[web]'.")
    
    # Allow OAuth2 to work on HTTP for local development
    if os.environ.get("FLASK_ENV") != "production":
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create Flask app with explicit template and static folders
    app = Flask(__name__,
                template_folder=os.path.join(current_dir, 'templates'),
                static_folder=os.path.join(current_dir, 'static'))
    
    app.secret_key = os.environ.get("FC_SECRET_KEY", os.urandom(24))
    
    # Initialize authentication
    auth = FCAuth(config_dir)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    
    @login_manager.user_loader
    def load_user(user_id):
        # Load user from credentials file
        credentials_file = os.path.join(auth.config_dir, "credentials.json")
        if os.path.exists(credentials_file):
            try:
                with open(credentials_file, "r") as f:
                    credentials = json.load(f)
                    if user_id in credentials:
                        user_info = credentials[user_id]
                        return User(
                            id=user_id,
                            email=user_info.get("email", ""),
                            name=user_info.get("name", ""),
                            token=user_info.get("token", "")
                        )
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return None
    
    @app.route("/")
    def index():
        """Home page."""
        return render_template("index.html")
    
    @app.route("/login")
    def login():
        """Login page."""
        # Get the Google OAuth URL
        redirect_uri = url_for("callback", _external=True)
        auth_url = auth.get_google_auth_url(redirect_uri)
        return render_template("login.html", auth_url=auth_url)
    
    @app.route("/callback")
    def callback():
        """OAuth callback."""
        # Handle the OAuth callback
        redirect_uri = url_for("callback", _external=True)
        success, message, user_info = auth.handle_google_callback(
            redirect_uri,
            request.url
        )
        
        if success:
            # Create a user object
            user = User(
                id=user_info["sub"],
                email=user_info["email"],
                name=user_info.get("name", ""),
                token=user_info.get("token", "")
            )
            
            # Log in the user
            login_user(user)
            
            # Redirect to dashboard
            return redirect(url_for("dashboard"))
        else:
            # Redirect to login with error
            return redirect(url_for("login", error=message))
    
    @app.route("/dashboard")
    @login_required
    def dashboard():
        """User dashboard."""
        return render_template("dashboard.html", user=current_user)
    
    @app.route("/logout")
    @login_required
    def logout():
        """Log out the user."""
        logout_user()
        return redirect(url_for("index"))
    
    @app.route("/api/token", methods=["GET"])
    @login_required
    def get_token():
        """Get the user's token."""
        return jsonify({"token": current_user.token})
    
    @app.route("/api/token/refresh", methods=["POST"])
    @login_required
    def refresh_token():
        """Refresh the user's token."""
        # Revoke the old token
        auth.revoke_token(current_user.token)
        
        # Generate a new token
        token = auth.generate_token()
        
        # Update the user's token
        current_user.token = token
        
        # Save the user's credentials
        credentials_file = os.path.join(auth.config_dir, "credentials.json")
        if os.path.exists(credentials_file):
            try:
                with open(credentials_file, "r") as f:
                    credentials = json.load(f)
                    if current_user.id in credentials:
                        credentials[current_user.id]["token"] = token
                        with open(credentials_file, "w") as f:
                            json.dump(credentials, f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return jsonify({"token": token})
    
    return app
