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

        # Create headers with form-encoded content type for login
        login_headers = self.session.headers.copy()
        login_headers["Content-Type"] = "application/x-www-form-urlencoded"

        try:
            # Use data= instead of json= for form-encoded submission
            response = self.session.post(url, data=payload, headers=login_headers)
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

        # First try the search API
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

            if venues:
                logger.info(f"Found {len(venues)} venue(s)")
                return venues

        except requests.exceptions.RequestException as e:
            logger.warning(f"Venue search API failed: {e}, trying alternative method...")

        # If search API fails, try looking up by URL slug
        return self.search_venue_by_slug(query, location)

    def search_venue_by_slug(self, query: str, location: str = "ny") -> List[Dict[str, Any]]:
        """
        Search for venue by constructing URL slug from restaurant name

        Args:
            query: Restaurant name
            location: Location code

        Returns:
            List with venue info if found
        """
        # Create URL slug from restaurant name (lowercase, spaces to hyphens)
        slug = query.lower().replace(" ", "-").replace("'", "")

        logger.info(f"Trying venue lookup with slug: {slug}")

        url = f"{self.BASE_URL}/3/venue?url_slug={slug}&location={location}"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            data = response.json()
            venue_id = data.get("id", {}).get("resy")

            if venue_id:
                # Format as search result for compatibility
                venue_result = {
                    "id": {"resy": venue_id},
                    "name": data.get("name"),
                    "location": data.get("location")
                }
                logger.info(f"Found venue via slug: {data.get('name')} (ID: {venue_id})")
                return [venue_result]

        except requests.exceptions.RequestException as e:
            logger.error(f"Venue slug lookup failed: {e}")

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

        # First, get venue details to extract latitude and longitude
        venue_url = f"{self.BASE_URL}/3/venue?id={venue_id}"
        try:
            venue_response = self.session.get(venue_url)
            venue_response.raise_for_status()
            venue_data = venue_response.json()

            location = venue_data.get("location", {})
            lat = location.get("latitude")
            long = location.get("longitude")

            if not lat or not long:
                logger.warning(f"Could not get venue location, using default SF coordinates")
                lat = 37.7749
                long = -122.4194

        except Exception as e:
            logger.warning(f"Failed to get venue location: {e}, using default SF coordinates")
            lat = 37.7749
            long = -122.4194

        url = f"{self.BASE_URL}/4/find"
        params = {
            "venue_id": venue_id,
            "day": reservation_date.strftime("%Y-%m-%d"),
            "party_size": party_size,
            "lat": lat,
            "long": long
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
                    # Extract display time from config or calculate from date
                    config = slot.get("config", {})
                    date_info = slot.get("date", {})
                    start_time = date_info.get("start", "")

                    # Parse display time
                    display_time = config.get("display_time")
                    if not display_time and start_time:
                        # Calculate from start time (format: "2025-10-31 21:45:00")
                        try:
                            time_part = start_time.split(" ")[1] if " " in start_time else ""
                            if time_part:
                                hour, minute, _ = time_part.split(":")
                                display_time = f"{hour}:{minute}"
                        except:
                            display_time = None

                    slot_info = {
                        "config_token": config.get("token"),  # Use token instead of id
                        "config_id": config.get("id"),  # Keep id for reference
                        "time": start_time,
                        "display_time": display_time,
                        "type": config.get("type"),
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

    def get_booking_details(self, config_token: str, party_size: int, reservation_date: date) -> Optional[Dict[str, Any]]:
        """
        Get booking token and details needed for reservation

        Args:
            config_token: Configuration token from availability search (e.g., "rgs://resy/...")
            party_size: Number of people
            reservation_date: Date for reservation

        Returns:
            Booking details dictionary or None
        """
        logger.info(f"Getting booking details for config token: {config_token[:50]}...")

        url = f"{self.BASE_URL}/3/details"
        params = {
            "config_id": config_token,  # API expects config_id param but wants the token value
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
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
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

        # Use form-encoded content type for booking
        booking_headers = self.session.headers.copy()
        booking_headers["Content-Type"] = "application/x-www-form-urlencoded"

        try:
            response = self.session.post(url, data=payload, headers=booking_headers)
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

        # Use form-encoded content type for cancellation
        cancel_headers = self.session.headers.copy()
        cancel_headers["Content-Type"] = "application/x-www-form-urlencoded"

        try:
            response = self.session.post(url, data=payload, headers=cancel_headers)
            response.raise_for_status()

            logger.info("Reservation cancelled successfully")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to cancel reservation: {e}")
            return False
