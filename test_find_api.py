#!/usr/bin/env python3
"""
Debug script to test the find availability endpoint
"""
import requests
from config import load_settings

settings = load_settings()

# First, authenticate to get a token
auth_url = "https://api.resy.com/3/auth/password"
api_key = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f'ResyAPI api_key="{api_key}"'
}

payload = {
    "email": settings.resy_email,
    "password": settings.resy_password
}

print("Authenticating...")
auth_response = requests.post(auth_url, data=payload, headers=headers)
print(f"Auth Status: {auth_response.status_code}")

if auth_response.status_code != 200:
    print("Auth failed!")
    exit(1)

auth_data = auth_response.json()
auth_token = auth_data.get("token")
print(f"✓ Authenticated\n")

# Now try to find availability with different parameter combinations
venue_id = 339
day = "2025-10-31"
party_size = 2

print("="*60)
print("TEST 1: Basic /4/find request")
print("="*60)

find_headers = headers.copy()
find_headers["X-Resy-Auth-Token"] = auth_token

params1 = {
    "venue_id": venue_id,
    "day": day,
    "party_size": party_size
}

find_url = "https://api.resy.com/4/find"
response1 = requests.get(find_url, params=params1, headers=find_headers)

print(f"URL: {response1.url}")
print(f"Status: {response1.status_code}")
print(f"Response: {response1.text[:500]}")
print()

print("="*60)
print("TEST 2: Try /3/find instead")
print("="*60)

find_url2 = "https://api.resy.com/3/find"
response2 = requests.get(find_url2, params=params1, headers=find_headers)

print(f"URL: {response2.url}")
print(f"Status: {response2.status_code}")
print(f"Response: {response2.text[:500]}")
print()

print("="*60)
print("TEST 3: Add lat/long parameters")
print("="*60)

params3 = {
    "venue_id": venue_id,
    "day": day,
    "party_size": party_size,
    "lat": "37.7749",
    "long": "-122.4194"
}

response3 = requests.get(find_url, params=params3, headers=find_headers)

print(f"URL: {response3.url}")
print(f"Status: {response3.status_code}")
print(f"Response: {response3.text[:500]}")
print()

print("="*60)
print("TEST 4: Try with venue info first")
print("="*60)

venue_url = f"https://api.resy.com/3/venue?id={venue_id}"
venue_response = requests.get(venue_url, headers=find_headers)

print(f"Venue Status: {venue_response.status_code}")

if venue_response.status_code == 200:
    venue_data = venue_response.json()
    print(f"Venue Name: {venue_data.get('name')}")
    print(f"Venue Location: {venue_data.get('location', {}).get('neighborhood')}")

    # Try find again with venue location data
    location = venue_data.get("location", {})
    params4 = {
        "venue_id": venue_id,
        "day": day,
        "party_size": party_size,
        "lat": location.get("latitude"),
        "long": location.get("longitude")
    }

    response4 = requests.get(find_url, params=params4, headers=find_headers)
    print(f"\nFind with venue lat/long:")
    print(f"Status: {response4.status_code}")
    print(f"Response: {response4.text[:500]}")
else:
    print(f"Could not get venue info: {venue_response.text[:200]}")

print()
print("="*60)
print("SUMMARY")
print("="*60)
print(f"Test 1 (/4/find basic): {response1.status_code}")
print(f"Test 2 (/3/find): {response2.status_code}")
print(f"Test 3 (/4/find with lat/long): {response3.status_code}")
if venue_response.status_code == 200:
    print(f"Test 4 (/4/find with venue lat/long): {response4.status_code}")
