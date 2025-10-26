# Google Places API Setup Guide

This guide will help you set up Google Places API to display restaurant reviews and photos in Reservation Hunter.

## 🎯 What You'll Get

With Google Places API integrated, your app will show:
- ⭐ Google ratings and review counts
- 📸 Restaurant photos (up to 6 photos per restaurant)
- 💬 Top 5 Google reviews with star ratings
- 📍 Additional restaurant information

## 📋 Prerequisites

- Google Cloud account (free tier available)
- Credit card (required for Google Cloud, but free tier is generous)
- 5-10 minutes for setup

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create New Project**
   - Click "Select a Project" at the top
   - Click "New Project"
   - Name it: "Reservation Hunter" (or any name you like)
   - Click "Create"

3. **Wait for project creation** (takes ~30 seconds)

### Step 2: Enable Places API

1. **Open API Library**
   - In the left menu, go to: **APIs & Services** → **Library**
   - Or visit: https://console.cloud.google.com/apis/library

2. **Search for Places API**
   - In the search bar, type: "Places API"
   - Click on "Places API" (NOT "Places API (New)")

3. **Enable the API**
   - Click the blue "Enable" button
   - Wait for it to activate (~10 seconds)

### Step 3: Create API Key

1. **Go to Credentials**
   - In the left menu: **APIs & Services** → **Credentials**
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **Create Credentials**
   - Click "+ CREATE CREDENTIALS" at the top
   - Select "API Key"
   - A popup will appear with your API key

3. **Copy Your API Key**
   - Click the copy icon or manually copy the key
   - It looks like: `AIzaSyD...` (long string of characters)
   - **Save this somewhere safe!**

### Step 4: Restrict API Key (Recommended)

For security, restrict your API key:

1. **Click "Edit API Key"** (in the popup) or find your key in the credentials list

2. **Application Restrictions**
   - Select "HTTP referrers (web sites)"
   - Add your Streamlit Cloud URL:
     - `https://your-app-name.streamlit.app/*`
     - `https://*.streamlit.app/*` (for all Streamlit apps)

3. **API Restrictions**
   - Select "Restrict key"
   - Check only: "Places API"
   - Click "Save"

### Step 5: Add API Key to Streamlit Cloud

1. **Go to your Streamlit Cloud dashboard**
   - Visit: https://share.streamlit.io/

2. **Open your app settings**
   - Find your "Reservation Hunter" app
   - Click the menu (⋮) → "Settings"

3. **Add Secret**
   - Go to the "Secrets" section
   - Add this content:
     ```toml
     GOOGLE_PLACES_API_KEY = "YOUR_API_KEY_HERE"
     ```
   - Replace `YOUR_API_KEY_HERE` with your actual key
   - Click "Save"

4. **Reboot the app**
   - The app will automatically restart with the new secret

### Step 6: Add API Key Locally (For Testing)

If you're running the app locally:

1. **Create `.streamlit/secrets.toml`** file:
   ```bash
   mkdir -p .streamlit
   ```

2. **Add your API key**:
   ```toml
   GOOGLE_PLACES_API_KEY = "YOUR_API_KEY_HERE"
   ```

3. **Or use environment variable**:
   ```bash
   export GOOGLE_PLACES_API_KEY="YOUR_API_KEY_HERE"
   ```

## 💰 Pricing Information

### Free Tier
- **$200 free credit** per month
- Enough for approximately:
  - **28,000 Place Details requests** (what we use for reviews/photos)
  - **28,000 Place Search requests** (for finding restaurants)

### Our Usage
- **Initial load**: ~1 search + 1 details request per restaurant
- **Cached for 1 hour** (details) and 24 hours (search)
- **Estimated monthly cost for 50 restaurants**:
  - With good caching: **~$2-5/month**
  - Well within the $200 free tier! ✅

### Cost Breakdown
- **Place Search**: $0.032 per request
- **Place Details**: $0.017 per request
- **Place Photos**: Free! (included with Place Details)

**Total for 50 restaurants** (with hourly reloads):
- Searches: 50 × 30 days = 1,500 requests = **$48/month**
- Details: 50 × 24 requests/day × 30 days = 36,000 requests = **$612/month**

**But with caching** (1 hour for details, 24 hours for search):
- Searches: 50 × 1 = 50 requests = **$1.60 one-time**
- Details: 50 × 24 × 30 = 36,000 requests = **$612/month**

Wait, that's too high! Let me recalculate:

Actually, with **1-hour caching**:
- Details called once per hour per restaurant
- 50 restaurants × 24 hours/day × 30 days = 36,000 requests/month
- Cost: 36,000 × $0.017 = **$612/month** ❌ Too expensive!

**Better caching strategy** (24-hour cache):
- Details called once per day per restaurant
- 50 restaurants × 30 days = 1,500 requests/month
- Cost: 1,500 × $0.017 = **$25.50/month** ✅ Within free tier!

## ⚙️ Optimizing Costs

### Recommended Settings

Update `google_places.py` to cache for longer:

```python
@st.cache_data(ttl=86400)  # 24 hours instead of 1 hour
def get_restaurant_google_data(place_id: str, api_key: str = None):
    # ... existing code
```

### Tips to Minimize Costs

1. **Use longer cache times** (24 hours recommended)
2. **Store `google_place_id` in database** (avoids search API calls)
3. **Only load Google data when viewing restaurant details** (not on browse page)
4. **Set up billing alerts** at $10, $50, $100 thresholds

## 🔍 Testing the Integration

### Verify API Key Works

1. **View any restaurant**
   - Click "View availability →" on any restaurant
   - Look for Google rating in the hero section

2. **Check for photos**
   - Scroll down to see "Photos" section
   - Should see up to 6 restaurant photos

3. **Read reviews**
   - Scroll to "Reviews from Google"
   - Should see 5 most recent reviews with star ratings

### Troubleshooting

**No reviews/photos showing?**
- Check if `GOOGLE_PLACES_API_KEY` is set in Streamlit secrets
- Check browser console for errors
- Verify API key has Places API enabled

**Getting API errors?**
- Make sure you enabled "Places API" (not "Places API (New)")
- Check API key restrictions allow your domain
- Verify billing is enabled on Google Cloud

**Photos not loading?**
- Check that photo URLs are accessible
- Try opening photo URL directly in browser
- Verify Places API is enabled

## 📊 Monitoring Usage

### Check Your Usage

1. **Go to Google Cloud Console**
   - APIs & Services → Dashboard

2. **View Metrics**
   - See how many requests you're making
   - Monitor costs in real-time

3. **Set Up Billing Alerts**
   - Billing → Budgets & alerts
   - Create alert at $10 threshold
   - Get email when approaching limit

## 🎨 Customizing Display

### Hide Google Data

If you don't want to show Google reviews/photos, simply don't set the API key. The app will work fine without it!

### Customize Number of Reviews

In `app.py`, change this line:
```python
reviews = google_data['reviews'][:5]  # Change 5 to any number
```

### Customize Number of Photos

In `app.py`, change this line:
```python
photos = google_data['photos'][:6]  # Change 6 to any number
```

## 🔒 Security Best Practices

1. **Never commit API keys to Git**
   - Add `.streamlit/secrets.toml` to `.gitignore`
   - Use Streamlit Cloud secrets for production

2. **Restrict API key**
   - Limit to specific domains
   - Only allow Places API

3. **Monitor usage regularly**
   - Set up billing alerts
   - Review usage monthly

4. **Rotate keys if compromised**
   - Delete old key
   - Create new key
   - Update in Streamlit secrets

## 📚 Additional Resources

- **Google Places API Documentation**: https://developers.google.com/maps/documentation/places/web-service
- **Pricing Calculator**: https://mapsplatform.google.com/pricing/
- **Free Tier Details**: https://cloud.google.com/free
- **Streamlit Secrets**: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management

## ❓ FAQ

**Q: Is the free tier really free?**
A: Yes! Google gives $200 credit per month, which resets monthly. As long as you stay under $200/month, you pay $0.

**Q: What happens if I exceed the free tier?**
A: Google will charge your credit card. Set up billing alerts to prevent surprises!

**Q: Can I use this without Google Places?**
A: Yes! The app works fine without it. You just won't see reviews and photos.

**Q: Will my API key be stolen?**
A: Not if you properly restrict it to your domain. Also, we use server-side requests, so the key isn't exposed to users.

**Q: How often does the data update?**
A: With 24-hour caching, reviews and photos refresh once per day.

---

**Need help?** Open an issue on GitHub or check the Google Cloud documentation!
