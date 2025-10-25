#!/usr/bin/env python3
"""
Debug script to see availability data and test booking details endpoint
"""
from datetime import date
from config import load_settings
from resy_client import ResyClient
import requests

settings = load_settings()
client = ResyClient(settings.resy_email, settings.resy_password)

print("Authenticating...")
if not client.login():
    print("Auth failed!")
    exit(1)

print("✓ Authenticated\n")

venue_id = 339
party_size = 2
reservation_date = date(2025, 10, 31)

print("="*60)
print("STEP 1: Getting availability")
print("="*60)

# Get venue location first
venue_url = f"{client.BASE_URL}/3/venue?id={venue_id}"
venue_response = client.session.get(venue_url)
venue_data = venue_response.json()

location = venue_data.get("location", {})
lat = location.get("latitude")
long = location.get("longitude")

print(f"Venue: {venue_data.get('name')}")
print(f"Location: {lat}, {long}\n")

# Find availability
find_url = f"{client.BASE_URL}/4/find"
params = {
    "venue_id": venue_id,
    "day": reservation_date.strftime("%Y-%m-%d"),
    "party_size": party_size,
    "lat": lat,
    "long": long
}

response = client.session.get(find_url, params=params)
print(f"Find Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()

    # Print the entire response to see structure
    import json
    print("\nFull find response:")
    print(json.dumps(data, indent=2)[:2000])  # First 2000 chars

    venues = data.get("results", {}).get("venues", [])

    if venues:
        print(f"\n\nFound {len(venues)} venue(s)")

        for venue in venues:
            slots = venue.get("slots", [])
            print(f"\nVenue has {len(slots)} slots:")

            for i, slot in enumerate(slots[:3], 1):  # Show first 3 slots
                print(f"\n  Slot {i}:")
                print(f"    Config ID: {slot.get('config', {}).get('id')}")
                print(f"    Type: {slot.get('config', {}).get('type')}")
                print(f"    Token: {slot.get('config', {}).get('token')}")
                print(f"    Date start: {slot.get('date', {}).get('start')}")
                print(f"    Date end: {slot.get('date', {}).get('end')}")

                # Test the details endpoint with this slot
                config_id = slot.get('config', {}).get('id')

                if config_id:
                    print(f"\n    Testing details endpoint for config {config_id}...")

                    # Try different combinations
                    print("\n    Test 1: Basic params")
                    details_url = f"{client.BASE_URL}/3/details"
                    details_params = {
                        "config_id": config_id,
                        "day": reservation_date.strftime("%Y-%m-%d"),
                        "party_size": party_size
                    }

                    details_response = client.session.get(details_url, params=details_params)
                    print(f"      Status: {details_response.status_code}")
                    print(f"      Response: {details_response.text[:500]}")

                    # Try with commit_id from the config token
                    config_token = slot.get('config', {}).get('token')
                    if config_token:
                        print("\n    Test 2: Using commit=1 param")
                        details_params2 = {
                            "commit": "1",
                            "config_id": config_token,
                            "day": reservation_date.strftime("%Y-%m-%d"),
                            "party_size": party_size
                        }

                        details_response2 = client.session.get(details_url, params=details_params2)
                        print(f"      Status: {details_response2.status_code}")
                        print(f"      Response: {details_response2.text[:500]}")

                    break  # Just test first slot

else:
    print(f"Error: {response.text}")

print("\n" + "="*60)
