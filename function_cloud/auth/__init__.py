"""
Authentication module for Function Cloud (FC).
"""

import os
import json
import time
import uuid
import secrets
from typing import Dict, Optional, Any, Tuple

# Optional imports for OAuth
try:
    import requests
    from oauthlib.oauth2 import WebApplicationClient
    HAS_OAUTH = True
except ImportError:
    HAS_OAUTH = False


class FCAuth:
    """Authentication manager for Function Cloud."""

    # Default paths - use /tmp for Vercel compatibility
    DEFAULT_CONFIG_DIR = os.environ.get("FC_CONFIG_DIR") or (
        "/tmp/function_cloud" if os.environ.get("VERCEL") else os.path.expanduser("~/.function_cloud")
    )
    DEFAULT_CREDENTIALS_FILE = os.path.join(DEFAULT_CONFIG_DIR, "credentials.json")
    DEFAULT_TOKENS_FILE = os.path.join(DEFAULT_CONFIG_DIR, "tokens.json")

    # OAuth settings
    GOOGLE_CLIENT_ID = os.environ.get("FC_GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("FC_GOOGLE_CLIENT_SECRET", "")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    REDIRECT_URL = os.environ.get("FC_REDIRECT_URL", "https://clud-h9ao-saad-momin-s-projects.vercel.app/callback")

    # Default config file path
    DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_DIR, "config.json")

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the authentication manager.

        Args:
            config_dir (str, optional): Directory to store configuration files.
        """
        self.config_dir = config_dir or self.DEFAULT_CONFIG_DIR
        self.credentials_file = os.path.join(self.config_dir, "credentials.json")
        self.tokens_file = os.path.join(self.config_dir, "tokens.json")
        self.config_file = os.path.join(self.config_dir, "config.json")

        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)

        # Load Google OAuth credentials from config file
        self._load_oauth_credentials()

        # Initialize OAuth client if available
        self.oauth_client = None
        if HAS_OAUTH and self.GOOGLE_CLIENT_ID:
            self.oauth_client = WebApplicationClient(self.GOOGLE_CLIENT_ID)

    def _load_oauth_credentials(self):
        """Load OAuth credentials from config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)

                # Load Google OAuth credentials
                if "google_client_id" in config:
                    self.GOOGLE_CLIENT_ID = config["google_client_id"]
                if "google_client_secret" in config:
                    self.GOOGLE_CLIENT_SECRET = config["google_client_secret"]
            except (json.JSONDecodeError, IOError):
                pass

    def generate_token(self) -> str:
        """
        Generate a new secure token.

        Returns:
            str: The generated token.
        """
        # Generate a random token
        token = secrets.token_hex(32)

        # Save the token
        self._save_token(token)

        return token

    def _save_token(self, token: str) -> None:
        """
        Save a token to the tokens file.

        Args:
            token (str): The token to save.
        """
        # Load existing tokens
        tokens = self._load_tokens()

        # Add the new token
        token_id = str(uuid.uuid4())
        tokens[token_id] = {
            "token": token,
            "created_at": time.time(),
            "expires_at": time.time() + 30 * 24 * 60 * 60,  # 30 days
            "active": True
        }

        # Save tokens
        with open(self.tokens_file, "w") as f:
            json.dump(tokens, f)

    def _load_tokens(self) -> Dict[str, Any]:
        """
        Load tokens from the tokens file.

        Returns:
            Dict[str, Any]: The loaded tokens.
        """
        if not os.path.exists(self.tokens_file):
            return {}

        try:
            with open(self.tokens_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def validate_token(self, token: str) -> bool:
        """
        Validate a token.

        Args:
            token (str): The token to validate.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        tokens = self._load_tokens()

        # Check if the token exists and is active
        for token_info in tokens.values():
            if token_info.get("token") == token and token_info.get("active", False):
                # Check if the token has expired
                if token_info.get("expires_at", 0) > time.time():
                    return True

        return False

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token.

        Args:
            token (str): The token to revoke.

        Returns:
            bool: True if the token was revoked, False otherwise.
        """
        tokens = self._load_tokens()

        # Find and revoke the token
        for token_id, token_info in tokens.items():
            if token_info.get("token") == token:
                tokens[token_id]["active"] = False

                # Save tokens
                with open(self.tokens_file, "w") as f:
                    json.dump(tokens, f)

                return True

        return False

    def get_google_auth_url(self, redirect_uri: str) -> str:
        """
        Get the Google OAuth authorization URL.

        Args:
            redirect_uri (str): The redirect URI for the OAuth flow.

        Returns:
            str: The authorization URL.
        """
        if not HAS_OAUTH:
            raise ImportError("OAuth dependencies not installed. Install with 'pip install function-cloud[auth]'.")

        if not self.oauth_client:
            raise ValueError("Google OAuth client not initialized. Set FC_GOOGLE_CLIENT_ID environment variable.")

        # Use the configured redirect URL if available
        redirect_uri = self.REDIRECT_URL or redirect_uri

        # Get Google's OAuth 2.0 endpoints
        google_provider_cfg = requests.get(self.GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Generate a random state for CSRF protection
        state = secrets.token_hex(16)

        # Store the state and redirect URI in a session-like mechanism
        # This is a simple implementation; in production, use a proper session
        state_file = os.path.join(self.config_dir, f"state_{state}.json")
        with open(state_file, "w") as f:
            json.dump({"redirect_uri": redirect_uri}, f)

        # Generate the authorization URL
        auth_url = self.oauth_client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=["openid", "email", "profile"],
            state=state
        )

        return auth_url

    def _save_credentials(self, user_info: Dict[str, Any], token: str) -> None:
        """
        Save user credentials to the credentials file.

        Args:
            user_info (Dict[str, Any]): User information from Google OAuth.
            token (str): The generated token for the user.
        """
        # Create credentials file directory if it doesn't exist
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)

        # Load existing credentials
        credentials = {}
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, "r") as f:
                    credentials = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Add or update user credentials
        user_id = user_info.get("sub")
        if user_id:
            credentials[user_id] = {
                "email": user_info.get("email", ""),
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", ""),
                "token": token,
                "created_at": time.time()
            }

            # Save credentials
            with open(self.credentials_file, "w") as f:
                json.dump(credentials, f)

    def handle_google_callback(self, redirect_uri: str, authorization_response: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Handle the Google OAuth callback.

        Args:
            redirect_uri (str): The redirect URI for the OAuth flow.
            authorization_response (str): The authorization response from Google.

        Returns:
            Tuple[bool, str, Dict[str, Any]]: A tuple containing:
                - bool: True if authentication was successful, False otherwise.
                - str: A message describing the result.
                - Dict[str, Any]: User information if authentication was successful.
        """
        if not HAS_OAUTH:
            raise ImportError("OAuth dependencies not installed. Install with 'pip install function-cloud[auth]'.")

        if not self.oauth_client:
            raise ValueError("Google OAuth client not initialized. Set FC_GOOGLE_CLIENT_ID environment variable.")

        # Use the configured redirect URL if available
        redirect_uri = self.REDIRECT_URL or redirect_uri

        # Extract state from the authorization response
        try:
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(authorization_response)
            state = parse_qs(parsed_url.query).get('state', [None])[0]

            # If state is available, try to load the stored redirect URI
            if state:
                state_file = os.path.join(self.config_dir, f"state_{state}.json")
                if os.path.exists(state_file):
                    with open(state_file, "r") as f:
                        data = json.load(f)
                        stored_redirect_uri = data.get("redirect_uri")
                        if stored_redirect_uri:
                            redirect_uri = stored_redirect_uri

                    # Clean up the state file
                    try:
                        os.remove(state_file)
                    except:
                        pass
        except:
            # If anything goes wrong, continue with the provided redirect URI
            pass

        # Get Google's OAuth 2.0 endpoints
        google_provider_cfg = requests.get(self.GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]

        # Prepare the token request
        token_url, headers, body = self.oauth_client.prepare_token_request(
            token_endpoint,
            authorization_response=authorization_response,
            redirect_url=redirect_uri,
            client_secret=self.GOOGLE_CLIENT_SECRET
        )

        # Get the token
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(self.GOOGLE_CLIENT_ID, self.GOOGLE_CLIENT_SECRET)
        )

        # Parse the token
        self.oauth_client.parse_request_body_response(json.dumps(token_response.json()))

        # Get user info
        uri, headers, body = self.oauth_client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        if userinfo_response.json().get("email_verified"):
            # User is verified
            user_info = userinfo_response.json()

            # Generate a token for the user
            token = self.generate_token()

            # Save user credentials
            self._save_credentials(user_info, token)

            return True, "Authentication successful", user_info
        else:
            return False, "User email not verified", {}


__all__ = ["FCAuth"]
