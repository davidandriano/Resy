"""
Helper functions for Resy bot
"""
import re
from typing import Optional, Tuple

def extract_venue_from_url(url: str) -> Optional[Tuple[int, str]]:
    """
    Extract venue ID and slug from a Resy URL

    Args:
        url: Resy URL (e.g., https://resy.com/cities/san-francisco-ca/venues/izakaya-rintaro)

    Returns:
        Tuple of (venue_id, venue_slug) if found in URL, or None
    """
    # Pattern 1: venues/slug format
    slug_match = re.search(r'/venues/([a-z0-9-]+)', url)
    if slug_match:
        slug = slug_match.group(1)

        # Try to extract ID if present in URL
        id_match = re.search(r'[?&]id=(\d+)', url)
        if id_match:
            return int(id_match.group(1)), slug
        else:
            return None, slug

    # Pattern 2: Direct ID in URL
    id_match = re.search(r'venue[=\-/](\d+)', url, re.IGNORECASE)
    if id_match:
        return int(id_match.group(1)), None

    return None, None

def get_location_from_url(url: str) -> str:
    """
    Extract location code from Resy URL

    Args:
        url: Resy URL

    Returns:
        Location code (defaults to 'ny')
    """
    city_map = {
        'new-york': 'ny',
        'san-francisco': 'sf',
        'los-angeles': 'la',
        'washington-dc': 'dc',
        'boston': 'boston',
        'austin': 'austin',
        'miami': 'miami',
        'chicago': 'chicago'
    }

    for city_slug, code in city_map.items():
        if city_slug in url.lower():
            return code

    return 'ny'  # default
