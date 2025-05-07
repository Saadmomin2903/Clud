"""
Comprehensive example of using Function Cloud (FC) with all its features.
"""

import os
from function_cloud import FC

# Configure FC with your Modal token and Groq API key
# In a real scenario, you would use environment variables or a config file
FC.configure(
    token=os.environ.get("MODAL_TOKEN", "your_modal_token"),
    llm_enabled=True,
    llm_api_key=os.environ.get("GROQ_API_KEY", "your_groq_api_key"),
    llm_provider="groq",
    memory=2048,  # 2GB of memory
    cpu=2,        # 2 CPUs
    timeout=300   # 5 minutes timeout
)

# Example 1: Basic Function
@FC.function
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Example 2: Function with Dependencies
@FC.function
def analyze_data(data_url: str):
    """
    Analyze data from a URL.

    This function demonstrates automatic dependency detection.
    FC will detect that it needs pandas, numpy, and matplotlib.
    """
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64

    # Download data
    df = pd.read_csv(data_url)

    # Perform analysis
    stats = {
        "mean": df.mean().to_dict(),
        "median": df.median().to_dict(),
        "std": df.std().to_dict(),
        "min": df.min().to_dict(),
        "max": df.max().to_dict()
    }

    # Create a plot
    plt.figure(figsize=(10, 6))
    for column in df.select_dtypes(include=[np.number]).columns:
        plt.plot(df.index, df[column], label=column)
    plt.legend()
    plt.title("Data Visualization")

    # Convert plot to base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    return {
        "stats": stats,
        "plot": plot_data
    }

# Example 3: Class with State
class DataProcessor:
    def __init__(self):
        self.processed_count = 0
        self.last_result = None

    @FC.method
    def process_text(self, text: str) -> dict:
        """Process text and keep count of processed items."""
        # Simple processing: uppercase and word count
        result = text.upper()
        word_count = len(text.split())

        # Update state
        self.processed_count += 1
        self.last_result = result

        return {
            "original": text,
            "processed": result,
            "word_count": word_count,
            "processed_count": self.processed_count,
            "last_result": self.last_result
        }

# Example 4: API Endpoint
@FC.endpoint(methods=["GET", "POST"])
def api_handler(name: str = None, action: str = "greet") -> dict:
    """A simple API endpoint."""
    if action == "greet":
        return {"message": f"Hello, {name or 'World'}!"}
    elif action == "echo":
        return {"echo": name}
    else:
        return {"error": "Invalid action"}

# Example 5: Async Function
@FC.function
async def fetch_multiple_urls(urls: list) -> list:
    """Fetch data from multiple URLs asynchronously."""
    import aiohttp
    import asyncio

    async def fetch_url(session, url):
        async with session.get(url) as response:
            return {
                "url": url,
                "status": response.status,
                "content": await response.text()
            }

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# Main execution
if __name__ == "__main__":
    # Example 1: Basic Function
    print("\n--- Example 1: Basic Function ---")
    result = calculate_fibonacci(10)
    print(f"Fibonacci(10) = {result}")
    print(f"Function URL: {calculate_fibonacci.get_url()}")

    # Example 2: Function with Dependencies
    print("\n--- Example 2: Function with Dependencies ---")
    # Call the function with a sample URL to trigger deployment
    try:
        # Using a mock URL - in a real scenario, use a real data URL
        analyze_data("https://example.com/data.csv")
    except Exception as e:
        print(f"Note: Function called to trigger deployment. Error: {e}")
    print(f"Function URL: {analyze_data.get_url()}")

    # Example 3: Class with State
    print("\n--- Example 3: Class with State ---")
    processor = DataProcessor()
    result = processor.process_text("Hello, Function Cloud!")
    print(f"Processed text: {result}")
    print(f"Method URL: {processor.process_text.get_url()}")

    # Example 4: API Endpoint
    print("\n--- Example 4: API Endpoint ---")
    result = api_handler(name="User", action="greet")
    print(f"API result: {result}")
    print(f"API URL: {api_handler.get_url()}")

    # Example 5: Async Function
    print("\n--- Example 5: Async Function ---")
    # Call the function with sample URLs to trigger deployment
    import asyncio
    try:
        # Using mock URLs - in a real scenario, use real URLs
        asyncio.run(fetch_multiple_urls(["https://example.com", "https://example.org"]))
    except Exception as e:
        print(f"Note: Function called to trigger deployment. Error: {e}")
    print(f"Async Function URL: {fetch_multiple_urls.get_url()}")

    print("\nAll examples completed successfully!")
