# Multi-Platform Reservation System

Your Resy Bot now supports **both Resy and OpenTable**! Book reservations on either platform from a single app.

## 🎯 Features

- **Dual Platform Support**: Book on Resy OR OpenTable
- **Platform Badges**: See which platform each restaurant uses
- **Unified Interface**: Same booking flow for both platforms
- **Platform Filtering**: Filter restaurants by platform
- **Single Login**: Use your credentials for both platforms

## 🚀 How It Works

### Adding Restaurants

When you add a restaurant, you now specify which platform it uses:

1. Go to **"Add Restaurant"** tab
2. Fill in restaurant details
3. **Select Platform**: Choose "resy" or "opentable"
4. Click "Add Restaurant"

### Platform Indicators

Restaurants now show platform badges:
- **[RESY]** - Red badge for Resy restaurants
- **[OPENTABLE]** - Dark red badge for OpenTable restaurants

You'll see these badges:
- In the restaurant dropdown menus
- In the restaurant database list
- When viewing restaurant details

### Booking Process

The app automatically uses the correct platform:
1. Select any restaurant (Resy or OpenTable)
2. Choose your booking details
3. Click "Book Now"
4. The app routes to the correct platform automatically!

## 📱 Platform Credentials

### Option 1: Same Email for Both
If you use the same email for Resy and OpenTable:
- Just login once with your email/password
- The app will try both platforms with the same credentials

### Option 2: Different Emails
Currently, the app uses one set of credentials. If you have different accounts:
- Login with your Resy credentials to book Resy restaurants
- Logout and login with OpenTable credentials to book OpenTable restaurants

**Future Enhancement**: Support for separate platform credentials in one session

## 🔧 Technical Details

### Platform Detection

The database now includes a `platform` field:

```json
{
  "name": "Flour + Water",
  "venue_id": 6291,
  "neighborhood": "Mission",
  "cuisine": "Italian",
  "platform": "resy"
}
```

###Files Modified:
- `app.py` - Updated UI with platform support
- `restaurants_db.json` - Added platform field
- `opentable_client.py` - New OpenTable API client
- `unified_bot.py` - Platform-agnostic booking interface

## ⚠️ Important Notes About OpenTable

### API Limitations

**OpenTable does not provide a public API.** The OpenTable client (`opentable_client.py`) uses reverse-engineered endpoints that:

1. **May break at any time** if OpenTable changes their API
2. **May trigger bot detection** and account restrictions
3. **May require CAPTCHA solving** for some actions
4. **Are not officially supported** by OpenTable

### Recommendations

For OpenTable restaurants, consider:
- **Testing thoroughly** before relying on automated booking
- **Having a backup plan** (manual booking)
- **Using sparingly** to avoid account issues
- **Keeping credentials separate** if possible

### Official Alternatives

OpenTable offers:
- **Widget/iframe embedding** for websites
- **Partnership programs** for commercial use
- **Manual booking** through their website/app

## 🎨 UI Updates

### Restaurant Dropdown
Before:
```
Flour + Water - Mission (Italian)
```

After:
```
Flour + Water - Mission (Italian) [RESY]
```

### Database Display
Restaurants now show colored platform badges:
- 🔴 **RESY** - Resy restaurants
- 🔴 **OPENTABLE** - OpenTable restaurants

### Add/Edit Forms
New platform selector in both forms:
- Dropdown to choose "resy" or "opentable"
- Default: "resy"
- Shown in edit form with current platform pre-selected

## 📊 Database Migration

### Existing Restaurants

All existing restaurants default to "resy" platform. To update:

1. Go to **"Add Restaurant"** → **"Edit/Delete"** tab
2. Select the restaurant
3. Change the platform dropdown to "opentable" if needed
4. Click "Update Restaurant"

### Bulk Updates

To update multiple restaurants, edit `restaurants_db.json` directly:

```json
{
  "san_francisco": [
    {
      "name": "Restaurant Name",
      "venue_id": 12345,
      "neighborhood": "Neighborhood",
      "cuisine": "Cuisine",
      "platform": "opentable"  ← Add this field
    }
  ]
}
```

## 🔮 Future Enhancements

Potential improvements:
1. **Separate credentials** for each platform in one session
2. **Platform-specific filters** in search
3. **Multi-platform search** for the same restaurant
4. **Platform comparison** (pricing, availability)
5. **Additional platforms** (Yelp Reservations, etc.)

## 🐛 Troubleshooting

### "Authentication failed" for OpenTable
- OpenTable's API may be different than expected
- Check that you're using correct OpenTable credentials
- Try booking manually to verify account works

### Restaurant not booking
- Verify the venue ID is correct for that platform
- Resy and OpenTable use different IDs for the same restaurant
- Check the platform badge matches where you found the ID

### Platform shows wrong
- Edit the restaurant and update the platform field
- Make sure you're using the correct venue ID for that platform

## 📞 Support

For issues:
1. Check that platform field is correct in database
2. Verify venue ID matches the platform
3. Test with a known-working restaurant first
4. Check authentication status in sidebar

---

**Note**: This is an experimental feature. OpenTable support is reverse-engineered and may have limitations. Always have a backup plan for important reservations!
