"""
Resy Reservation Bot - Main bot logic with scheduling
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import schedule
from resy_client import ResyClient
from config import ReservationConfig, Settings, load_settings
from notifications import send_notification, setup_logging

logger = logging.getLogger(__name__)


class ResyBot:
    """Automated reservation booking bot for Resy"""

    def __init__(self, settings: Settings):
        """
        Initialize bot with settings

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.client = ResyClient(settings.resy_email, settings.resy_password)
        self.active_reservations: Dict[str, ReservationConfig] = {}
        self.is_authenticated = False

    def authenticate(self) -> bool:
        """
        Authenticate with Resy

        Returns:
            True if successful
        """
        if self.is_authenticated:
            return True

        logger.info("Authenticating with Resy...")
        success = self.client.login()

        if success:
            self.is_authenticated = True
            # Get payment methods if not provided
            if not self.client.payment_method_id:
                payment_methods = self.client.get_payment_methods()
                if payment_methods:
                    logger.info(f"Using payment method: {payment_methods[0].get('provider_name')} ending in {payment_methods[0].get('last_four')}")
        else:
            logger.error("Authentication failed. Please check your credentials.")

        return success

    def find_venue(self, restaurant_name: str, location: str = "ny") -> Optional[int]:
        """
        Find venue ID for a restaurant

        Args:
            restaurant_name: Name of restaurant
            location: Location code

        Returns:
            Venue ID or None
        """
        venues = self.client.search_venue(restaurant_name, location)

        if not venues:
            logger.error(f"Could not find restaurant: {restaurant_name}")
            return None

        # Use first match
        venue = venues[0]
        venue_id = venue.get("id", {}).get("resy")
        venue_name = venue.get("name")

        logger.info(f"Found venue: {venue_name} (ID: {venue_id})")
        return venue_id

    def attempt_booking(self, config: ReservationConfig) -> Optional[Dict[str, Any]]:
        """
        Attempt to book a reservation

        Args:
            config: Reservation configuration

        Returns:
            Booking confirmation or None
        """
        logger.info(f"Attempting booking: {config}")

        # Ensure we have venue ID
        if not config.venue_id:
            config.venue_id = self.find_venue(config.restaurant_name, config.location)
            if not config.venue_id:
                return None

        # Find availability
        available_slots = self.client.find_availability(
            venue_id=config.venue_id,
            party_size=config.party_size,
            reservation_date=config.reservation_date,
            preferred_times=config.preferred_times if not config.auto_accept_any_time else None
        )

        if not available_slots:
            logger.info("No availability found for preferred times")

            # If auto-accept is enabled, try any time
            if config.auto_accept_any_time:
                logger.info("Checking for any available times...")
                available_slots = self.client.find_availability(
                    venue_id=config.venue_id,
                    party_size=config.party_size,
                    reservation_date=config.reservation_date
                )

            if not available_slots:
                return None

        # Use the first available slot
        slot = available_slots[0]
        logger.info(f"Found available slot: {slot['display_time']}")

        # Get booking details
        booking_details = self.client.get_booking_details(
            config_id=slot["config_id"],
            party_size=config.party_size,
            reservation_date=config.reservation_date
        )

        if not booking_details:
            logger.error("Failed to get booking details")
            return None

        # Book the reservation
        confirmation = self.client.book_reservation(
            booking_details=booking_details,
            payment_method_id=self.settings.resy_payment_method_id
        )

        if confirmation:
            logger.info("=" * 60)
            logger.info("RESERVATION BOOKED SUCCESSFULLY!")
            logger.info(f"Restaurant: {config.restaurant_name}")
            logger.info(f"Date: {config.reservation_date}")
            logger.info(f"Time: {slot['display_time']}")
            logger.info(f"Party Size: {config.party_size}")
            logger.info("=" * 60)

            # Send notification
            send_notification(
                self.settings,
                subject=f"Resy Reservation Booked: {config.restaurant_name}",
                message=f"Successfully booked reservation at {config.restaurant_name} "
                        f"for {config.party_size} on {config.reservation_date} at {slot['display_time']}"
            )

        return confirmation

    def monitor_reservation(self, config: ReservationConfig, check_interval: int = 5) -> Optional[Dict[str, Any]]:
        """
        Monitor and attempt to book a reservation repeatedly

        Args:
            config: Reservation configuration
            check_interval: Seconds between checks (default: 5)

        Returns:
            Booking confirmation when successful, or None
        """
        logger.info(f"Starting monitoring for: {config}")
        logger.info(f"Will check every {check_interval} seconds")

        # Pre-fetch venue ID
        if not config.venue_id:
            config.venue_id = self.find_venue(config.restaurant_name, config.location)
            if not config.venue_id:
                logger.error("Cannot start monitoring without venue ID")
                return None

        attempt_count = 0
        while True:
            attempt_count += 1
            logger.info(f"Check attempt #{attempt_count}")

            try:
                confirmation = self.attempt_booking(config)
                if confirmation:
                    return confirmation

                # Wait before next attempt
                logger.info(f"Waiting {check_interval} seconds before next check...")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                return None
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                logger.info(f"Waiting {check_interval} seconds before retry...")
                time.sleep(check_interval)

    def schedule_monitoring(self, config: ReservationConfig, start_time: str, check_interval: int = 5):
        """
        Schedule monitoring to start at a specific time

        Args:
            config: Reservation configuration
            start_time: Time to start monitoring (format: "HH:MM" in 24-hour)
            check_interval: Seconds between checks once started
        """
        logger.info(f"Scheduling monitoring to start at {start_time}")

        def start_monitoring():
            logger.info(f"Starting scheduled monitoring at {datetime.now()}")
            self.monitor_reservation(config, check_interval)

        # Schedule the job
        schedule.every().day.at(start_time).do(start_monitoring)

        logger.info("Waiting for scheduled time...")
        logger.info("Press Ctrl+C to cancel")

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduling cancelled by user")

    def quick_book(self, config: ReservationConfig) -> Optional[Dict[str, Any]]:
        """
        Make a single booking attempt (no monitoring)

        Args:
            config: Reservation configuration

        Returns:
            Booking confirmation or None
        """
        if not self.is_authenticated:
            if not self.authenticate():
                return None

        return self.attempt_booking(config)


def main():
    """Main entry point"""
    # Setup logging
    setup_logging()

    # Load settings
    try:
        settings = load_settings()
    except ValueError as e:
        logger.error(str(e))
        return

    # Create bot
    bot = ResyBot(settings)

    # Authenticate
    if not bot.authenticate():
        logger.error("Failed to authenticate. Exiting.")
        return

    logger.info("Resy Bot is ready!")
    logger.info("Use the example scripts to configure and run the bot")


if __name__ == "__main__":
    main()
