#!/usr/bin/env python3
"""
Example: Search for restaurants and check availability

Use this script to test searching for restaurants and viewing available times.
Great for exploring what's available before committing to a booking.
"""
from datetime import date
from bot import ResyBot
from config import load_settings
from notifications import setup_logging

# Setup logging
setup_logging()

# Load settings
settings = load_settings()

# Create bot
bot = ResyBot(settings)

# Authenticate
if not bot.authenticate():
    print("Authentication failed. Please check your .env credentials.")
    exit(1)

# Search for a restaurant
print("\n" + "="*60)
print("SEARCHING FOR RESTAURANTS")
print("="*60 + "\n")

restaurant_name = "Carbone"
location = "ny"

venues = bot.client.search_venue(restaurant_name, location)

if venues:
    print(f"Found {len(venues)} restaurant(s):\n")
    for i, venue in enumerate(venues[:5], 1):  # Show top 5
        print(f"{i}. {venue.get('name')}")
        print(f"   Location: {venue.get('location', {}).get('name')}")
        print(f"   Neighborhood: {venue.get('location', {}).get('neighborhood')}")
        print(f"   Venue ID: {venue.get('id', {}).get('resy')}")
        print()

    # Check availability for the first result
    venue_id = venues[0].get("id", {}).get("resy")
    venue_name = venues[0].get("name")

    print("\n" + "="*60)
    print(f"CHECKING AVAILABILITY: {venue_name}")
    print("="*60 + "\n")

    # Set your search parameters
    party_size = 2
    reservation_date = date(2025, 11, 1)

    print(f"Party size: {party_size}")
    print(f"Date: {reservation_date}\n")

    slots = bot.client.find_availability(
        venue_id=venue_id,
        party_size=party_size,
        reservation_date=reservation_date
    )

    if slots:
        print(f"Found {len(slots)} available time slot(s):\n")
        for slot in slots:
            badge = f" [{slot['badge']}]" if slot['badge'] else ""
            print(f"  • {slot['display_time']}{badge}")
    else:
        print("No availability found for this date.")

else:
    print(f"No restaurants found matching '{restaurant_name}'")

print("\n" + "="*60)
