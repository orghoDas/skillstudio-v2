import requests
import json

# Test registration
url = "http://127.0.0.1:8000/api/v1/auth/register"
data = {
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
}

print(f"Testing POST {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
