# Expanding Your Restaurant Database

Since Resy blocks automated API access, here are the best ways to expand your restaurant database:

## Option 1: Use the Web App "Add Restaurant" Tab (Easiest)

1. Open your Streamlit app
2. Go to the "Add Restaurant" tab
3. Enter restaurant details one by one
4. The app will automatically add them to the database

**How to find a Venue ID:**
1. Go to https://resy.com/cities/sf
2. Click on the restaurant you want
3. Right-click on the page and select "Inspect" (or press F12)
4. Press Ctrl+F (or Cmd+F) and search for `"venue_id"`
5. You'll see something like `"venue_id": 339` - that's your venue ID!

## Option 2: Batch Import from CSV (Fastest for Many Restaurants)

1. Edit the `sf_restaurants_sample.csv` file
2. Add restaurants in the format: `Name,VenueID,Neighborhood,Cuisine`
3. Run the batch import script:
   ```bash
   python batch_add_restaurants.py
   ```
4. Choose option 2 to import from CSV

**Example CSV format:**
```csv
State Bird Provisions,1505,Western Addition,American
Rich Table,3007,Hayes Valley,American
Zuni Cafe,795,Hayes Valley,Mediterranean
```

## Option 3: Interactive Command Line Tool

Run the batch script and choose option 1 to add restaurants interactively:

```bash
python batch_add_restaurants.py
```

This will prompt you for each restaurant's details.

## Finding Venue IDs - Detailed Steps

### Method 1: From Restaurant Page
1. Go to https://resy.com
2. Search for the restaurant
3. Click on the restaurant to open its page
4. Right-click anywhere and select "Inspect" (Chrome/Firefox) or "Inspect Element" (Safari)
5. In the developer tools, press Ctrl+F (Cmd+F on Mac)
6. Search for `venue_id`
7. You'll find lines like `"id":{"resy":339}` or `"venue_id":339`
8. The number is your venue ID!

### Method 2: From URL (Sometimes)
Some restaurant URLs include the venue ID:
- URL might look like: `https://resy.com/cities/sf/restaurant-name?venue_id=339`
- Or in the page source you might see: `resy://venue/339`

## Tips for Building Your Database

1. **Start with your favorites** - Add restaurants you actually want to book
2. **Add as you go** - When you discover a restaurant on Resy, add it to your database
3. **Share with others** - If you and your boyfriend both use the app, you can each add restaurants
4. **Neighborhoods** - Group by neighborhood (e.g., "Mission", "Hayes Valley", "Nob Hill")
5. **Cuisine types** - Use consistent categories (e.g., "Italian", "Japanese", "American")

## Popular SF Restaurants to Add

Here are some popular SF restaurants to look up on Resy:

### Michelin-Starred:
- Atelier Crenn (Cow Hollow) - French
- Saison (SoMa) - American
- Benu (SoMa) - Asian Fusion
- Quince (Jackson Square) - Italian
- Lazy Bear (Mission) - American
- Californios (Mission) - Mexican
- State Bird Provisions (Western Addition) - American
- Rich Table (Hayes Valley) - American

### Popular Casual:
- Nopa (Western Addition) - American
- Beretta (Mission) - Italian
- Trick Dog (Mission) - American/Bar
- Tartine Manufactory (Mission) - Bakery/Cafe
- Zazie (Cole Valley) - French/Brunch
- Nopalito (Western Addition) - Mexican

### Classic SF:
- Zuni Cafe (Hayes Valley) - Mediterranean
- Foreign Cinema (Mission) - Mediterranean
- Kokkari (Financial District) - Greek
- Boulevard (Embarcadero) - American
- Gary Danko (Fisherman's Wharf) - American

## Current Database Status

Your database currently has these restaurants:
- Izakaya Rintaro (339) - Mission, Japanese
- State Bird Provisions (1505) - Western Addition, American
- Zuni Cafe (795) - Hayes Valley, Mediterranean
- Foreign Cinema (856) - Mission, Mediterranean
- SPQR (1740) - Pacific Heights, Italian
- Flour + Water (305) - Mission, Italian
- Nopa (494) - Western Addition, American
- Rich Table (3007) - Hayes Valley, American
- Liholiho Yacht Club (4552) - Nob Hill, Hawaiian
- The Progress (4551) - Western Addition, American
- Tartine Manufactory (7982) - Mission, Bakery
- Che Fico (24965) - Nopa, Italian
- Lord Stanley (6906) - Polk, American
- Sorrel (8540) - Pacific Heights, Italian
- Cotogna (1739) - Jackson Square, Italian

That's 15 restaurants to start with!

## Need Help?

If you're having trouble finding venue IDs or adding restaurants:
1. Use the web app's "Add Restaurant" tab - it's the easiest method
2. Start with the sample CSV file provided
3. Add restaurants gradually as you discover them on Resy

Happy booking! 🍽️
