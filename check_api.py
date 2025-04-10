#!/usr/bin/env C:\Users\bened\AppData\Local\Programs\Python\Python313\python.exe
import requests
import sys

def check_api(url):
    """Simple function to check if API is running"""
    try:
        print(f"Checking API at {url}...")
        response = requests.get(f"{url}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ API is running!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error checking API: {e}")
        return False

if __name__ == "__main__":
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = check_api(api_url)
    sys.exit(0 if success else 1) 