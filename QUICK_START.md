# Quick Start Checklist

Follow these steps to get your bot running in 5 minutes!

## ☐ Step 1: Install Python
- Go to https://python.org/downloads
- Download and install Python 3.8 or higher
- On Windows: Check "Add Python to PATH" during installation

## ☐ Step 2: Install Packages
Open Terminal (Mac/Linux) or Command Prompt (Windows) and run:
```bash
cd path/to/Resy
pip3 install -r requirements.txt
```

## ☐ Step 3: Set Up Credentials
1. Copy `.env.example` and rename it to `.env`
2. Open `.env` in a text editor
3. Add your Resy email and password:
   ```
   RESY_EMAIL=your.email@example.com
   RESY_PASSWORD=your_password_here
   ```
4. Save the file

## ☐ Step 4: Verify Setup
Run the setup checker:
```bash
python3 setup_check.py
```
Fix any issues it finds.

## ☐ Step 5: Configure Your Reservation
1. Open `example_book.py` in a text editor
2. Change these values:
   - `restaurant_name`: e.g., "Carbone"
   - `party_size`: e.g., 2
   - `reservation_date`: e.g., `date(2025, 11, 15)`
   - `preferred_times`: e.g., `["19:00", "19:30", "20:00"]`
3. Save the file

## ☐ Step 6: Run the Bot!

Choose one:

### Quick Book (book now)
```bash
python3 example_book.py
```

### Monitor Mode (keep checking)
```bash
python3 example_monitor.py
```
Press Ctrl+C to stop

### Scheduled Mode (start at specific time)
```bash
python3 example_scheduled.py
```
Edit the `START_TIME` in the file first!

---

## Time Conversion Chart

| 12-Hour | 24-Hour | 12-Hour | 24-Hour |
|---------|---------|---------|---------|
| 5:00 PM | 17:00   | 8:00 PM | 20:00   |
| 5:30 PM | 17:30   | 8:30 PM | 20:30   |
| 6:00 PM | 18:00   | 9:00 PM | 21:00   |
| 6:30 PM | 18:30   | 9:30 PM | 21:30   |
| 7:00 PM | 19:00   | 10:00 PM| 22:00   |
| 7:30 PM | 19:30   | 10:30 PM| 22:30   |

---

## Common Issues

**"Command not found: python3"**
→ Try `python` instead of `python3`

**"Authentication failed"**
→ Check your email/password in `.env`

**"No module named..."**
→ Run `pip3 install -r requirements.txt` again

**Restaurant not found**
→ Try different name, or run `python3 example_search.py` first

**Need more help?**
→ Read `BEGINNER_GUIDE.md` for detailed instructions

---

## Pro Tips

1. **Add a payment method** to your Resy account before running
2. **Know when reservations open** (usually midnight or 9 AM)
3. **Start early** - run the scheduled bot 1-2 minutes before release
4. **Multiple times** - always specify 3-4 preferred times
5. **Check intervals** - 2-5 seconds for competitive restaurants

Good luck! 🍽️
