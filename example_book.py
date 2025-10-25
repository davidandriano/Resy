#!/usr/bin/env python3
"""
Example: Book a reservation immediately

This script attempts to book a reservation right away.
Use this when reservations are already available.
"""
from datetime import date
from bot import ResyBot
from config import ReservationConfig, load_settings
from notifications import setup_logging

# Setup logging
setup_logging()

# Load settings from .env
settings = load_settings()

# Create bot
bot = ResyBot(settings)

# Configure the reservation you want to book
reservation = ReservationConfig(
    restaurant_name="Carbone",  # Restaurant name to search for
    party_size=2,                # Number of people
    reservation_date=date(2025, 11, 15),  # Reservation date
    preferred_times=[            # Preferred times (24-hour format)
        "19:00",
        "19:30",
        "20:00",
        "20:30"
    ],
    location="ny",              # Location code (ny, la, sf, etc.)
    auto_accept_any_time=False  # Accept any time if preferred times unavailable
)

# Authenticate and book
if bot.authenticate():
    print(f"\nAttempting to book: {reservation}\n")
    confirmation = bot.quick_book(reservation)

    if confirmation:
        print("\n✓ Reservation booked successfully!")
        print(f"Confirmation: {confirmation}")
    else:
        print("\n✗ Could not book reservation")
        print("Possible reasons:")
        print("  - No availability at preferred times")
        print("  - Restaurant not found")
        print("  - Reservation window not yet open")
else:
    print("Authentication failed. Please check your .env credentials.")
