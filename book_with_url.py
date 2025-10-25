#!/usr/bin/env python3
"""
Book a reservation using Resy venue URL

This script extracts the venue information from a Resy URL and books directly.
Useful when the search API isn't working.
"""
from datetime import date
import re
import requests
from bot import ResyBot
from config import ReservationConfig, load_settings
from notifications import setup_logging

# Setup logging
setup_logging()

# Load settings from .env
settings = load_settings()

# Create bot
bot = ResyBot(settings)

# PASTE YOUR RESY URL HERE:
# Example: https://resy.com/cities/san-francisco-ca/venues/izakaya-rintaro?date=2025-10-31&seats=2
resy_url = "https://resy.com/cities/san-francisco-ca/venues/izakaya-rintaro?date=2025-10-31&seats=2"

# Extract venue slug from URL
match = re.search(r'/venues/([^?]+)', resy_url)
if not match:
    print("Error: Could not extract venue from URL")
    exit(1)

venue_slug = match.group(1)
print(f"Venue slug: {venue_slug}")

# Try to get venue ID by accessing the venue page
print(f"\nFetching venue information from Resy...")

# Method 1: Try the venue details endpoint
try:
    # Access venue page to get ID
    venue_url = f"https://api.resy.com/3/venue?url_slug={venue_slug}&location=sf"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Authorization": f'ResyAPI api_key="{bot.client.API_KEY}"'
    }

    response = requests.get(venue_url, headers=headers)
    response.raise_for_status()

    data = response.json()
    venue_id = data.get("id", {}).get("resy")
    venue_name = data.get("name")

    if not venue_id:
        print("Error: Could not find venue ID")
        exit(1)

    print(f"✓ Found: {venue_name} (ID: {venue_id})")

except Exception as e:
    print(f"Error fetching venue: {e}")
    print("\nTrying alternative method...")

    # Method 2: Try direct venue ID lookup
    # Common venue IDs for popular SF restaurants - you may need to find yours
    print("\nPlease provide the venue ID manually.")
    print("To find it:")
    print("1. Go to the Resy page in Chrome")
    print("2. Right-click → Inspect")
    print("3. Go to Network tab")
    print("4. Search for a reservation time")
    print("5. Look for a request to '/4/find' and check the 'venue_id' parameter")
    venue_id = input("\nEnter venue ID: ")

    if not venue_id:
        print("No venue ID provided. Exiting.")
        exit(1)

# Configure your reservation
reservation = ReservationConfig(
    restaurant_name=venue_name if 'venue_name' in locals() else venue_slug,
    party_size=2,                      # Change this
    reservation_date=date(2025, 10, 31),  # Change this (Year, Month, Day)
    preferred_times=[
        "22:00",  # 10:00 PM
        "21:30",  # 9:30 PM
        "21:00",  # 9:00 PM
        "22:30",  # 10:30 PM
    ],
    location="sf",
    auto_accept_any_time=False
)

# Set the venue ID directly
reservation.venue_id = int(venue_id)

print(f"\nAttempting to book: {reservation}")
print(f"Venue ID: {venue_id}\n")

# Authenticate
if bot.authenticate():
    # Try to book
    confirmation = bot.attempt_booking(reservation)

    if confirmation:
        print("\n✓ Reservation booked successfully!")
        print(f"Confirmation: {confirmation}")
    else:
        print("\n✗ Could not book reservation")
        print("Check the logs above for details")
else:
    print("Authentication failed. Please check your .env credentials.")
