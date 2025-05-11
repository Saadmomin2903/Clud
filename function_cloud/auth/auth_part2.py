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
