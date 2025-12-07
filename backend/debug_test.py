"""Debug test to see the actual error"""
import requests

response = requests.post(
    "http://localhost:8000/api/eligibility/check",
    json={
        "name": "Rajesh Kumar",
        "state": "Karnataka",
        "age": 20,
        "gender": "Male",
        "occupation": "student",
        "annual_income": 300000
    }
)

print(f"Status: {response.status_code}")
print(f"Response text: {response.text}")
