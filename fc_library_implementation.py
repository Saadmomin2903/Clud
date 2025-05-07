import inspect
import os
import sys
import ast
import json
import asyncio
import importlib
import hashlib
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar, Set, Tuple

import modal
import requests
from modal import Image, Stub, web_endpoint, asgi_app, Secret

# Optional import for LLM integration
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

T = TypeVar('T')

class FCConfig:
    """Configuration for the FC library."""
    token: str = None
    region: str = "us-east"
    memory: int = 1024
    timeout: int = 60
    cpu: int = 1
    llm_enabled: bool = True
    llm_api_key: str = None
    stub_name: str = "fc_app"
    
    @classmethod
    def validate(cls):
        if not cls.token:
            raise ValueError("FC token not configured. Call FC.configure(token='your_token') first.")

class DependencyAnalyzer:
    """Analyzes function dependencies using static analysis and LLM."""
    
    @staticmethod
    def analyze_imports(func: Callable) -> Set[str]:
        """Extract import statements from function source code."""
        source = inspect.getsource(func)
        parsed = ast.parse(source)
        imports = set()
        
        for node in ast.walk(parsed):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        return imports
    
    @staticmethod
    def enhance_with_llm(func: Callable, imports: Set[str]) -> Dict[str, str]:
        """Use LLM to enhance dependency detection and generate requirements."""
        if not FCConfig.llm_enabled or not HAS_OPENAI:
            return {"packages": list(imports)}
            
        source = inspect.getsource(func)
        func_name = func.__name__
        module_name = func.__module__
        
        if not FCConfig.llm_api_key:
            return {"packages": list(imports)}
            
        openai.api_key = FCConfig.llm_api_key
        
        prompt = f"""
        I have a Python function that I want to deploy to the cloud.
        Please analyze its dependencies and generate a requirements.txt file.
        
        Function name: {func_name}
        Module: {module_name}
        Identified imports: {', '.join(imports)}
        
        Function source:
        ```python
        {source}
        ```
        
        Generate a JSON response with these fields:
        1. "packages": List of required pip packages with versions
        2. "system_dependencies": List of system packages needed
        3. "python_version": Recommended Python version
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return {"packages": list(imports)}

class FCURLManager:
    """Manages function URLs."""
    
    @staticmethod
    def generate_url_path(func: Callable) -> str:
        """Generate a unique URL path for a function."""
        module = func.__module__
        name = func.__name__
        source = inspect.getsource(func)
        source_hash = hashlib.md5(source.encode()).hexdigest()[:8]
        return f"{module}.{name}-{source_hash}"
    
    @staticmethod
    def function_to_endpoint(func_path: str) -> str:
        """Convert a function path to a Modal endpoint URL."""
        base_url = f"https://{FCConfig.stub_name}--{func_path.replace('.', '-')}.modal.run"
        return base_url

class FCDeployer:
    """Handles deployment to Modal."""
    
    @staticmethod
    def create_modal_function(func: Callable, dependencies: Dict[str, Any]) -> Callable:
        """Create a Modal-compatible function wrapper."""
        # Create image with dependencies
        packages = dependencies.get("packages", [])
        system_deps = dependencies.get("system_dependencies", [])
        python_version = dependencies.get("python_version", "3.10")
        
        image = modal.Image.debian_slim(python_version=python_version)
        
        if packages:
            image = image.pip_install(packages)
        
        if system_deps:
            image = image.apt_install(system_deps)
        
        # Create a stub for this function
        stub_name = f"{FCConfig.stub_name}_{func.__name__}"
        stub = modal.Stub(stub_name)
        
        # Define the Modal function
        @stub.function(image=image, timeout=FCConfig.timeout, memory=FCConfig.memory, cpu=FCConfig.cpu, secrets=[Secret.from_name("fc_token") if FCConfig.token else None])
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
        """Deploy a function to Modal and return its URL."""
        # This would actually deploy to Modal
        # For this example, we're just returning a mock URL
        func_path = FCURLManager.generate_url_path(modal_func.__wrapped__)
        url = FCURLManager.function_to_endpoint(func_path)
        
        # Store URL on the original function
        modal_func.__wrapped__._fc_url = url
        
        return url

class FC:
    """Main Function Cloud class."""
    
    @classmethod
    def configure(cls, token: str = None, **kwargs):
        """Configure the FC library."""
        if token:
            FCConfig.token = token
            
        for key, value in kwargs.items():
            if hasattr(FCConfig, key):
                setattr(FCConfig, key, value)
    
    @classmethod
    def function(cls, func: Callable) -> Callable:
        """Decorator to deploy a function to Modal."""
        FCConfig.validate()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # If this is the first call, deploy to Modal
            if not hasattr(func, "_fc_deployed") or not func._fc_deployed:
                # Analyze dependencies
                imports = DependencyAnalyzer.analyze_imports(func)
                dependencies = DependencyAnalyzer.enhance_with_llm(func, imports)
                
                # Create Modal function
                modal_func = FCDeployer.create_modal_function(func, dependencies)
                
                # Deploy function
                url = FCDeployer.deploy_function(modal_func)
                
                # Mark as deployed
                func._fc_deployed = True
                func._fc_url = url
                func._fc_modal_func = modal_func
            
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
        """Decorator for class methods."""
        return cls.function(method)
    
    @classmethod
    def endpoint(cls, methods=None):
        """Decorator for API endpoints."""
        if methods is None:
            methods = ["GET", "POST"]
            
        def decorator(func: Callable) -> Callable:
            # Mark as endpoint
            func._fc_endpoint = True
            func._fc_endpoint_methods = methods
            
            return cls.function(func)
        
        return decorator


# Example usage
if __name__ == "__main__":
    # Configure FC
    FC.configure(token="example_token", llm_enabled=True)
    
    # Example function
    @FC.function
    def add(x: int, y: int) -> int:
        """Add two numbers."""
        return x + y
    
    # Example class method
    class TextProcessor:
        @FC.method
        def process(self, text: str) -> str:
            """Process text."""
            return text.upper()
    
    # Example API endpoint
    @FC.endpoint(methods=["GET", "POST"])
    def greet(name: str) -> Dict[str, str]:
        """Greet someone."""
        return {"message": f"Hello, {name}!"}
    
    # Trigger deployment
    result = add(1, 2)
    print(f"Local result: {result}")
    
    # Get URL
    url = add.get_url()
    print(f"Function URL: {url}")
    
    # Example of how to call the function via HTTP
    # response = requests.post(url, json={"x": 1, "y": 2})
    # print(f"Remote result: {response.json()}")
