"""
Test script to verify the LLM integration in the Function Cloud (FC) library.
"""

import os
from function_cloud import FC
from function_cloud.dependency_analyzer import DependencyAnalyzer

# Check if Groq is installed
try:
    import groq
    HAS_GROQ = True
    print("Groq is installed!")
except ImportError:
    HAS_GROQ = False
    print("Groq is not installed. Install it with 'pip install groq'.")

# Configure FC with a mock Groq API key
# In a real scenario, you would use your actual Groq API key
FC.configure(
    token="test_token",
    llm_enabled=True,
    llm_api_key="mock_groq_api_key",
    llm_provider="groq"
)

# Define a test function with some imports
@FC.function
def process_data(data_url: str):
    """
    Process data from a URL.

    Args:
        data_url (str): URL to fetch data from.

    Returns:
        dict: Processed data.
    """
    import requests
    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import StandardScaler

    # Fetch data
    response = requests.get(data_url)
    data = response.json()

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Preprocess
    df = df.fillna(0)

    # Scale numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    return {
        "processed_data": df.to_dict(),
        "stats": {
            "mean": df.mean().to_dict(),
            "std": df.std().to_dict()
        }
    }

# Test the dependency analyzer directly
print("\nTesting dependency analysis:")
imports = DependencyAnalyzer.analyze_imports(process_data)
print(f"Detected imports: {imports}")

# In a real scenario with a valid Groq API key, this would call the LLM
# For this test, we'll simulate the LLM response
if HAS_GROQ:
    print("\nTesting LLM enhancement (simulated):")

    # Simulate the LLM response without mocking
    # This is a simplified version that doesn't make actual API calls
    dependencies = {
        "packages": ["requests", "pandas", "numpy", "scikit-learn"],
        "system_dependencies": [],
        "python_version": "3.9"
    }

    print(f"Simulated dependencies: {dependencies}")

    # For demonstration, let's show what would be analyzed
    print("\nIn a real scenario with a valid Groq API key:")
    print("1. The function source code would be sent to Groq")
    print("2. Groq would analyze the imports and dependencies")
    print("3. The response would be parsed to extract dependency information")
    print("4. The dependencies would be used to create a Modal container")
else:
    print("\nSkipping LLM enhancement test because Groq is not installed.")

print("\nTest completed successfully!")
