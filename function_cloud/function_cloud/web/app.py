"""
Flask application for Function Cloud (FC) web interface.
"""

import os
import json
import sys
import io
import uuid
import tempfile
import importlib.util
import traceback
from typing import Optional, Dict, Any, Tuple

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

    Args:
        config_dir (str, optional): Directory to store configuration files.

    Returns:
        Flask: The Flask application.
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

    @app.route("/docs")
    def docs():
        """Documentation page."""
        return render_template("docs.html")

    @app.route("/playground")
    @login_required
    def playground():
        """Developer playground."""
        return render_template("playground.html")

    @app.route("/api/playground/run", methods=["POST"])
    @login_required
    def run_playground_code():
        """Run code in the playground."""
        code = request.json.get("code", "")

        # Capture stdout to get print output
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        result = ""
        error = None
        temp_module_name = f"fc_playground_{uuid.uuid4().hex}"

        try:
            # Create a temporary directory to store the module
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, f"{temp_module_name}.py")

            # Write the code to a temporary file
            with open(temp_file_path, 'w') as f:
                f.write(code)

            # Add the temp directory to sys.path so we can import the module
            sys.path.insert(0, temp_dir)

            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(temp_module_name, temp_file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Get the output
                result = redirected_output.getvalue()
            finally:
                # Clean up: remove the temporary directory from sys.path
                if temp_dir in sys.path:
                    sys.path.remove(temp_dir)

                # Clean up: remove the temporary file and directory
                try:
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)
                except:
                    pass  # Ignore cleanup errors

        except Exception as e:
            error = str(e)
            result = traceback.format_exc()
        finally:
            # Restore stdout
            sys.stdout = old_stdout

        return jsonify({
            "output": result,
            "error": error
        })

    @app.route("/api/playground/deploy", methods=["POST"])
    @login_required
    def deploy_playground_code():
        """Deploy code from the playground."""
        code = request.json.get("code", "")
        code_type = request.json.get("type", "function")

        # Capture stdout to get print output
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        result = ""
        error = None
        url = None
        temp_module_name = f"fc_playground_{uuid.uuid4().hex}"

        try:
            # Create a temporary directory to store the module
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, f"{temp_module_name}.py")

            # Write the code to a temporary file
            with open(temp_file_path, 'w') as f:
                f.write(code)

            # Add the temp directory to sys.path so we can import the module
            sys.path.insert(0, temp_dir)

            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(temp_module_name, temp_file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Get the output
                result = redirected_output.getvalue()

                # Try to extract the URL from the output
                for line in result.split("\n"):
                    if "URL:" in line:
                        url = line.split("URL:")[1].strip()
                        break
            finally:
                # Clean up: remove the temporary directory from sys.path
                if temp_dir in sys.path:
                    sys.path.remove(temp_dir)

                # Clean up: remove the temporary file and directory
                try:
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)
                except:
                    pass  # Ignore cleanup errors

        except Exception as e:
            error = str(e)
            result = traceback.format_exc()
        finally:
            # Restore stdout
            sys.stdout = old_stdout

        return jsonify({
            "output": result,
            "error": error,
            "url": url
        })

    return app
