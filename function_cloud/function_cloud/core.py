"""
Core functionality for the Function Cloud (FC) library.
"""

import inspect
import hashlib
import os
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar, Set, Tuple

from function_cloud.config import FCConfig
from function_cloud.dependency_analyzer import DependencyAnalyzer
from function_cloud.deployer import FCDeployer
from function_cloud.url_manager import FCURLManager
from function_cloud.auth import FCAuth

T = TypeVar('T')

class FC:
    """Main Function Cloud class for deploying functions to Modal.com."""

    @classmethod
    def configure(cls, token: str = None, **kwargs):
        """
        Configure the FC library.

        Args:
            token (str, optional): Your Modal.com API token.
                Can be in format "token_id:token_secret" or a single token string.
            **kwargs: Additional configuration options.
                - region (str): Cloud region (default: "us-east")
                - memory (int): Memory allocation in MB (default: 1024)
                - timeout (int): Function timeout in seconds (default: 60)
                - cpu (int): CPU allocation (default: 1)
                - llm_enabled (bool): Whether to use LLM for dependency analysis (default: True)
                - llm_api_key (str): API key for LLM service
                - llm_provider (str): LLM provider (default: "groq")
                - stub_name (str): Name for Modal stub (default: "fc_app")
                - validate_token (bool): Whether to validate the token (default: False)
                - config_path (str): Path to a configuration file
                - use_default_credentials (bool): Whether to use default credentials (default: True)
        """
        # Initialize authentication
        auth = FCAuth()

        # Load configuration from environment variables and file
        FCConfig.load_from_env()

        # Load from config file if specified
        if "config_path" in kwargs:
            FCConfig.load_from_file(kwargs["config_path"])
        else:
            FCConfig.load_from_file()

        # If token is provided, validate it if requested
        if token:
            if kwargs.get("validate_token", False):
                if not auth.validate_token(token):
                    raise ValueError("Invalid token. Please provide a valid token or generate a new one.")
            FCConfig.token = token

        # Set other configuration options
        for key, value in kwargs.items():
            if hasattr(FCConfig, key) and key != "config_path":
                setattr(FCConfig, key, value)

        # Use default credentials if requested and needed
        if kwargs.get("use_default_credentials", True):
            FCConfig.use_default_credentials()

        # Debug information about the configuration
        print(f"Configuration complete:")
        print(f"  - Token: {'Set' if FCConfig.token else 'Not set'}")
        print(f"  - LLM API Key: {FCConfig.llm_api_key[:10]}... (from {'environment' if os.environ.get('GROQ_API_KEY') else 'default'})")

    @classmethod
    def function(cls, func: Callable) -> Callable:
        """
        Decorator to deploy a function to Modal.

        Args:
            func (Callable): The function to deploy.

        Returns:
            Callable: The wrapped function.

        Example:
            ```python
            @FC.function
            def add(x, y):
                return x + y
            ```
        """
        FCConfig.validate()

        @wraps(func)
        def wrapper(*args, **kwargs):
            # If this is the first call, deploy to Modal
            if not hasattr(func, "_fc_deployed") or not func._fc_deployed:
                try:
                    # Analyze dependencies
                    imports = DependencyAnalyzer.analyze_imports(func)

                    # Try to enhance with LLM, but catch any errors
                    try:
                        dependencies = DependencyAnalyzer.enhance_with_llm(func, imports)
                    except Exception as llm_error:
                        print(f"LLM enhancement failed, falling back to basic analysis: {llm_error}")
                        # Fallback to basic dependency analysis
                        dependencies = {"packages": list(imports)}

                    # Create Modal function
                    modal_func = FCDeployer.create_modal_function(func, dependencies)

                    # Deploy function
                    url = FCDeployer.deploy_function(modal_func)

                    # Mark as deployed
                    func._fc_deployed = True
                    # The URL might have been set on the original function by deploy_function
                    # if the function has __wrapped__ attribute, but we set it here as well
                    # to ensure it's always available
                    func._fc_url = url
                    func._fc_modal_func = modal_func
                except ImportError as e:
                    print(f"Warning: {e}")
                    print("Running in local-only mode.")
                    # Mark as deployed to avoid repeated attempts
                    func._fc_deployed = True
                    func._fc_url = f"https://example.com/{func.__module__}.{func.__name__}"

            # If called directly, execute locally
            return func(*args, **kwargs)

        # Add method to get the function's URL
        def get_url():
            if not hasattr(func, "_fc_url"):
                raise ValueError("Function not yet deployed. Call it once to trigger deployment.")
            return func._fc_url

        wrapper.get_url = get_url

        return wrapper

    @classmethod
    def method(cls, method: Callable) -> Callable:
        """
        Decorator for class methods.

        Args:
            method (Callable): The class method to deploy.

        Returns:
            Callable: The wrapped method.

        Example:
            ```python
            class MyService:
                @FC.method
                def process_data(self, data):
                    return data.upper()
            ```
        """
        return cls.function(method)

    @classmethod
    def endpoint(cls, methods=None):
        """
        Decorator for API endpoints.

        Args:
            methods (List[str], optional): HTTP methods to support. Defaults to ["GET", "POST"].

        Returns:
            Callable: Decorator function.

        Example:
            ```python
            @FC.endpoint(methods=["GET", "POST"])
            def api_handler(request):
                return {"status": "success", "data": request.json}
            ```
        """
        if methods is None:
            methods = ["GET", "POST"]

        def decorator(func: Callable) -> Callable:
            # Mark as endpoint
            func._fc_endpoint = True
            func._fc_endpoint_methods = methods

            return cls.function(func)

        return decorator
