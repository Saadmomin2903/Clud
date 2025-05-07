"""
URL manager for the Function Cloud (FC) library.
"""

import inspect
import hashlib
from typing import Callable

from function_cloud.config import FCConfig


class FCURLManager:
    """Manages function URLs."""

    @staticmethod
    def generate_url_path(func: Callable) -> str:
        """
        Generate a unique URL path for a function.

        Args:
            func (Callable): The function to generate a URL path for.

        Returns:
            str: The URL path.
        """
        # Get function name and module with fallbacks
        try:
            name = func.__name__
        except (AttributeError, TypeError):
            # If function doesn't have __name__, use a generic name
            name = "function"

        try:
            module = func.__module__
        except (AttributeError, TypeError):
            # If function doesn't have __module__, use a generic module name
            module = "playground"

        # Try to get the source code, but handle potential errors
        try:
            source = inspect.getsource(func)
            source_hash = hashlib.md5(source.encode()).hexdigest()[:8]
        except (OSError, TypeError, IOError, AttributeError):
            # If we can't get the source code, use a timestamp-based hash instead
            import time
            import random
            # Add some randomness to ensure uniqueness
            random_str = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            timestamp = str(time.time())
            source_hash = hashlib.md5(f"{timestamp}_{random_str}".encode()).hexdigest()[:8]

        return f"{module}.{name}-{source_hash}"

    @staticmethod
    def function_to_endpoint(func_path: str) -> str:
        """
        Convert a function path to a Modal endpoint URL.

        Args:
            func_path (str): The function path.

        Returns:
            str: The Modal endpoint URL.
        """
        base_url = f"https://{FCConfig.stub_name}--{func_path.replace('.', '-')}.modal.run"
        return base_url
