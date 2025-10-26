# How to Find Resy Venue IDs - Easy Methods

There are 3 easy ways to get venue IDs from Resy.com:

## 🔖 Method 1: Browser Bookmarklet (EASIEST - Recommended!)

**One-time setup:**
1. Right-click your browser's bookmarks bar
2. Click "Add page" or "Add bookmark"
3. Name it: `Get Resy Venue ID`
4. For the URL, paste this entire code:

```javascript
javascript:(function(){let venueId=null;try{const scripts=document.querySelectorAll('script');for(let script of scripts){const text=script.textContent;if(text.includes('venue_id')||text.includes('"id"')){const match1=text.match(/"venue_id["\s:]+(\d+)/);const match2=text.match(/"id["\s:]+{\s*"resy["\s:]+(\d+)/);const match3=text.match(/venue\/(\d+)/);if(match1){venueId=match1[1];break}else if(match2){venueId=match2[1];break}else if(match3){venueId=match3[1];break}}}}catch(e){}if(venueId){alert('Venue ID: '+venueId+'\n\nCopied to clipboard!');navigator.clipboard.writeText(venueId)}else{alert('Could not find venue ID on this page.\n\nMake sure you are on a Resy restaurant page.')}})();
```

5. Save the bookmark

**To use:**
1. Go to ANY restaurant on Resy.com
2. Click the bookmark
3. Venue ID appears in a popup AND is copied to clipboard!
4. Paste into your app (Ctrl+V or Cmd+V)

**Example:**
- Go to: https://resy.com/cities/sf/venues/flour-water
- Click the "Get Resy Venue ID" bookmark
- See popup: "Venue ID: 6291"
- It's already copied - just paste it!

---

## 💻 Method 2: Browser Console (No Setup Needed)

**Use this if you don't want to create a bookmarklet:**

1. Go to any restaurant page on Resy.com
2. Press **F12** (or right-click → Inspect)
3. Click the **"Console"** tab
4. Paste this code and press Enter:

```javascript
let venueId = null;
const scripts = document.querySelectorAll('script');
for (let script of scripts) {
    const text = script.textContent;
    if (text.includes('venue_id') || text.includes('"id"')) {
        const match1 = text.match(/"venue_id["\s:]+(\d+)/);
        const match2 = text.match(/"id["\s:]+{\s*"resy["\s:]+(\d+)/);
        const match3 = text.match(/venue\/(\d+)/);
        if (match1) {
            venueId = match1[1];
            break;
        } else if (match2) {
            venueId = match2[1];
            break;
        } else if (match3) {
            venueId = match3[1];
            break;
        }
    }
}
if (venueId) {
    console.log('Venue ID:', venueId);
    navigator.clipboard.writeText(venueId);
    alert('Venue ID: ' + venueId + '\n\nCopied to clipboard!');
} else {
    console.log('Could not find venue ID');
}
```

5. Venue ID is shown and copied to clipboard!

---

## 🐍 Method 3: Python Script (For Multiple URLs)

**Use this to process many restaurants at once:**

**Requirements:**
```bash
pip install requests pyperclip
```

**Run:**
```bash
python get_venue_ids.py
```

**Features:**
- Paste multiple Resy URLs (one per line)
- Automatically extracts all venue IDs
- Exports to CSV if you want
- Detects URLs from clipboard automatically

**Example:**
```
$ python get_venue_ids.py

Paste Resy restaurant URLs (one per line)
Press Enter twice when done
------------------------------------------------------------
https://resy.com/cities/sf/venues/flour-water
https://resy.com/cities/sf/venues/state-bird-provisions
https://resy.com/cities/sf/venues/nopa
<press Enter twice>

Found 3 venue ID(s):

  Flour Water
  Venue ID: 6291

  State Bird Provisions
  Venue ID: 187

  Nopa
  Venue ID: 108
```

---

## 📱 Works on Mobile Too!

The **console method** works on mobile browsers:

**iPhone (Safari):**
1. Enable Developer menu: Settings → Safari → Advanced → Web Inspector
2. Connect to a computer with Safari
3. Use the console from your computer

**Android (Chrome):**
1. Open Chrome Developer Tools on your computer
2. Enable USB debugging on your phone
3. Inspect the mobile page from your computer
4. Use the console

**Or just use the desktop version - it's much easier!**

---

## Quick Reference

| Method | Setup Time | Ease of Use | Best For |
|--------|------------|-------------|----------|
| Bookmarklet | 1 minute | ⭐⭐⭐⭐⭐ | Single restaurants, everyday use |
| Console | None | ⭐⭐⭐⭐ | Quick one-time lookups |
| Python Script | 2 minutes | ⭐⭐⭐ | Batch processing many URLs |

---

## Tips

1. **Bookmarklet is recommended** - Set it up once, use forever
2. **Save to your phone** - Add the bookmarklet to mobile browser too
3. **Share with friends** - Send them the bookmarklet code
4. **Works on all restaurants** - Not just SF, works anywhere on Resy

---

## Troubleshooting

**"Could not find venue ID":**
- Make sure you're on a restaurant page (not search results)
- URL should look like: `resy.com/cities/[city]/venues/[restaurant-name]`
- Try refreshing the page and running again

**Bookmarklet not working:**
- Make sure you copied the ENTIRE javascript code (it's long!)
- Should start with `javascript:(function(){`
- Some browsers don't allow bookmarklets - use console method instead

**Python script errors:**
- Install dependencies: `pip install requests pyperclip`
- Make sure URLs have `https://` at the beginning
- Check your internet connection

---

Happy venue hunting! 🎯
