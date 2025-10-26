"""
Resy Venue ID Extractor

This script helps you find venue IDs from Resy restaurant URLs or pages.
"""

import re
import requests


def extract_venue_id_from_url(url):
    """
    Extract venue ID from a Resy URL

    Args:
        url: Resy restaurant page URL

    Returns:
        venue_id (int) or None
    """

    print(f"\nFetching: {url}")

    try:
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        html = response.text

        # Try multiple patterns to find venue ID
        patterns = [
            r'"venue_id["\s:]+(\d+)',
            r'"id["\s:]+{\s*"resy["\s:]+(\d+)',
            r'venue/(\d+)',
            r'venue_id=(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                venue_id = int(match.group(1))
                print(f"✅ Found Venue ID: {venue_id}")
                return venue_id

        print("❌ Could not find venue ID in page source")
        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching URL: {e}")
        return None


def extract_from_clipboard():
    """Try to get URL from clipboard"""
    try:
        import pyperclip
        url = pyperclip.paste()
        if 'resy.com' in url:
            return url
    except:
        pass
    return None


def main():
    print("=" * 60)
    print("Resy Venue ID Extractor")
    print("=" * 60)

    # Try to get URL from clipboard
    clipboard_url = extract_from_clipboard()
    if clipboard_url:
        print(f"\n📋 Found Resy URL in clipboard: {clipboard_url}")
        use_clipboard = input("Use this URL? (y/n): ").lower().strip()
        if use_clipboard == 'y':
            venue_id = extract_venue_id_from_url(clipboard_url)
            if venue_id:
                print(f"\n🎯 Venue ID: {venue_id}")
                print("\nCopy this to your Resy app!")
            return

    print("\nPaste Resy restaurant URLs (one per line)")
    print("Press Enter twice when done")
    print("-" * 60)

    urls = []
    while True:
        url = input().strip()
        if not url:
            break
        if 'resy.com' in url:
            urls.append(url)
        else:
            print("⚠️  Not a Resy URL, skipping...")

    if not urls:
        print("\nNo URLs provided. Exiting.")
        return

    print(f"\n\nProcessing {len(urls)} URL(s)...")
    print("=" * 60)

    results = []
    for url in urls:
        venue_id = extract_venue_id_from_url(url)
        if venue_id:
            # Try to extract restaurant name from URL
            name_match = re.search(r'/venues/([^/?]+)', url)
            name = name_match.group(1).replace('-', ' ').title() if name_match else 'Unknown'
            results.append((name, venue_id, url))

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    if results:
        print(f"\nFound {len(results)} venue ID(s):\n")
        for name, venue_id, url in results:
            print(f"  {name}")
            print(f"  Venue ID: {venue_id}")
            print(f"  URL: {url}")
            print()

        # Offer to create CSV
        create_csv = input("Export to CSV? (y/n): ").lower().strip()
        if create_csv == 'y':
            import csv
            filename = "resy_venues.csv"
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Venue ID', 'URL'])
                for name, venue_id, url in results:
                    writer.writerow([name, venue_id, url])
            print(f"\n✅ Exported to {filename}")
    else:
        print("\n❌ No venue IDs found")


if __name__ == "__main__":
    main()
