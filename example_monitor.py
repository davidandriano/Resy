#!/usr/bin/env python3
"""
Example: Monitor for reservations continuously

This script will continuously check for availability and book as soon as a slot opens.
Perfect for high-demand restaurants where you need to act fast.
"""
from datetime import date
from bot import ResyBot
from config import ReservationConfig, load_settings
from notifications import setup_logging

# Setup logging with file output
setup_logging(log_file="logs/monitor.log")

# Load settings from .env
settings = load_settings()

# Create bot
bot = ResyBot(settings)

# Configure the reservation you want to monitor
reservation = ReservationConfig(
    restaurant_name="Don Angie",  # Restaurant name
    party_size=2,                 # Number of people
    reservation_date=date(2025, 11, 20),  # Target date
    preferred_times=[             # Preferred times
        "18:30",
        "19:00",
        "19:30",
        "20:00"
    ],
    location="ny",
    auto_accept_any_time=False   # Set to True to accept any available time
)

# Authenticate
if bot.authenticate():
    print(f"\nStarting monitoring for: {reservation}")
    print("\nThis will check every 5 seconds for availability.")
    print("Press Ctrl+C to stop.\n")

    # Start monitoring (checks every 5 seconds)
    confirmation = bot.monitor_reservation(
        config=reservation,
        check_interval=5  # seconds between checks
    )

    if confirmation:
        print("\n✓ Successfully booked!")
    else:
        print("\nMonitoring stopped")
else:
    print("Authentication failed. Please check your .env credentials.")
