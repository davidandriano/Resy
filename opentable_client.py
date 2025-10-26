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
