# How to Find OpenTable Restaurant IDs

OpenTable uses restaurant IDs (RIDs) to identify each restaurant. Here's how to find them:

## Method 1: Browser Inspector (Recommended)

1. **Open the restaurant page on OpenTable**
   - Example: https://www.opentable.com/r/the-happy-crane-san-francisco

2. **Open Developer Tools**
   - Right-click anywhere on the page
   - Select "Inspect" or "Inspect Element"
   - OR press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)

3. **Search for the Restaurant ID**
   - Press `Ctrl+F` (Windows) / `Cmd+F` (Mac) to open search
   - Search for one of these terms:
     - `"rid"`
     - `"restaurantId"`
     - `"restaurant_id"`
     - `"RestaurantID"`

4. **Find the numeric ID**
   - Look for patterns like:
     - `"rid": "123456"`
     - `"restaurantId": 123456`
     - `data-rid="123456"`
   - The ID is usually a 5-7 digit number

## Method 2: Network Tab

1. **Open Developer Tools** (F12)
2. **Go to Network tab**
3. **Refresh the page**
4. **Look for API calls** containing:
   - `availability`
   - `restaurant`
   - `booking`
5. **Check the request URL or payload** for the restaurant ID

## Method 3: Page Source

1. **Right-click on the page** → **View Page Source**
2. **Search** (`Ctrl+F`) for:
   - `rid`
   - `restaurantId`
3. **Look for JSON data** with the restaurant ID

## Method 4: Booking Widget

1. **Click on a time slot** to start booking
2. **Open Developer Tools**
3. **Look at the Network tab** for the booking request
4. The restaurant ID will be in the API call

## Example for The Happy Crane:

1. Go to: https://www.opentable.com/r/the-happy-crane-san-francisco
2. Open Inspector (F12)
3. Search for "rid" or "restaurantId"
4. You should find something like: `"rid": "1234567"`

## Example for Four Kings:

1. Go to: https://www.opentable.com/r/four-kings-san-francisco
2. Open Inspector (F12)
3. Search for "rid" or "restaurantId"
4. You should find something like: `"rid": "7654321"`

## What to Look For:

The OpenTable restaurant ID is typically:
- **5-7 digits long**
- **Numeric only** (no letters)
- Found in JSON data structures
- Often labeled as `rid`, `restaurantId`, or `restaurant_id`

## Once You Have the IDs:

Add them to the database using the app's "Add Restaurant" feature:
- Restaurant Name: The Happy Crane
- Venue ID: [the ID you found]
- Neighborhood: Hayes Valley
- Cuisine: Chinese
- Platform: **opentable**

---

**Note:** OpenTable's website structure may change, so if these methods don't work, try looking in different parts of the page source or network requests.
