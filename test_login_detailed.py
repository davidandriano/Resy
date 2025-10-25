import requests
import json

email = "andrianodavid@gmail.com"
password = "TestPass123!"

url = "https://api.resy.com/3/auth/password"
api_key = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://resy.com",
    "Referer": "https://resy.com/",
    "Authorization": f'ResyAPI api_key="{api_key}"'
}

# Try different payload formats
print("="*60)
print("TEST 1: JSON payload with json parameter")
print("="*60)

payload1 = {"email": email, "password": password}
print(f"Payload: {payload1}")
print()

response1 = requests.post(url, json=payload1, headers=headers)
print(f"Status: {response1.status_code}")
print(f"Response: {response1.text}")
print()

print("="*60)
print("TEST 2: Form-encoded data")
print("="*60)

payload2 = {"email": email, "password": password}
print(f"Payload: {payload2}")
print()

headers2 = headers.copy()
headers2["Content-Type"] = "application/x-www-form-urlencoded"

response2 = requests.post(url, data=payload2, headers=headers2)
print(f"Status: {response2.status_code}")
print(f"Response: {response2.text}")
print()

print("="*60)
print("TEST 3: JSON with Content-Type application/json")
print("="*60)

payload3 = {"email": email, "password": password}
print(f"Payload: {payload3}")
print()

headers3 = headers.copy()
headers3["Content-Type"] = "application/json"

response3 = requests.post(url, data=json.dumps(payload3), headers=headers3)
print(f"Status: {response3.status_code}")
print(f"Response: {response3.text}")
print()

# Check if any worked
if response1.status_code == 200:
    print("✓ TEST 1 WORKED!")
elif response2.status_code == 200:
    print("✓ TEST 2 WORKED!")
elif response3.status_code == 200:
    print("✓ TEST 3 WORKED!")
else:
    print("✗ ALL TESTS FAILED")
    print("\nThis might indicate:")
    print("1. The Resy API has changed")
    print("2. Your account has restrictions")
    print("3. Resy might be blocking automated logins")
