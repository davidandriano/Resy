"""
Google Places API Integration for Restaurant Reviews and Photos
"""
import os
import requests
from typing import Optional, Dict, List, Any
import streamlit as st

class GooglePlacesClient:
    """Client for Google Places API"""

    BASE_URL = "https://maps.googleapis.com/maps/api/place"

    def __init__(self, api_key: str = None):
        """
        Initialize Google Places client

        Args:
            api_key: Google Places API key (or set GOOGLE_PLACES_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY')
        if not self.api_key:
            st.warning("⚠️ Google Places API key not configured. Reviews and photos won't be available.")

    def search_place(self, name: str, location: str = "San Francisco, CA", debug: bool = False) -> Optional[str]:
        """
        Search for a place and get its place_id

        Args:
            name: Restaurant name
            location: Location (city, state)
            debug: If True, print detailed debug information

        Returns:
            place_id if found, None otherwise
        """
        if not self.api_key:
            return None

        # Try multiple search strategies
        search_queries = [
            f"{name} restaurant {location}",
            f"{name} {location}",
            f"{name} restaurant San Francisco",
            f"{name} San Francisco",
            name  # Just the name alone
        ]

        for query in search_queries:
            url = f"{self.BASE_URL}/textsearch/json"
            params = {
                "query": query,
                "key": self.api_key
            }

            try:
                if debug:
                    st.info(f"🔍 Searching with query: \"{query}\"")

                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if debug:
                    status = data.get("status")
                    results_count = len(data.get("results", []))
                    st.info(f"📊 API Status: {status}, Results: {results_count}")

                    if results_count > 0:
                        for idx, result in enumerate(data.get("results", [])[:3]):
                            st.info(f"Result {idx+1}: {result.get('name')} - {result.get('formatted_address', 'No address')}")

                if data.get("results"):
                    place_id = data["results"][0].get("place_id")
                    if debug:
                        st.success(f"✅ Found place_id: {place_id}")
                    return place_id

            except Exception as e:
                if debug:
                    st.error(f"❌ Error searching with query '{query}': {e}")
                continue

        return None

    def get_place_details(self, place_id: str, debug: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a place

        Args:
            place_id: Google Places ID
            debug: If True, show detailed error information

        Returns:
            Dictionary with place details or None
        """
        if not self.api_key or not place_id:
            if debug:
                st.error("❌ Missing API key or place_id")
            return None

        url = f"{self.BASE_URL}/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,rating,user_ratings_total,reviews,photos,formatted_address,website,formatted_phone_number,opening_hours,price_level",
            "key": self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            status = data.get("status")

            if debug:
                st.info(f"📊 API Response Status: {status}")
                if status != "OK":
                    error_msg = data.get("error_message", "No error message provided")
                    st.error(f"❌ API Error: {error_msg}")
                    st.code(f"Response: {data}")

            if status == "OK" and data.get("result"):
                return data["result"]

            return None
        except Exception as e:
            if debug:
                st.error(f"❌ Exception getting place details: {e}")
            return None

    def get_photo_url(self, photo_reference: str, max_width: int = 400) -> Optional[str]:
        """
        Get photo URL from photo reference

        Args:
            photo_reference: Photo reference from place details
            max_width: Maximum width of the photo

        Returns:
            Photo URL or None
        """
        if not self.api_key or not photo_reference:
            return None

        url = f"{self.BASE_URL}/photo"
        params = {
            "photo_reference": photo_reference,
            "maxwidth": max_width,
            "key": self.api_key
        }

        # Return the URL (requests will handle redirect)
        return f"{url}?" + "&".join([f"{k}={v}" for k, v in params.items()])

    def format_reviews(self, reviews: List[Dict]) -> List[Dict[str, Any]]:
        """
        Format reviews for display

        Args:
            reviews: List of review dictionaries from Google

        Returns:
            Formatted list of reviews
        """
        formatted = []
        for review in reviews[:5]:  # Top 5 reviews
            formatted.append({
                "author": review.get("author_name", "Anonymous"),
                "rating": review.get("rating", 0),
                "text": review.get("text", ""),
                "time": review.get("relative_time_description", ""),
                "profile_photo": review.get("profile_photo_url", "")
            })
        return formatted


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_restaurant_google_data(place_id: str, api_key: str = None, debug: bool = False) -> Optional[Dict]:
    """
    Cached function to get Google Places data for a restaurant

    Args:
        place_id: Google Places ID
        api_key: Google API key
        debug: If True, show detailed debug information

    Returns:
        Dictionary with Google data or None
    """
    client = GooglePlacesClient(api_key)
    return client.get_place_details(place_id, debug=debug)


@st.cache_data(ttl=86400)  # Cache for 24 hours
def search_restaurant_place_id(name: str, location: str = "San Francisco, CA", api_key: str = None, debug: bool = False) -> Optional[str]:
    """
    Cached function to search for restaurant and get place_id

    Args:
        name: Restaurant name
        location: Location
        api_key: Google API key
        debug: If True, show detailed debug information

    Returns:
        place_id or None
    """
    client = GooglePlacesClient(api_key)
    return client.search_place(name, location, debug=debug)
