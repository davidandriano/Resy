Files to Upload to GitHub
You need to upload 3 new files and update 1 existing file:

NEW FILES:
opentable_client.py - OpenTable API client
unified_bot.py - Platform-agnostic booking interface
MULTI_PLATFORM_GUIDE.md - Documentation for multi-platform feature
UPDATE:
app.py - Fix the SyntaxError on Streamlit Cloud
Step-by-Step Upload Instructions
Step 1: Upload opentable_client.py
Go to https://github.com/davidandriano/Resy
Click the "Add file" button (top right)
Select "Create new file"
In the filename box, type: opentable_client.py
Copy and paste this entire code:
"""
OpenTable API Client for automated reservation booking

WARNING: OpenTable does not provide a public API. This client reverse-engineers
their web API and may break if they make changes. Use responsibly.
"""
import requests
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, date
import json

logger = logging.getLogger(__name__)


class OpenTableClient:
    """Client for interacting with OpenTable's API"""

    BASE_URL = "https://www.opentable.com"
    API_URL = "https://www.opentable.com/dapi"

    def __init__(self, email: str, password: str):
        """
        Initialize OpenTable client

        Args:
            email: OpenTable account email
            password: OpenTable account password
        """
        self.email = email
        self.password = password
        self.auth_token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def login(self) -> bool:
        """
        Authenticate with OpenTable

        Returns:
            bool: True if login successful, False otherwise
        """
        logger.info(f"Logging in to OpenTable as {self.email}")

        # OpenTable login endpoint
        url = f"{self.BASE_URL}/api/auth/login"

        payload = {
            "email": self.email,
            "password": self.password
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            data = response.json()

            # Extract auth token from response
            # Note: This structure may vary - OpenTable's API is not documented
            self.auth_token = data.get("token") or data.get("access_token")

            if self.auth_token:
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                logger.info("OpenTable login successful")
                return True
            else:
                logger.error("No auth token in response")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenTable login failed: {e}")
            return False

    def find_availability(
        self,
        restaurant_id: int,
        party_size: int,
        reservation_date: date,
        preferred_times: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find available reservation slots

        Args:
            restaurant_id: OpenTable restaurant ID
            party_size: Number of people
            reservation_date: Date for reservation
            preferred_times: List of preferred times in HH:MM format

        Returns:
            List of available time slots
        """
        logger.info(f"Searching OpenTable availability for restaurant {restaurant_id}")

        # OpenTable availability endpoint
        url = f"{self.API_URL}/availability/search"

        params = {
            "restaurantId": restaurant_id,
            "partySize": party_size,
            "dateTime": reservation_date.strftime("%Y-%m-%d")
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Parse available slots
            # Note: Structure may vary based on OpenTable's API
            slots = []
            available_times = data.get("times", []) or data.get("availabilities", [])

            for slot in available_times:
                slot_info = {
                    "time": slot.get("time"),
                    "display_time": slot.get("displayTime"),
                    "available": slot.get("available", False),
                    "token": slot.get("token") or slot.get("reservationToken")
                }
                slots.append(slot_info)

            logger.info(f"Found {len(slots)} available slots")
            return slots

        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking availability: {e}")
            return []

    def make_reservation(
        self,
        restaurant_id: int,
        party_size: int,
        reservation_date: date,
        time_slot: str,
        reservation_token: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make a reservation

        Args:
            restaurant_id: OpenTable restaurant ID
            party_size: Number of people
            reservation_date: Date for reservation
            time_slot: Time in HH:MM format
            reservation_token: Token from availability check

        Returns:
            Confirmation details or None
        """
        if not self.auth_token:
            logger.error("Not authenticated. Please login first.")
            return None

        logger.info(f"Attempting to book OpenTable reservation")

        # OpenTable booking endpoint
        url = f"{self.API_URL}/reservation/create"

        payload = {
            "restaurantId": restaurant_id,
            "partySize": party_size,
            "dateTime": f"{reservation_date.strftime('%Y-%m-%d')}T{time_slot}:00",
            "reservationToken": reservation_token
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            data = response.json()

            confirmation = {
                "confirmation_number": data.get("confirmationNumber") or data.get("reservationId"),
                "restaurant_id": restaurant_id,
                "party_size": party_size,
                "date": reservation_date,
                "time": time_slot,
                "status": data.get("status", "confirmed")
            }

            logger.info(f"Reservation confirmed: {confirmation['confirmation_number']}")
            return confirmation

        except requests.exceptions.RequestException as e:
            logger.error(f"Booking failed: {e}")
            return None


# Note about OpenTable API
"""
IMPORTANT: OpenTable does not provide a public API and actively works to prevent
automated bookings. This client is a reverse-engineered implementation and may:

1. Break at any time if OpenTable changes their API
2. Result in account suspension if detected as a bot
3. Require CAPTCHA solving for some actions

For production use, consider:
- OpenTable's official partnership program (if eligible)
- Using OpenTable's widget/iframe embed
- Manual booking through their website

This implementation is for educational purposes and personal use only.
"""
Scroll down and click "Commit new file" (green button)
Add commit message: "Add OpenTable API client"
Click "Commit new file"
Step 2: Upload unified_bot.py
Click "Add file" → "Create new file" again
Filename: unified_bot.py
Copy and paste this code:
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
