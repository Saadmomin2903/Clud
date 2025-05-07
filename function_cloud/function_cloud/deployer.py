"""
Deployer for the Function Cloud (FC) library.
"""

import hashlib
from functools import wraps
from typing import Callable, Dict, Any

from function_cloud.config import FCConfig
from function_cloud.url_manager import FCURLManager

# Import Modal
try:
    import modal
    from modal import Image, Stub, web_endpoint, asgi_app, Secret
    HAS_MODAL = True
except ImportError:
    HAS_MODAL = False
    # Create mock classes for type hints
    class Image:
        pass
    class Stub:
        pass
    web_endpoint = lambda *args, **kwargs: lambda f: f
    asgi_app = lambda *args, **kwargs: lambda f: f
    class Secret:
        @staticmethod
        def from_name(name):
            pass


class FCDeployer:
    """Handles deployment to Modal."""

    @staticmethod
    def create_modal_function(func: Callable, dependencies: Dict[str, Any]) -> Callable:
        """
        Create a Modal-compatible function wrapper.

        Args:
            func (Callable): The function to wrap.
            dependencies (Dict[str, Any]): The dependencies to include.

        Returns:
            Callable: The Modal-compatible function.
        """
        if not HAS_MODAL:
            raise ImportError("Modal is required for deployment. Install it with 'pip install modal'.")

        # Create image with dependencies
        packages = dependencies.get("packages", [])
        system_deps = dependencies.get("system_dependencies", [])
        python_version = dependencies.get("python_version", "3.10")

        # Ensure packages list only contains strings
        valid_packages = []
        for pkg in packages:
            if pkg is not None:
                try:
                    valid_packages.append(str(pkg))
                except Exception as e:
                    print(f"Warning: Could not convert package to string: {pkg}, Error: {e}")

        print(f"Installing packages: {valid_packages}")

        image = modal.Image.debian_slim(python_version=python_version)

        if valid_packages:
            image = image.pip_install(valid_packages)

        # Ensure system_deps list only contains strings
        valid_system_deps = []
        for dep in system_deps:
            if dep is not None:
                try:
                    valid_system_deps.append(str(dep))
                except Exception as e:
                    print(f"Warning: Could not convert system dependency to string: {dep}, Error: {e}")

        print(f"Installing system dependencies: {valid_system_deps}")

        if valid_system_deps:
            image = image.apt_install(valid_system_deps)

        # Create a stub for this function
        stub_name = f"{FCConfig.stub_name}_{func.__name__}"
        stub = modal.Stub(stub_name)

        # Define the Modal function
        @stub.function(
            image=image,
            timeout=FCConfig.timeout,
            memory=FCConfig.memory,
            cpu=FCConfig.cpu,
            secrets=[Secret.from_name("fc_token") if FCConfig.token else None]
        )
        @wraps(func)
        def modal_func(*args, **kwargs):
            return func(*args, **kwargs)

        # Make it a web endpoint if it's meant to be an API
        if hasattr(func, "_fc_endpoint"):
            methods = getattr(func, "_fc_endpoint_methods", ["GET", "POST"])

            @stub.function(image=image)
            @web_endpoint(methods=methods)
            def endpoint_func(request):
                # Parse request body based on content type
                if request.method == "GET":
                    kwargs = dict(request.query_params)
                else:
                    content_type = request.headers.get("content-type", "")
                    if "application/json" in content_type:
                        kwargs = request.json()
                    elif "application/x-www-form-urlencoded" in content_type:
                        kwargs = dict(request.form())
                    else:
                        kwargs = {}

                # Call the original function
                result = func(**kwargs)

                # Return JSON response
                return {"result": result}

            return endpoint_func

        return modal_func

    @staticmethod
    def deploy_function(modal_func: Callable) -> str:
        """
        Deploy a function to Modal and return its URL.

        Args:
            modal_func (Callable): The Modal function to deploy.

        Returns:
            str: The URL of the deployed function.
        """
        # This would actually deploy to Modal
        # For this example, we're just returning a mock URL

        try:
            # Handle the case where modal_func doesn't have __wrapped__ attribute
            if hasattr(modal_func, '__wrapped__'):
                # Normal case - function was wrapped with functools.wraps
                original_func = modal_func.__wrapped__
                func_path = FCURLManager.generate_url_path(original_func)
                url = FCURLManager.function_to_endpoint(func_path)

                # Store URL on the original function
                try:
                    original_func._fc_url = url
                except (AttributeError, TypeError):
                    # If we can't set the attribute, just continue
                    pass
            else:
                # Fallback case - function doesn't have __wrapped__ attribute
                # This happens in the playground environment
                func_path = FCURLManager.generate_url_path(modal_func)
                url = FCURLManager.function_to_endpoint(func_path)

                # Store URL directly on the function
                try:
                    modal_func._fc_url = url
                except (AttributeError, TypeError):
                    # If we can't set the attribute, just continue
                    pass
        except Exception as e:
            # If anything goes wrong, generate a generic URL
            import time
            import random
            timestamp = str(time.time())
            random_str = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            hash_value = hashlib.md5(f"{timestamp}_{random_str}".encode()).hexdigest()[:8]
            func_path = f"playground.function-{hash_value}"
            url = FCURLManager.function_to_endpoint(func_path)

            # Log the error
            print(f"Warning: Error generating URL path: {e}")
            print(f"Using generic URL: {url}")

        return url
