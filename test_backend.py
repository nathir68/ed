import requests
import time

BASE_URL = "http://localhost:5000"

def test_server_running():
    print(f"Testing connection to {BASE_URL}...")
    try:
        response = requests.get(BASE_URL + "/")
        if response.status_code == 200:
            print("✅ Server is running and homepage is accessible.")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Please make sure your Flask app is running (python app.py).")
        return False

def test_endpoints():
    endpoints = [
        {"path": "/login", "name": "Login Page", "method": "GET"},
        {"path": "/signup/teacher", "name": "Teacher Signup", "method": "GET"},
        {"path": "/signup/student", "name": "Student Signup", "method": "GET"}
    ]
    
    for ep in endpoints:
        print(f"Testing {ep['name']} ({ep['path']})...")
        response = requests.request(ep['method'], BASE_URL + ep['path'])
        if response.status_code == 200:
            print(f"✅ {ep['name']} is working.")
        else:
            print(f"❌ {ep['name']} failed with status: {response.status_code}")

def run_all_tests():
    print("--- Starting Backend API Tests ---")
    if test_server_running():
        print("-" * 30)
        test_endpoints()
    print("--- Tests Completed ---")

if __name__ == "__main__":
    run_all_tests()
