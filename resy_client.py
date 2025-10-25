"""
Resy API Client for automated reservation booking
"""
import requests
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, date
import json

logger = logging.getLogger(__name__)


class ResyClient:
    """Client for interacting with Resy's API"""

    BASE_URL = "https://api.resy.com"
    API_KEY = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"  # Public API key used by Resy's web app

    def __init__(self, email: str, password: str):
        """
        Initialize Resy client

        Args:
            email: Resy account email
            password: Resy account password
        """
        self.email = email
        self.password = password
        self.auth_token: Optional[str] = None
        self.payment_method_id: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f'ResyAPI api_key="{self.API_KEY}"'
        })

    def login(self) -> bool:
        """
        Authenticate with Resy

        Returns:
            bool: True if login successful, False otherwise
        """
        logger.info(f"Logging in as {self.email}")

        url = f"{self.BASE_URL}/3/auth/password"
        payload = {
            "email": self.email,
            "password": self.password
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            self.auth_token = data.get("token")
            self.payment_method_id = data.get("payment_method_id")

            # Update session with auth token
            self.session.headers.update({
                "Authorization": f'ResyAPI api_key="{self.API_KEY}"',
                "X-Resy-Auth-Token": self.auth_token
            })

            logger.info("Login successful")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Login failed: {e}")
            return False

    def get_payment_methods(self) -> List[Dict[str, Any]]:
        """
        Get available payment methods for the account

        Returns:
            List of payment method dictionaries
        """
        if not self.auth_token:
            logger.error("Not authenticated. Please login first.")
            return []

        url = f"{self.BASE_URL}/3/user/payment_methods"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            payment_methods = data.get("payment_methods", [])

            if payment_methods:
                # Use the first payment method by default
                self.payment_method_id = payment_methods[0].get("id")
                logger.info(f"Found {len(payment_methods)} payment method(s)")

            return payment_methods

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get payment methods: {e}")
            return []

    def search_venue(self, query: str, location: str = "ny") -> List[Dict[str, Any]]:
        """
        Search for restaurants/venues

        Args:
            query: Restaurant name to search for
            location: Location code (default: "ny" for New York)

        Returns:
            List of matching venues
        """
        logger.info(f"Searching for venue: {query}")

        url = f"{self.BASE_URL}/3/venuesearch/search"
        params = {
            "query": query,
            "location": location
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            venues = data.get("search", {}).get("hits", [])

            logger.info(f"Found {len(venues)} venue(s)")
            return venues

        except requests.exceptions.RequestException as e:
            logger.error(f"Venue search failed: {e}")
            return []

    def find_availability(
        self,
        venue_id: int,
        party_size: int,
        reservation_date: date,
        preferred_times: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find available reservation slots

        Args:
            venue_id: Venue ID from search results
            party_size: Number of people
            reservation_date: Date for reservation
            preferred_times: List of preferred times (e.g., ["19:00", "19:30"])

        Returns:
            List of available slots
        """
        logger.info(f"Finding availability for venue {venue_id} on {reservation_date}")

        url = f"{self.BASE_URL}/4/find"
        params = {
            "venue_id": venue_id,
            "day": reservation_date.strftime("%Y-%m-%d"),
            "party_size": party_size
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            slots = data.get("results", {}).get("venues", [])

            if not slots:
                logger.info("No availability found")
                return []

            # Extract all available time slots
            available_slots = []
            for venue_data in slots:
                for slot in venue_data.get("slots", []):
                    slot_info = {
                        "config_id": slot.get("config", {}).get("id"),
                        "time": slot.get("date", {}).get("start"),
                        "display_time": slot.get("config", {}).get("display_time"),
                        "type": slot.get("config", {}).get("type"),
                        "badge": slot.get("badge", {}).get("text") if slot.get("badge") else None
                    }
                    available_slots.append(slot_info)

            # Filter by preferred times if specified
            if preferred_times:
                filtered_slots = []
                for slot in available_slots:
                    slot_time = datetime.fromisoformat(slot["time"]).strftime("%H:%M")
                    if slot_time in preferred_times:
                        filtered_slots.append(slot)
                available_slots = filtered_slots

            logger.info(f"Found {len(available_slots)} available slot(s)")
            return available_slots

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to find availability: {e}")
            return []

    def get_booking_details(self, config_id: str, party_size: int, reservation_date: date) -> Optional[Dict[str, Any]]:
        """
        Get booking token and details needed for reservation

        Args:
            config_id: Configuration ID from availability search
            party_size: Number of people
            reservation_date: Date for reservation

        Returns:
            Booking details dictionary or None
        """
        logger.info(f"Getting booking details for config {config_id}")

        url = f"{self.BASE_URL}/3/details"
        params = {
            "config_id": config_id,
            "day": reservation_date.strftime("%Y-%m-%d"),
            "party_size": party_size
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get booking details: {e}")
            return None

    def book_reservation(
        self,
        booking_details: Dict[str, Any],
        payment_method_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Book a reservation

        Args:
            booking_details: Details from get_booking_details()
            payment_method_id: Payment method ID (uses default if not provided)

        Returns:
            Reservation confirmation or None
        """
        if not self.auth_token:
            logger.error("Not authenticated. Please login first.")
            return None

        # Use provided payment method or default
        payment_id = payment_method_id or self.payment_method_id

        book_token = booking_details.get("book_token", {}).get("value")
        if not book_token:
            logger.error("No booking token found in details")
            return None

        logger.info("Attempting to book reservation...")

        url = f"{self.BASE_URL}/3/book"
        payload = {
            "book_token": book_token,
            "struct_payment_method": json.dumps({"id": payment_id}) if payment_id else None,
            "source_id": "resy.com-venue-details"
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            logger.info("Reservation booked successfully!")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to book reservation: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return None

    def cancel_reservation(self, resy_token: str) -> bool:
        """
        Cancel a reservation

        Args:
            resy_token: Reservation token from booking confirmation

        Returns:
            True if cancellation successful
        """
        if not self.auth_token:
            logger.error("Not authenticated. Please login first.")
            return False

        logger.info(f"Canceling reservation {resy_token}")

        url = f"{self.BASE_URL}/3/cancel"
        payload = {"resy_token": resy_token}

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            logger.info("Reservation cancelled successfully")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to cancel reservation: {e}")
            return False
