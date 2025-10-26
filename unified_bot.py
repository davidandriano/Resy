"""
Unified Reservation Bot - Supports both Resy and OpenTable

This module provides a platform-agnostic interface for booking reservations
on either Resy or OpenTable based on the restaurant's platform.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import date
from resy_client import ResyClient
from opentable_client import OpenTableClient

logger = logging.getLogger(__name__)


class UnifiedReservationBot:
    """
    Unified bot that can book on both Resy and OpenTable
    """

    def __init__(self, resy_email: str = None, resy_password: str = None,
                 opentable_email: str = None, opentable_password: str = None):
        """
        Initialize with credentials for both platforms

        Args:
            resy_email: Resy account email
            resy_password: Resy account password
            opentable_email: OpenTable account email (can be same as Resy)
            opentable_password: OpenTable account password
        """
        self.resy_client = None
        self.opentable_client = None
        self.resy_authenticated = False
        self.opentable_authenticated = False

        # Initialize Resy client if credentials provided
        if resy_email and resy_password:
            self.resy_client = ResyClient(resy_email, resy_password)

        # Initialize OpenTable client if credentials provided
        # (can use same credentials if user has accounts on both)
        if opentable_email and opentable_password:
            self.opentable_client = OpenTableClient(opentable_email, opentable_password)
        elif resy_email and resy_password:
            # Try using Resy credentials for OpenTable if no separate ones provided
            self.opentable_client = OpenTableClient(resy_email, resy_password)

    def authenticate(self, platform: str = "both") -> Dict[str, bool]:
        """
        Authenticate with specified platform(s)

        Args:
            platform: "resy", "opentable", or "both"

        Returns:
            Dict with authentication status for each platform
        """
        results = {}

        if platform in ["resy", "both"] and self.resy_client:
            logger.info("Authenticating with Resy...")
            self.resy_authenticated = self.resy_client.login()
            results["resy"] = self.resy_authenticated

        if platform in ["opentable", "both"] and self.opentable_client:
            logger.info("Authenticating with OpenTable...")
            self.opentable_authenticated = self.opentable_client.login()
            results["opentable"] = self.opentable_authenticated

        return results

    def find_availability(
        self,
        restaurant_id: int,
        party_size: int,
        reservation_date: date,
        platform: str,
        preferred_times: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find availability on the specified platform

        Args:
            restaurant_id: Restaurant ID on the platform
            party_size: Number of people
            reservation_date: Date for reservation
            platform: "resy" or "opentable"
            preferred_times: List of preferred times

        Returns:
            List of available slots
        """
        if platform == "resy":
            if not self.resy_authenticated:
                logger.error("Not authenticated with Resy")
                return []
            return self.resy_client.find_availability(
                restaurant_id, party_size, reservation_date, preferred_times
            )

        elif platform == "opentable":
            if not self.opentable_authenticated:
                logger.error("Not authenticated with OpenTable")
                return []
            return self.opentable_client.find_availability(
                restaurant_id, party_size, reservation_date, preferred_times
            )

        else:
            logger.error(f"Unknown platform: {platform}")
            return []

    def book_reservation(
        self,
        restaurant_id: int,
        restaurant_name: str,
        party_size: int,
        reservation_date: date,
        platform: str,
        preferred_times: List[str] = None,
        auto_accept_any_time: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Book a reservation on the specified platform

        Args:
            restaurant_id: Restaurant ID
            restaurant_name: Restaurant name (for logging)
            party_size: Number of people
            reservation_date: Date for reservation
            platform: "resy" or "opentable"
            preferred_times: List of preferred times
            auto_accept_any_time: Book any available time if preferred not available

        Returns:
            Confirmation details or None
        """
        logger.info(f"Attempting to book {restaurant_name} on {platform.upper()}")

        # Get availability
        slots = self.find_availability(
            restaurant_id, party_size, reservation_date, platform, preferred_times
        )

        if not slots:
            logger.warning(f"No availability found for {restaurant_name}")
            return None

        # Find preferred slot or any slot
        selected_slot = None

        if preferred_times:
            # Try to find a preferred time
            for slot in slots:
                slot_time = slot.get("time") or slot.get("display_time", "").split()[0]
                if slot_time in preferred_times:
                    selected_slot = slot
                    break

        # If no preferred time found, take any slot if auto_accept is True
        if not selected_slot and auto_accept_any_time and slots:
            selected_slot = slots[0]

        if not selected_slot:
            logger.warning(f"No suitable time slot found for {restaurant_name}")
            return None

        # Book the reservation
        if platform == "resy":
            # Resy-specific booking logic (use existing bot.py logic)
            config_token = selected_slot.get("config", {}).get("token")
            if config_token:
                booking_details = self.resy_client.get_booking_details(
                    config_token, party_size, reservation_date
                )
                if booking_details:
                    return self.resy_client.book_reservation(
                        config_token, party_size, reservation_date
                    )

        elif platform == "opentable":
            # OpenTable-specific booking logic
            reservation_token = selected_slot.get("token")
            time_slot = selected_slot.get("time")
            return self.opentable_client.make_reservation(
                restaurant_id, party_size, reservation_date, time_slot, reservation_token
            )

        return None

    def get_platform_status(self) -> Dict[str, str]:
        """
        Get authentication status for all platforms

        Returns:
            Dict with status for each platform
        """
        return {
            "resy": "authenticated" if self.resy_authenticated else "not authenticated",
            "opentable": "authenticated" if self.opentable_authenticated else "not authenticated"
        }
