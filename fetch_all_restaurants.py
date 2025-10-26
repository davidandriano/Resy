"""
Script to fetch all San Francisco restaurants from Resy API
and update the restaurants database
"""
import requests
import json
import os

def fetch_sf_restaurants():
    """Fetch all San Francisco restaurants from Resy API"""

    print("Note: Using Resy's public find endpoint")

    # Resy's venue search endpoint
    base_url = "https://api.resy.com"
    api_key = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Authorization": f'ResyAPI api_key="{api_key}"',
        "Origin": "https://resy.com",
        "Referer": "https://resy.com/",
        "Cache-Control": "no-cache"
    }

    restaurants = []

    # Use the /4/find endpoint that Resy's website uses
    search_url = f"{base_url}/4/find"

    # San Francisco coordinates
    lat = 37.7749
    lon = -122.4194

    # Use tomorrow's date
    from datetime import datetime, timedelta
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Try searching with different parameters
    params = {
        "lat": lat,
        "long": lon,
        "day": tomorrow,
        "party_size": 2,
    }

    print("Attempting to fetch SF restaurants from Resy API...")
    print(f"Using endpoint: {search_url}")

    try:
        response = requests.get(search_url, params=params, headers=headers)
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Save raw response for inspection
            with open("resy_api_response.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Raw API response saved to resy_api_response.json")

            # Parse venues from response
            venues = data.get("results", {}).get("venues", [])

            if not venues:
                print("No venues found in standard location. Checking alternate structure...")
                # Try alternate data structures
                if "venues" in data:
                    venues = data["venues"]
                elif "search" in data and "hits" in data["search"]:
                    venues = data["search"]["hits"]

            print(f"Found {len(venues)} venues")

            for venue in venues:
                try:
                    # Extract venue information
                    venue_id = venue.get("id", {}).get("resy") if isinstance(venue.get("id"), dict) else venue.get("id")
                    name = venue.get("name", "Unknown")

                    # Get neighborhood/location
                    location = venue.get("location", {})
                    neighborhood = location.get("neighborhood", "") or location.get("name", "")

                    # Get cuisine type
                    cuisine = venue.get("type", "") or venue.get("cuisine", "") or "American"

                    if venue_id and name:
                        restaurant = {
                            "name": name,
                            "venue_id": venue_id,
                            "neighborhood": neighborhood,
                            "cuisine": cuisine
                        }
                        restaurants.append(restaurant)
                        print(f"Added: {name} (ID: {venue_id})")

                except Exception as e:
                    print(f"Error parsing venue: {e}")
                    continue

        else:
            print(f"API request failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"Error fetching from API: {e}")

    return restaurants


def try_explore_api():
    """Try different Resy API endpoints to find restaurant listings"""

    base_url = "https://api.resy.com"
    api_key = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Authorization": f'ResyAPI api_key="{api_key}"',
        "Origin": "https://resy.com",
        "Referer": "https://resy.com/"
    }

    # Try different endpoints that Resy uses
    from datetime import datetime, timedelta
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    endpoints = [
        f"/4/find?lat=37.7749&long=-122.4194&day={tomorrow}&party_size=2",
        f"/3/venue/search?lat=37.7749&long=-122.4194&day={tomorrow}&party_size=2",
        "/2/cities",
        "/2/cities/sf/venues",
        f"/4/find?geo_id=100&day={tomorrow}&party_size=2",
    ]

    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\n\nTrying: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")

                # Save successful response
                filename = f"api_test_{endpoint.split('/')[1].split('?')[0]}.json"
                with open(filename, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"Saved to {filename}")
            else:
                print(f"Error response: {response.text[:200]}")

        except Exception as e:
            print(f"Error: {e}")


def update_database(restaurants):
    """Update restaurants_db.json with fetched restaurants"""

    if not restaurants:
        print("No restaurants to add to database")
        return

    # Load existing database
    db_path = "restaurants_db.json"
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            db = json.load(f)
    else:
        db = {"san_francisco": []}

    # Sort and deduplicate
    existing_ids = {r["venue_id"] for r in db.get("san_francisco", [])}
    new_restaurants = [r for r in restaurants if r["venue_id"] not in existing_ids]

    # Add new restaurants
    db["san_francisco"].extend(new_restaurants)

    # Sort by name
    db["san_francisco"] = sorted(db["san_francisco"], key=lambda x: x["name"])

    # Save updated database
    with open(db_path, 'w') as f:
        json.dump(db, f, indent=2)

    print(f"\nDatabase updated!")
    print(f"Total SF restaurants: {len(db['san_francisco'])}")
    print(f"Newly added: {len(new_restaurants)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Resy Restaurant Database Updater")
    print("=" * 60)

    # First, explore API to find the right endpoint
    print("\n\nStep 1: Exploring Resy API endpoints...")
    try_explore_api()

    print("\n\nStep 2: Fetching SF restaurants...")
    restaurants = fetch_sf_restaurants()

    if restaurants:
        print(f"\n\nSuccessfully fetched {len(restaurants)} restaurants")

        # Show sample
        print("\nSample restaurants:")
        for r in restaurants[:5]:
            print(f"  - {r['name']} ({r['neighborhood']}) - ID: {r['venue_id']}")

        # Update database
        update_database(restaurants)
    else:
        print("\nNo restaurants fetched. Check the API responses saved to JSON files.")
        print("You may need to manually inspect the API structure.")
