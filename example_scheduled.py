#!/usr/bin/env python3
"""
Example: Schedule monitoring to start at a specific time

This script will wait until a specific time, then start monitoring.
Perfect for when you know exactly when reservations will be released
(e.g., midnight, 9am, etc.)
"""
from datetime import date
from bot import ResyBot
from config import ReservationConfig, load_settings
from notifications import setup_logging

# Setup logging with file output
setup_logging(log_file="logs/scheduled.log")

# Load settings from .env
settings = load_settings()

# Create bot
bot = ResyBot(settings)

# Configure the reservation
reservation = ReservationConfig(
    restaurant_name="4 Charles Prime Rib",
    party_size=4,
    reservation_date=date(2025, 12, 1),
    preferred_times=[
        "19:00",
        "19:15",
        "19:30",
        "20:00"
    ],
    location="ny",
    auto_accept_any_time=False
)

# Time to start monitoring (24-hour format)
# For example: "00:00" for midnight, "09:00" for 9am
START_TIME = "00:00"  # Start at midnight

# Authenticate
if bot.authenticate():
    print(f"\nScheduled monitoring for: {reservation}")
    print(f"Will start checking at: {START_TIME}")
    print("\nPress Ctrl+C to cancel.\n")

    # Schedule monitoring to start at the specified time
    bot.schedule_monitoring(
        config=reservation,
        start_time=START_TIME,
        check_interval=2  # Once started, check every 2 seconds
    )
else:
    print("Authentication failed. Please check your .env credentials.")
