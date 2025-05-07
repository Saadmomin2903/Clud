#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from function_cloud.web import create_app

# Load environment variables from .env file if it exists
load_dotenv()

# Set development environment variables
os.environ["FLASK_ENV"] = "development"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Generate a random secret key if not provided
if not os.environ.get("FC_SECRET_KEY"):
    os.environ["FC_SECRET_KEY"] = os.urandom(24).hex()

# Verify Groq API key
print("\n=== Verifying Groq API Key ===")
print(f"GROQ_API_KEY environment variable: {os.environ.get('GROQ_API_KEY')[:10]}...")

try:
    import groq
    client = groq.Client(api_key=os.environ.get("GROQ_API_KEY"))
    print("Testing Groq API connection...")
    # Simple test request
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # Using a smaller model for testing
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        max_tokens=10
    )
    print(f"Groq API test successful! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error testing Groq API: {e}")
    import traceback
    print(f"Detailed error: {traceback.format_exc()}")
print("==============================\n")

# Create and run app
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
