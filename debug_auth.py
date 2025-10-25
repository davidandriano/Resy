#!/usr/bin/env python3
"""
Debug script to troubleshoot Resy authentication
"""
import os
from pathlib import Path

# Check if .env file exists and read it manually
env_path = Path(".env")
print("="*60)
print("DEBUGGING RESY AUTHENTICATION")
print("="*60)
print()

print("Step 1: Checking .env file...")
print(f".env file exists: {env_path.exists()}")
print()

if env_path.exists():
    print("Step 2: Reading .env file contents...")
    with open(".env", "r", encoding="utf-8") as f:
        lines = f.readlines()

    email = None
    password = None

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line.startswith("RESY_EMAIL="):
            email = line.split("=", 1)[1].strip()
            print(f"Line {i}: Found RESY_EMAIL")
            print(f"  Value: {email}")
            print(f"  Length: {len(email)} characters")
            print(f"  Has quotes: {email.startswith(('\"', \"'\")) or email.endswith(('\"', \"'\"))}")

        elif line.startswith("RESY_PASSWORD="):
            password = line.split("=", 1)[1].strip()
            print(f"Line {i}: Found RESY_PASSWORD")
            print(f"  Value: {'*' * len(password)} (hidden for security)")
            print(f"  Length: {len(password)} characters")
            print(f"  Has quotes: {password.startswith(('\"', \"'\")) or password.endswith(('\"', \"'\"))}")
            print(f"  First char: {repr(password[0]) if password else 'N/A'}")
            print(f"  Last char: {repr(password[-1]) if password else 'N/A'}")

    print()
    print("Step 3: Testing with pydantic-settings (how the bot reads it)...")

    try:
        from config import load_settings
        settings = load_settings()
        print(f"Email from settings: {settings.resy_email}")
        print(f"Email length: {len(settings.resy_email)}")
        print(f"Password length: {len(settings.resy_password)}")
        print(f"Password first char: {repr(settings.resy_password[0])}")
        print(f"Password last char: {repr(settings.resy_password[-1])}")
        print()

        print("Step 4: Testing Resy API call with detailed error info...")
        import requests
        import json

        url = "https://api.resy.com/3/auth/password"
        api_key = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f'ResyAPI api_key="{api_key}"'
        }

        payload = {
            "email": settings.resy_email,
            "password": settings.resy_password
        }

        print(f"Making API call to: {url}")
        print(f"Email being sent: {settings.resy_email}")
        print(f"Password length being sent: {len(settings.resy_password)} characters")
        print()

        response = requests.post(url, json=payload, headers=headers)

        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print()

        if response.status_code == 200:
            print("✓ SUCCESS! Authentication worked!")
            data = response.json()
            print(f"Received auth token: {data.get('token', 'N/A')[:20]}...")
        else:
            print("✗ FAILED!")
            print(f"Response body: {response.text}")
            print()

            # Try to parse error message
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error response as JSON")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

print()
print("="*60)
print("If you see issues above, we can fix them!")
print("="*60)
