"""
Configuration for the Function Cloud (FC) library.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

class FCConfig:
    """Configuration for the FC library."""
    # Default values
    token: str = None
    region: str = "us-east"
    memory: int = 1024
    timeout: int = 60
    cpu: int = 1
    llm_enabled: bool = True
    llm_api_key: str = None
    llm_provider: str = "groq"  # Using Groq as the default LLM provider
    stub_name: str = "fc_app"
    validate_token: bool = False
    config_dir: str = None

    # Default Modal credentials - will be loaded from environment variables
    MODAL_TOKEN_ID = os.environ.get("MODAL_TOKEN_ID", "")
    MODAL_TOKEN_SECRET = os.environ.get("MODAL_TOKEN_SECRET", "")

    # Default Groq API key - will be loaded from environment variables
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

    @classmethod
    def load_from_env(cls):
        """Load configuration from environment variables."""
        # Modal token
        if os.environ.get("MODAL_TOKEN"):
            cls.token = os.environ.get("MODAL_TOKEN")
        elif os.environ.get("MODAL_TOKEN_ID") and os.environ.get("MODAL_TOKEN_SECRET"):
            # Format: "token_id:token_secret"
            cls.token = f"{os.environ.get('MODAL_TOKEN_ID')}:{os.environ.get('MODAL_TOKEN_SECRET')}"

        # Groq API key
        if os.environ.get("GROQ_API_KEY"):
            cls.llm_api_key = os.environ.get("GROQ_API_KEY")
            cls.llm_enabled = True

        # Other configuration
        if os.environ.get("FC_REGION"):
            cls.region = os.environ.get("FC_REGION")
        if os.environ.get("FC_MEMORY"):
            cls.memory = int(os.environ.get("FC_MEMORY"))
        if os.environ.get("FC_TIMEOUT"):
            cls.timeout = int(os.environ.get("FC_TIMEOUT"))
        if os.environ.get("FC_CPU"):
            cls.cpu = int(os.environ.get("FC_CPU"))
        if os.environ.get("FC_LLM_PROVIDER"):
            cls.llm_provider = os.environ.get("FC_LLM_PROVIDER")
        if os.environ.get("FC_STUB_NAME"):
            cls.stub_name = os.environ.get("FC_STUB_NAME")

    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None):
        """
        Load configuration from a file.

        Args:
            config_path (str, optional): Path to the configuration file.
                If not provided, will look for ~/.function_cloud/config.json
        """
        if not config_path:
            home_dir = Path.home()
            config_dir = home_dir / ".function_cloud"
            config_path = config_dir / "config.json"

        if Path(config_path).exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)

                # Modal token
                if "token" in config:
                    cls.token = config["token"]
                elif "modal_token_id" in config and "modal_token_secret" in config:
                    cls.token = f"{config['modal_token_id']}:{config['modal_token_secret']}"

                # Groq API key
                if "llm_api_key" in config:
                    cls.llm_api_key = config["llm_api_key"]
                    cls.llm_enabled = True
                elif "groq_api_key" in config:
                    cls.llm_api_key = config["groq_api_key"]
                    cls.llm_enabled = True

                # Other configuration
                for key, value in config.items():
                    if hasattr(cls, key) and key not in ["token", "llm_api_key"]:
                        setattr(cls, key, value)
            except (json.JSONDecodeError, IOError):
                pass

    @classmethod
    def use_default_credentials(cls):
        """Use default credentials if no custom ones are provided."""
        if not cls.token:
            cls.token = f"{cls.MODAL_TOKEN_ID}:{cls.MODAL_TOKEN_SECRET}"

        if not cls.llm_api_key and cls.llm_enabled:
            # First try to get from environment
            if os.environ.get("GROQ_API_KEY"):
                cls.llm_api_key = os.environ.get("GROQ_API_KEY")
                print(f"Using Groq API key from environment: {cls.llm_api_key[:10]}...")
            else:
                # Fall back to default
                cls.llm_api_key = cls.GROQ_API_KEY
                print(f"Using default Groq API key: {cls.llm_api_key[:10]}...")

    @classmethod
    def validate(cls):
        """Validate the configuration."""
        # Try to load from environment and file first
        cls.load_from_env()
        cls.load_from_file()

        # Use default credentials if needed
        cls.use_default_credentials()

        # Final validation
        if not cls.token:
            raise ValueError("FC token not configured. Call FC.configure(token='your_token') first.")
