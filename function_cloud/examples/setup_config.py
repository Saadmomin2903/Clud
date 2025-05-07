"""
Script to set up Function Cloud configuration.
"""

import os
import json
import argparse
from pathlib import Path

def main():
    """Set up Function Cloud configuration."""
    parser = argparse.ArgumentParser(description="Set up Function Cloud configuration.")
    parser.add_argument("--modal-token-id", help="Modal token ID")
    parser.add_argument("--modal-token-secret", help="Modal token secret")
    parser.add_argument("--groq-api-key", help="Groq API key")
    parser.add_argument("--google-client-id", help="Google OAuth client ID")
    parser.add_argument("--google-client-secret", help="Google OAuth client secret")
    parser.add_argument("--config-dir", default="~/.function_cloud", help="Configuration directory")
    args = parser.parse_args()
    
    # Expand config directory path
    config_dir = os.path.expanduser(args.config_dir)
    
    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    
    # Config file path
    config_file = os.path.join(config_dir, "config.json")
    
    # Load existing config if it exists
    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Update config with provided values
    if args.modal_token_id:
        config["modal_token_id"] = args.modal_token_id
    if args.modal_token_secret:
        config["modal_token_secret"] = args.modal_token_secret
    if args.groq_api_key:
        config["groq_api_key"] = args.groq_api_key
    if args.google_client_id:
        config["google_client_id"] = args.google_client_id
    if args.google_client_secret:
        config["google_client_secret"] = args.google_client_secret
    
    # Save config
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    
    # Set permissions to user only
    os.chmod(config_file, 0o600)
    
    print(f"Configuration saved to {config_file}")
    print("The following credentials are configured:")
    if "modal_token_id" in config and "modal_token_secret" in config:
        print("- Modal token: ✓")
    else:
        print("- Modal token: ✗")
    if "groq_api_key" in config:
        print("- Groq API key: ✓")
    else:
        print("- Groq API key: ✗")
    if "google_client_id" in config and "google_client_secret" in config:
        print("- Google OAuth: ✓")
    else:
        print("- Google OAuth: ✗")
    
    print("\nYou can now use Function Cloud with the configured credentials:")
    print("```python")
    print("from function_cloud import FC")
    print("FC.configure()")  # Will use the configured credentials
    print("```")

if __name__ == "__main__":
    main()
