# Complete Beginner's Guide to Running the Resy Bot

Welcome! This guide will help you set up and run the Resy reservation bot, even if you've never coded before.

## Step 1: Install Python

### For Mac:
1. Open **Terminal** (press Cmd+Space, type "Terminal", press Enter)
2. Copy and paste this command, then press Enter:
   ```bash
   python3 --version
   ```
3. If you see something like "Python 3.8.x" or higher, you're good! Skip to Step 2.
4. If not, install Python:
   - Go to https://www.python.org/downloads/
   - Click "Download Python"
   - Open the downloaded file and follow the installer

### For Windows:
1. Open **Command Prompt** (press Windows key, type "cmd", press Enter)
2. Type this and press Enter:
   ```bash
   python --version
   ```
3. If you see "Python 3.8.x" or higher, you're good! Skip to Step 2.
4. If not, install Python:
   - Go to https://www.python.org/downloads/
   - Click "Download Python"
   - **Important**: When installing, check the box "Add Python to PATH"
   - Click "Install Now"

### For Linux:
Python is usually pre-installed. Open Terminal and type:
```bash
python3 --version
```

## Step 2: Open the Project Folder

### Mac/Linux:
1. Open **Terminal**
2. Type these commands one at a time:
   ```bash
   cd ~/Resy
   ```
   (If you cloned the project elsewhere, navigate to that location instead)

### Windows:
1. Open **Command Prompt** or **PowerShell**
2. Type:
   ```bash
   cd C:\Users\YourUsername\Resy
   ```
   (Replace "YourUsername" with your actual Windows username)

**Tip**: You can drag the Resy folder into Terminal/Command Prompt to automatically type the path!

## Step 3: Install Required Packages

These are the tools the bot needs to work. In your Terminal/Command Prompt, type:

### Mac/Linux:
```bash
pip3 install -r requirements.txt
```

### Windows:
```bash
pip install -r requirements.txt
```

This will take a minute or two. You'll see lots of text scrolling - that's normal!

## Step 4: Set Up Your Resy Credentials

Now we need to tell the bot your Resy account information.

1. **Find the `.env.example` file** in your Resy folder
2. **Make a copy** and name it `.env` (just `.env`, no `.example`)
   - On Mac: Right-click the file → Duplicate → Rename to `.env`
   - On Windows: Right-click → Copy → Paste → Rename to `.env`

3. **Open `.env` in a text editor**:
   - Mac: Use TextEdit (right-click file → Open With → TextEdit)
   - Windows: Use Notepad (right-click file → Open With → Notepad)
   - Or use any text editor like VS Code, Sublime Text, etc.

4. **Fill in your information**:
   ```env
   RESY_EMAIL=your.email@example.com
   RESY_PASSWORD=your_password_here
   ```

   Replace:
   - `your.email@example.com` with your actual Resy email
   - `your_password_here` with your actual Resy password

5. **Save the file** (File → Save or Ctrl+S / Cmd+S)

**Important**:
- Keep this file secure - it contains your password!
- The `.gitignore` file ensures it won't be uploaded to GitHub
- Don't share this file with anyone

## Step 5: Test That Everything Works

Let's make sure the bot can connect to Resy.

### Mac/Linux:
```bash
python3 example_search.py
```

### Windows:
```bash
python example_search.py
```

**What you should see**:
- "Logging in as your.email@example.com"
- "Login successful"
- A list of restaurants

**If you see errors**:
- "Authentication failed" → Check your email/password in `.env`
- "No module named..." → Re-run the pip install command from Step 3
- Other errors? See Troubleshooting section below

## Step 6: Configure Your Reservation

Now let's set up what reservation you want to book!

1. **Open `example_book.py`** in your text editor

2. **Find these lines** (around line 20-30):
   ```python
   reservation = ReservationConfig(
       restaurant_name="Carbone",
       party_size=2,
       reservation_date=date(2025, 11, 15),
       preferred_times=[
           "19:00",
           "19:30",
           "20:00",
           "20:30"
       ],
       location="ny",
       auto_accept_any_time=False
   )
   ```

3. **Change the values**:
   - `restaurant_name`: The name of the restaurant (keep the quotes)
   - `party_size`: How many people (just a number, no quotes)
   - `reservation_date`: Year, Month, Day in this format: `date(2025, 11, 15)`
   - `preferred_times`: Times you want (24-hour format: "19:00" = 7:00 PM)
   - `location`: City code ("ny", "la", "sf", "boston", "dc", etc.)
   - `auto_accept_any_time`:
     - `False` = only book if your preferred times are available
     - `True` = book any available time if preferred times are full

4. **Save the file**

### Time Format Guide:
- 6:00 PM = "18:00"
- 6:30 PM = "18:30"
- 7:00 PM = "19:00"
- 7:30 PM = "19:30"
- 8:00 PM = "20:00"
- 8:30 PM = "20:30"
- 9:00 PM = "21:00"

## Step 7: Run the Bot!

Now you have three options depending on what you need:

### Option A: Book Right Now (if reservations are already available)

**Mac/Linux:**
```bash
python3 example_book.py
```

**Windows:**
```bash
python example_book.py
```

This will attempt to book immediately. Use this when:
- Reservations are already open
- You just want to try booking once

---

### Option B: Keep Checking Until Available (monitor mode)

**Mac/Linux:**
```bash
python3 example_monitor.py
```

**Windows:**
```bash
python example_monitor.py
```

This will check every 5 seconds and book as soon as a spot opens. Use this when:
- You're hunting for cancellations
- The restaurant is fully booked but you want to catch a cancellation
- You want the bot to keep trying

**To stop**: Press `Ctrl+C` (hold Ctrl and press C)

---

### Option C: Start at a Specific Time (scheduled mode)

**Mac/Linux:**
```bash
python3 example_scheduled.py
```

**Windows:**
```bash
python example_scheduled.py
```

This will wait until a specific time (like midnight) then start checking. Use this when:
- Reservations open at a specific time (usually midnight or 9 AM)
- You want to be ready the moment reservations are released

**Before running**, edit `example_scheduled.py` and change:
```python
START_TIME = "00:00"  # Change to when reservations open
```

Common times:
- Midnight = "00:00"
- 9:00 AM = "09:00"
- 10:00 AM = "10:00"

**To cancel**: Press `Ctrl+C`

## What to Expect When Running

### If Successful:
```
==========================================================
RESERVATION BOOKED SUCCESSFULLY!
Restaurant: Carbone
Date: 2025-11-15
Time: 7:00 PM
Party Size: 2
==========================================================
```

You'll also receive an email confirmation from Resy!

### If No Availability:
```
No availability found for preferred times
```

Try:
- Different dates
- Different times
- Setting `auto_accept_any_time=True`
- Using monitor mode to catch cancellations

### If Restaurant Not Found:
```
Could not find restaurant: [name]
```

Try:
- Different spelling
- Just the restaurant name without location (e.g., "Carbone" not "Carbone NYC")
- Running `example_search.py` first to see what names work

## Using the Simple Command Line Tool

Once you're comfortable, you can use the command line tool for quick bookings:

```bash
python3 book_reservation.py "Restaurant Name" 2 2025-11-15 "19:00,19:30,20:00"
```

Format:
```bash
python3 book_reservation.py "RESTAURANT" PARTY_SIZE YYYY-MM-DD "TIME1,TIME2,TIME3"
```

Examples:
```bash
# Book for 2 at Carbone on Nov 15
python3 book_reservation.py "Carbone" 2 2025-11-15 "19:00,19:30,20:00"

# Monitor for cancellations
python3 book_reservation.py "Don Angie" 4 2025-12-01 "19:00,20:00" --monitor

# Schedule for midnight
python3 book_reservation.py "4 Charles" 2 2025-11-20 "19:00" --schedule "00:00"

# Accept any time
python3 book_reservation.py "Carbone" 2 2025-11-15 "19:00,20:00" --any-time
```

## Tips for Success

### 1. Know When Reservations Open
Most restaurants release reservations at specific times:
- **30 days in advance at midnight** (12:00 AM)
- **30 days in advance at 9:00 AM**
- Some restaurants have different schedules

**How to find out**:
- Call the restaurant and ask
- Check their website
- Try booking manually on Resy and see when dates become available

### 2. Be Ready Early
Start the bot 1-2 minutes before the release time.

### 3. For Very Popular Restaurants
Use the scheduled mode:
1. Edit `example_scheduled.py`
2. Set `START_TIME` to when reservations open
3. Run it and leave your computer on
4. The bot will start checking at exactly that time

### 4. Payment Method
**Important**: Make sure you have a credit card saved on your Resy account!
- Log into Resy.com
- Go to your account settings
- Add a payment method
- The bot will automatically use it

### 5. Check Intervals
In monitoring mode:
- **Very competitive** (Carbone, Don Angie): Check every 2-3 seconds
- **Normal popularity**: Check every 5-10 seconds
- **Cancellation hunting**: Check every 30-60 seconds

Edit the `check_interval` in the script to change this.

## Troubleshooting

### "Command not found: python3"
Try `python` instead of `python3`

### "No module named 'requests'"
Run the pip install command again:
```bash
pip3 install -r requirements.txt
```

### "Authentication failed"
1. Check your `.env` file
2. Make sure email and password are correct
3. Try logging into Resy.com manually to verify your credentials

### ".env file not found"
1. Make sure you created `.env` (not `.env.txt` or `.env.example`)
2. Make sure it's in the same folder as the Python scripts
3. On Mac, you may need to show hidden files (Cmd+Shift+.)

### "Rate limited" or "Too many requests"
You're checking too frequently. Increase the `check_interval` to 10-30 seconds.

### "Booking failed"
Common reasons:
- Someone else booked the slot first (very common for popular restaurants)
- Reservation window isn't open yet
- No payment method on your Resy account
- Restaurant requires special booking conditions

### Bot runs but doesn't find the restaurant
1. Run `example_search.py` first
2. Try different name variations
3. Make sure the `location` code is correct

## Getting Help

If you're stuck:
1. Check the main `README.md` file
2. Look at the error message - it often tells you what's wrong
3. Make sure you completed all steps above
4. Check that your `.env` file is set up correctly

## Important Reminders

- ✓ This bot is for **personal use only** - book for yourself, not to resell
- ✓ Always **honor your reservations** - don't no-show
- ✓ Use **reasonable check intervals** - don't hammer Resy's servers
- ✓ Keep your **`.env` file secure** - never share it
- ✓ Make sure you have a **payment method** saved on Resy

## Next Steps

Once you're comfortable:
1. Try different restaurants
2. Experiment with monitoring mode for cancellations
3. Set up email notifications (see main README.md)
4. Use the CLI tool for quick bookings

Good luck booking your reservations! 🍽️
