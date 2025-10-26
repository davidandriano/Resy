"""
Batch add restaurants to the database

This script helps you quickly add multiple restaurants to your database.
Since Resy blocks automated scraping, you'll need to manually find venue IDs.

How to find a venue ID:
1. Go to the restaurant's page on resy.com
2. Look at the URL - it will be like: https://resy.com/cities/sf/venue-name
3. Inspect the page source (Right-click > Inspect)
4. Search for "venue_id" or "resy://venue/"
5. The venue ID is a number like 339, 1505, etc.

Usage:
python batch_add_restaurants.py
"""

import json
import os

def load_database():
    """Load existing restaurant database"""
    db_path = "restaurants_db.json"
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            return json.load(f)
    else:
        return {"san_francisco": []}

def save_database(db):
    """Save restaurant database"""
    # Sort by name
    db["san_francisco"] = sorted(db["san_francisco"], key=lambda x: x["name"])

    with open("restaurants_db.json", 'w') as f:
        json.dump(db, f, indent=2)

def add_restaurant_interactive():
    """Interactively add restaurants"""
    db = load_database()
    existing_ids = {r["venue_id"] for r in db.get("san_francisco", [])}

    print("\n" + "=" * 60)
    print("Batch Restaurant Addition Tool")
    print("=" * 60)
    print(f"\nCurrent database has {len(db['san_francisco'])} restaurants")
    print("\nEnter restaurant details (or 'done' to finish)")
    print("-" * 60)

    added_count = 0

    while True:
        print("\n")
        name = input("Restaurant name (or 'done' to finish): ").strip()

        if name.lower() == 'done':
            break

        if not name:
            print("❌ Name cannot be empty")
            continue

        try:
            venue_id = input("Venue ID: ").strip()
            venue_id = int(venue_id)

            if venue_id in existing_ids:
                print(f"⚠️  Venue ID {venue_id} already exists in database")
                continue

        except ValueError:
            print("❌ Venue ID must be a number")
            continue

        neighborhood = input("Neighborhood: ").strip() or "San Francisco"
        cuisine = input("Cuisine type: ").strip() or "American"

        # Add restaurant
        restaurant = {
            "name": name,
            "venue_id": venue_id,
            "neighborhood": neighborhood,
            "cuisine": cuisine
        }

        db["san_francisco"].append(restaurant)
        existing_ids.add(venue_id)
        added_count += 1

        print(f"✅ Added: {name}")

    if added_count > 0:
        save_database(db)
        print(f"\n🎉 Successfully added {added_count} restaurant(s)!")
        print(f"📊 Total restaurants in database: {len(db['san_francisco'])}")
    else:
        print("\n No restaurants added")

def import_from_list():
    """Import restaurants from a prepared list"""
    print("\n" + "=" * 60)
    print("Import from CSV")
    print("=" * 60)
    print("\nPrepare a CSV file with format:")
    print("name,venue_id,neighborhood,cuisine")
    print("\nExample:")
    print("State Bird Provisions,339,Western Addition,American")
    print("Rich Table,1505,Hayes Valley,American")

    filename = input("\nEnter CSV filename (or press Enter to skip): ").strip()

    if not filename:
        return

    if not os.path.exists(filename):
        print(f"❌ File '{filename}' not found")
        return

    db = load_database()
    existing_ids = {r["venue_id"] for r in db.get("san_francisco", [])}
    added_count = 0
    skipped_count = 0

    with open(filename, 'r') as f:
        # Skip header if present
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.lower().startswith('name'):
                continue

            try:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 4:
                    print(f"⚠️  Skipping invalid line: {line}")
                    continue

                name, venue_id, neighborhood, cuisine = parts[0], int(parts[1]), parts[2], parts[3]

                if venue_id in existing_ids:
                    print(f"⚠️  Skipping duplicate: {name} (ID: {venue_id})")
                    skipped_count += 1
                    continue

                restaurant = {
                    "name": name,
                    "venue_id": venue_id,
                    "neighborhood": neighborhood,
                    "cuisine": cuisine
                }

                db["san_francisco"].append(restaurant)
                existing_ids.add(venue_id)
                added_count += 1
                print(f"✅ Added: {name}")

            except Exception as e:
                print(f"❌ Error processing line '{line}': {e}")
                continue

    if added_count > 0:
        save_database(db)
        print(f"\n🎉 Successfully imported {added_count} restaurant(s)!")
        print(f"⚠️  Skipped {skipped_count} duplicate(s)")
        print(f"📊 Total restaurants in database: {len(db['san_francisco'])}")
    else:
        print("\n No new restaurants imported")

def show_database():
    """Show current database"""
    db = load_database()
    restaurants = db.get("san_francisco", [])

    print("\n" + "=" * 60)
    print(f"Current Database ({len(restaurants)} restaurants)")
    print("=" * 60)

    for r in restaurants:
        print(f"\n{r['name']}")
        print(f"  ID: {r['venue_id']} | {r['neighborhood']} | {r['cuisine']}")

def main():
    """Main menu"""
    while True:
        print("\n" + "=" * 60)
        print("Restaurant Database Manager")
        print("=" * 60)
        print("\n1. Add restaurants one by one")
        print("2. Import from CSV file")
        print("3. View current database")
        print("4. Exit")

        choice = input("\nChoose an option (1-4): ").strip()

        if choice == '1':
            add_restaurant_interactive()
        elif choice == '2':
            import_from_list()
        elif choice == '3':
            show_database()
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-4")

if __name__ == "__main__":
    main()
