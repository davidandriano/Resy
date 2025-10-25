#!/usr/bin/env python3
"""
Interactive CLI for booking Resy reservations

Simple command-line interface for quick reservation booking.
"""
import argparse
from datetime import datetime, date
from bot import ResyBot
from config import ReservationConfig, load_settings
from notifications import setup_logging


def parse_date(date_string: str) -> date:
    """Parse date from string (YYYY-MM-DD)"""
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}. Use YYYY-MM-DD")


def parse_times(times_string: str) -> list:
    """Parse comma-separated times"""
    return [t.strip() for t in times_string.split(",")]


def main():
    parser = argparse.ArgumentParser(
        description="Book Resy reservations automatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick book
  %(prog)s "Carbone" 2 2025-11-15 "19:00,19:30,20:00"

  # Monitor continuously
  %(prog)s "Don Angie" 4 2025-12-01 "19:00,20:00" --monitor --interval 5

  # Schedule for midnight
  %(prog)s "4 Charles" 2 2025-11-20 "19:00,19:30" --schedule "00:00"

  # Accept any available time
  %(prog)s "Carbone" 2 2025-11-15 "19:00,20:00" --any-time
        """
    )

    parser.add_argument(
        "restaurant",
        help="Restaurant name to search for"
    )
    parser.add_argument(
        "party_size",
        type=int,
        help="Number of people (1-20)"
    )
    parser.add_argument(
        "date",
        type=parse_date,
        help="Reservation date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "times",
        type=parse_times,
        help="Preferred times as comma-separated 24-hour format (e.g., '19:00,19:30,20:00')"
    )
    parser.add_argument(
        "--location",
        default="ny",
        help="Location code (default: ny)"
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Monitor continuously for availability"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Check interval in seconds for monitoring (default: 5)"
    )
    parser.add_argument(
        "--schedule",
        metavar="TIME",
        help="Schedule monitoring to start at specific time (HH:MM in 24-hour format)"
    )
    parser.add_argument(
        "--any-time",
        action="store_true",
        help="Accept any available time if preferred times are unavailable"
    )
    parser.add_argument(
        "--log-file",
        help="Log file path (default: logs/booking.log)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Setup logging
    log_file = args.log_file or "logs/booking.log"
    setup_logging(log_file=log_file)

    # Load settings
    try:
        settings = load_settings()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nMake sure you have configured your .env file with Resy credentials.")
        return 1

    # Create bot
    bot = ResyBot(settings)

    # Authenticate
    print(f"\nAuthenticating with Resy...")
    if not bot.authenticate():
        print("Authentication failed. Please check your credentials in .env")
        return 1

    # Create reservation configuration
    reservation = ReservationConfig(
        restaurant_name=args.restaurant,
        party_size=args.party_size,
        reservation_date=args.date,
        preferred_times=args.times,
        location=args.location,
        auto_accept_any_time=args.any_time
    )

    print(f"\n{'='*60}")
    print(f"Reservation Request")
    print(f"{'='*60}")
    print(f"Restaurant: {args.restaurant}")
    print(f"Party Size: {args.party_size}")
    print(f"Date: {args.date}")
    print(f"Preferred Times: {', '.join(args.times)}")
    print(f"Location: {args.location}")
    if args.any_time:
        print(f"Will accept: Any available time")
    print(f"{'='*60}\n")

    # Execute based on mode
    if args.schedule:
        print(f"Scheduling monitoring to start at {args.schedule}")
        print(f"Will check every {args.interval} seconds once started")
        print("Press Ctrl+C to cancel\n")
        bot.schedule_monitoring(reservation, args.schedule, args.interval)

    elif args.monitor:
        print(f"Starting continuous monitoring")
        print(f"Checking every {args.interval} seconds")
        print("Press Ctrl+C to stop\n")
        confirmation = bot.monitor_reservation(reservation, args.interval)
        if confirmation:
            print("\n✓ Reservation booked successfully!")
            return 0
        else:
            print("\nMonitoring stopped")
            return 1

    else:
        print("Attempting to book reservation...\n")
        confirmation = bot.quick_book(reservation)
        if confirmation:
            print("\n✓ Reservation booked successfully!")
            return 0
        else:
            print("\n✗ Could not book reservation")
            return 1


if __name__ == "__main__":
    exit(main())
