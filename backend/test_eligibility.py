"""
Quick test script for eligibility engine.
Run this after starting the FastAPI server.

Usage:
    python test_eligibility.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_seed_data():
    """Test seeding demo schemes."""
    print("\n1. Seeding demo data...")
    response = requests.post(f"{BASE_URL}/schemes/seed-demo-data")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_get_schemes():
    """Test getting all schemes."""
    print("\n2. Getting all schemes...")
    response = requests.get(f"{BASE_URL}/schemes/")
    print(f"Status: {response.status_code}")
    schemes = response.json()
    print(f"Total schemes: {len(schemes)}")
    for scheme in schemes[:2]:  # Show first 2
        print(f"  - {scheme['name']} ({scheme['state']})")

def test_eligibility_check():
    """Test eligibility checking."""
    print("\n3. Testing eligibility check...")
    
    # Test profile: Karnataka student
    profile = {
        "name": "Rajesh Kumar",
        "state": "Karnataka",
        "age": 20,
        "gender": "Male",
        "occupation": "student",
        "annual_income": 300000
    }
    
    print(f"Profile: {profile['name']}, {profile['age']} years, {profile['occupation']}, Income: ₹{profile['annual_income']}")
    
    response = requests.post(f"{BASE_URL}/eligibility/check", json=profile)
    print(f"Status: {response.status_code}")
    
    result = response.json()
    print(f"\nSummary:")
    print(f"  Total schemes checked: {result['summary']['total_schemes_checked']}")
    print(f"  Eligible: {result['summary']['eligible_count']}")
    print(f"  Ineligible: {result['summary']['ineligible_count']}")
    
    print(f"\nEligible Schemes:")
    for item in result['eligible_schemes']:
        print(f"  ✓ {item['scheme']['name']}")
    
    print(f"\nIneligible Schemes:")
    for item in result['ineligible_schemes']:
        reasons = ", ".join(item['eligibility']['reasons'])
        print(f"  ✗ {item['scheme']['name']}")
        print(f"    Reason: {reasons}")

if __name__ == "__main__":
    try:
        test_seed_data()
        test_get_schemes()
        test_eligibility_check()
        print("\n✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server. Make sure FastAPI is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
