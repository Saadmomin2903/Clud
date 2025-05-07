# Example 1: Basic Function Deployment
from fc import FC

# Configure with your Modal token
FC.configure(token="your_modal_token")

# Simple function example
@FC.function
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Use it locally first
result = calculate_fibonacci(10)
print(f"Fibonacci(10) = {result}")

# Get the cloud URL
url = calculate_fibonacci.get_url()
print(f"Function URL: {url}")

# Call it via HTTP (uncomment to use)
# import requests
# response = requests.get(url, params={"n": 10})
# print(f"Remote result: {response.json()['result']}")


# Example 2: Class with State
class DataProcessor:
    def __init__(self):
        self.processed_count = 0
    
    @FC.method
    def process_text(self, text: str) -> dict:
        """Process text and keep count of processed items."""
        result = text.upper()
        self.processed_count += 1
        return {
            "result": result,
            "processed_count": self.processed_count
        }

# Create an instance and use it
processor = DataProcessor()
print(processor.process_text("hello world"))

# Get the cloud URL for the method
method_url = processor.process_text.get_url()
print(f"Method URL: {method_url}")


# Example 3: API Endpoint
@FC.endpoint(methods=["GET", "POST"])
def user_api(user_id: str = None, action: str = "get") -> dict:
    """A simple API endpoint for user operations."""
    if action == "get":
        # In a real app, this would fetch from a database
        return {"user_id": user_id, "name": f"User {user_id}", "status": "active"}
    elif action == "update":
        return {"user_id": user_id, "status": "updated"}
    else:
        return {"error": "Invalid action"}

# Get the API URL
api_url = user_api.get_url()
print(f"API URL: {api_url}")


# Example 4: Async Function
import asyncio

@FC.function
async def fetch_data(urls: list) -> list:
    """Fetch data from multiple URLs asynchronously."""
    import aiohttp
    
    async def get_url(session, url):
        async with session.get(url) as response:
            return await response.text()
    
    async with aiohttp.ClientSession() as session:
        tasks = [get_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# Use it locally with asyncio
urls = ["https://example.com", "https://example.org"]
result = asyncio.run(fetch_data(urls))
print(f"Fetched {len(result)} pages")

# Get the cloud URL
async_url = fetch_data.get_url()
print(f"Async Function URL: {async_url}")


# Example 5: Machine Learning Function
@FC.function
def train_model(data_url: str, features: list, target: str) -> dict:
    """Train a machine learning model."""
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    
    # Download data
    df = pd.read_csv(data_url)
    
    # Prepare data
    X = df[features]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Train model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    return {
        "accuracy": accuracy,
        "feature_importance": dict(zip(features, model.feature_importances_.tolist())),
        "model_params": model.get_params()
    }

# Get the URL (would need actual data to run locally)
ml_url = train_model.get_url()
print(f"ML Function URL: {ml_url}")


# Example 6: Integration with External Services
@FC.function
def send_notification(email: str, message: str) -> dict:
    """Send an email notification."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # This would typically use environment variables or secrets
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_user = "notifications@example.com"
    smtp_password = "password"  # Would use FC.secrets in real implementation
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = email
    msg['Subject'] = "Notification from FC"
    msg.attach(MIMEText(message, 'plain'))
    
    # Connect and send
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return {"status": "sent", "recipient": email}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Get URL
notification_url = send_notification.get_url()
print(f"Notification URL: {notification_url}")


# Example 7: Scheduled Function
@FC.function
def daily_report() -> dict:
    """Generate a daily report."""
    import datetime
    
    today = datetime.datetime.now()
    
    # This would typically connect to a database or other data source
    report = {
        "date": today.strftime("%Y-%m-%d"),
        "metrics": {
            "users": 1250,
            "transactions": 522,
            "revenue": 12435.50
        },
        "status": "generated"
    }
    
    return report

# Get URL (can be triggered by a scheduler)
report_url = daily_report.get_url()
print(f"Report URL: {report_url}")


# Example 8: Complex Web API with Authentication
@FC.endpoint(methods=["GET", "POST", "PUT", "DELETE"])
def crud_api(request_data: dict) -> dict:
    """A CRUD API with authentication."""
    # Extract auth token from request
    auth_token = request_data.get("auth_token")
    
    # Validate token (simplified)
    if auth_token != "valid_token":
        return {"error": "Unauthorized", "code": 401}
    
    # Get action and resource
    action = request_data.get("action", "read")
    resource_type = request_data.get("resource_type", "item")
    resource_id = request_data.get("resource_id")
    
    # Handle different CRUD operations
    if action == "create":
        # Create new resource
        return {"status": "created", "id": "new_id_123"}
    elif action == "read":
        # Get resource
        if resource_id:
            return {"id": resource_id, "name": f"Resource {resource_id}", "status": "active"}
        else:
            return {"items": [{"id": "1", "name": "Item 1"}, {"id": "2", "name": "Item 2"}]}
    elif action == "update":
        # Update resource
        return {"id": resource_id, "status": "updated"}
    elif action == "delete":
        # Delete resource
        return {"id": resource_id, "status": "deleted"}
    else:
        return {"error": "Invalid action"}

# Get API URL
crud_url = crud_api.get_url()
print(f"CRUD API URL: {crud_url}")
