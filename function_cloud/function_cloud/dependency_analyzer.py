"""
Dependency analyzer for the Function Cloud (FC) library.
"""

import inspect
import ast
import json
import os
from typing import Callable, Set, Dict, Any

from function_cloud.config import FCConfig

# Optional import for Groq LLM integration
try:
    import groq
    HAS_GROQ = True
    print("Groq package is installed")
except ImportError:
    HAS_GROQ = False
    print("Groq package is not installed. Install with 'pip install groq'")

# Import traceback for detailed error reporting
import traceback


class DependencyAnalyzer:
    """Analyzes function dependencies using static analysis and LLM."""

    @staticmethod
    def analyze_imports(func: Callable) -> Set[str]:
        """
        Extract import statements from function source code.

        Args:
            func (Callable): The function to analyze.

        Returns:
            Set[str]: Set of imported module names.
        """
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
    def enhance_with_llm(func: Callable, imports: Set[str]) -> Dict[str, Any]:
        """
        Use Groq LLM to enhance dependency detection and generate requirements.

        Args:
            func (Callable): The function to analyze.
            imports (Set[str]): Set of imported module names.

        Returns:
            Dict[str, Any]: Dictionary with dependency information.
        """
        # Debug information
        print("\n=== LLM Dependency Analysis Debug ===")
        print(f"LLM enabled: {FCConfig.llm_enabled}")
        print(f"LLM provider: {FCConfig.llm_provider}")
        print(f"Has Groq: {HAS_GROQ}")
        print(f"API key set: {bool(FCConfig.llm_api_key)}")
        print(f"API key (first 10 chars): {FCConfig.llm_api_key[:10] if FCConfig.llm_api_key else 'None'}")
        print("=======================================\n")

        if not FCConfig.llm_enabled:
            print("LLM analysis skipped: LLM is not enabled")
            return {"packages": list(imports)}

        source = inspect.getsource(func)
        func_name = func.__name__
        module_name = func.__module__

        if not FCConfig.llm_api_key:
            print("LLM analysis skipped: No API key provided")
            return {"packages": list(imports)}

        # Use Groq for dependency analysis
        if FCConfig.llm_provider == "groq" and HAS_GROQ:
            print("Creating Groq client with API key...")
            try:
                # Try to use the environment variable directly first
                if os.environ.get("GROQ_API_KEY"):
                    api_key = os.environ.get("GROQ_API_KEY")
                    print(f"Using Groq API key from environment: {api_key[:10]}...")
                else:
                    # Fall back to the config
                    api_key = FCConfig.llm_api_key
                    print(f"Using Groq API key from config: {api_key[:10]}...")

                # Force update the class variable to ensure consistency
                FCConfig.GROQ_API_KEY = api_key
                FCConfig.llm_api_key = api_key

                client = groq.Client(api_key=api_key)
                print("Groq client created successfully")
            except Exception as e:
                print(f"Error creating Groq client: {e}")
                return {"packages": list(imports)}

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

            print("Sending request to Groq API...")
            try:
                # Use a smaller model that's more likely to be available
                print(f"Using model: llama3-8b-8192")
                response = client.chat.completions.create(
                    model="llama3-8b-8192",  # Using Llama 3 8B model (more widely available)
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                print("Received response from Groq API")
                result_text = response.choices[0].message.content
                # Extract JSON from the response
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result_text[json_start:json_end]
                    print(f"Extracted JSON: {json_str}")
                    result = json.loads(json_str)
                    print("JSON parsed successfully")

                    # Ensure packages list only contains strings
                    if "packages" in result and isinstance(result["packages"], list):
                        # Convert all items to strings and filter out None values
                        result["packages"] = [str(pkg) for pkg in result["packages"] if pkg is not None]
                        print(f"Sanitized packages list: {result['packages']}")
                    else:
                        # If no packages or invalid format, use the imports
                        result["packages"] = list(map(str, imports))
                        print(f"Using imports as packages: {result['packages']}")

                    return result
                else:
                    print("Could not extract JSON from response")
                    # Ensure imports are converted to strings
                    packages = [str(pkg) for pkg in imports if pkg is not None]
                    print(f"Using imports as packages: {packages}")
                    return {"packages": packages}
            except Exception as e:
                print(f"LLM analysis failed: {str(e)}")
                # Print more detailed error information
                import traceback
                print(f"Detailed error: {traceback.format_exc()}")
                # Ensure imports are converted to strings
                packages = [str(pkg) for pkg in imports if pkg is not None]
                print(f"Using imports as packages after error: {packages}")
                return {"packages": packages}
        else:
            if not HAS_GROQ:
                print("LLM analysis skipped: Groq is not installed. Install with 'pip install groq'")
            else:
                print(f"LLM analysis skipped: Provider {FCConfig.llm_provider} is not supported or not configured")
            # Fallback to basic dependency analysis with string conversion
            packages = [str(pkg) for pkg in imports if pkg is not None]
            print(f"Using imports as packages (fallback): {packages}")
            return {"packages": packages}
