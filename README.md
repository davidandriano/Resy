# Resy Reservation Bot

An automated reservation booking bot for Resy.com that helps you secure hard-to-get restaurant reservations. Configure your desired restaurant, date, party size, and preferred times, and let the bot handle the rest!

## Features

- **Automatic Booking**: Books reservations as soon as they become available
- **Payment Support**: Handles restaurants requiring credit card to hold reservations
- **Flexible Scheduling**: Book immediately, monitor continuously, or schedule for specific times
- **Smart Monitoring**: Continuously checks for availability with configurable intervals
- **Multiple Time Preferences**: Specify multiple preferred time slots
- **Email Notifications**: Get notified when reservations are successfully booked
- **Comprehensive Logging**: Track all attempts and bookings

## Use Cases

1. **High-Demand Restaurants**: Monitor and book the moment reservations open (e.g., midnight releases)
2. **Cancellation Hunting**: Continuously check for cancellations at fully-booked restaurants
3. **Last-Minute Booking**: Quick booking when you find availability
4. **Scheduled Booking**: Set it to start checking exactly when reservations are released

## Installation

### Prerequisites

- Python 3.8 or higher
- A Resy account
- Payment method added to your Resy account (for restaurants requiring cards)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Resy
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure credentials**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Resy credentials:
   ```env
   RESY_EMAIL=your.email@example.com
   RESY_PASSWORD=your_password_here
   ```

4. **Make example scripts executable** (optional):
   ```bash
   chmod +x example_*.py
   ```

## Quick Start

### 1. Search for Restaurants

First, find your target restaurant and check availability:

```bash
python example_search.py
```

Edit the script to search for your restaurant and check what times are available.

### 2. Book Immediately

If reservations are already available, use the quick book script:

```bash
python example_book.py
```

Edit `example_book.py` to configure:
- Restaurant name
- Party size
- Reservation date
- Preferred times

### 3. Monitor Continuously

For high-demand restaurants, monitor continuously and book as soon as availability appears:

```bash
python example_monitor.py
```

This will check every 5 seconds and book immediately when a slot opens.

### 4. Schedule for Release Time

If you know when reservations are released (e.g., midnight, 9 AM), schedule the bot to start monitoring at that exact time:

```bash
python example_scheduled.py
```

Edit the `START_TIME` variable to match when reservations are released.

## Usage Examples

### Example 1: Book Carbone for 2 on a specific date

```python
from datetime import date
from bot import ResyBot
from config import ReservationConfig, load_settings

settings = load_settings()
bot = ResyBot(settings)

reservation = ReservationConfig(
    restaurant_name="Carbone",
    party_size=2,
    reservation_date=date(2025, 11, 15),
    preferred_times=["19:00", "19:30", "20:00"],
    location="ny"
)

if bot.authenticate():
    bot.quick_book(reservation)
```

### Example 2: Monitor for cancellations

```python
# Will check every 30 seconds for cancellations
bot.monitor_reservation(reservation, check_interval=30)
```

### Example 3: Accept any available time

```python
reservation = ReservationConfig(
    restaurant_name="Don Angie",
    party_size=4,
    reservation_date=date(2025, 12, 1),
    preferred_times=["19:00", "20:00"],
    auto_accept_any_time=True  # Accept any time if preferred times unavailable
)
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RESY_EMAIL` | Yes | Your Resy account email |
| `RESY_PASSWORD` | Yes | Your Resy account password |
| `RESY_PAYMENT_METHOD_ID` | No | Payment method ID (auto-detected if not provided) |
| `NOTIFICATION_EMAIL` | No | Email to receive booking notifications |
| `SMTP_SERVER` | No | SMTP server for email notifications |
| `SMTP_PORT` | No | SMTP port (default: 587) |
| `SMTP_USERNAME` | No | SMTP username |
| `SMTP_PASSWORD` | No | SMTP password |

### Reservation Configuration

```python
ReservationConfig(
    restaurant_name="Restaurant Name",  # Name to search for
    party_size=2,                       # Number of people (1-20)
    reservation_date=date(2025, 11, 15), # Target date
    preferred_times=["19:00", "19:30"],  # List of preferred times (24-hour)
    location="ny",                       # Location code (ny, la, sf, etc.)
    auto_accept_any_time=False          # Accept any time if preferred unavailable
)
```

### Location Codes

Common location codes:
- `ny` - New York
- `la` - Los Angeles
- `sf` - San Francisco
- `dc` - Washington DC
- `boston` - Boston
- `austin` - Austin

## How It Works

1. **Authentication**: Logs into Resy using your credentials
2. **Venue Search**: Finds the restaurant by name
3. **Availability Check**: Queries for available reservation slots
4. **Booking**: When a slot is found, immediately books it
5. **Payment**: Automatically uses your saved payment method for restaurants requiring cards
6. **Notification**: Sends confirmation via email (if configured)

## Tips for Success

### Timing is Everything

- **Know the release schedule**: Most restaurants release reservations at specific times:
  - Often at midnight (00:00) for bookings X days in advance
  - Some release at 9:00 AM or 10:00 AM
  - Check the restaurant's website or call to confirm

- **Start monitoring early**: Begin checking 1-2 minutes before the release time

- **Use scheduled monitoring**: For midnight releases, use `example_scheduled.py`

### Optimizing Your Chances

- **Multiple time slots**: Provide several preferred times to increase chances
- **Check interval**: Balance between responsiveness and server load:
  - High demand: 2-5 second intervals
  - Moderate demand: 10-30 second intervals
  - Cancellation hunting: 30-60 second intervals

- **Auto-accept**: For very hard-to-get reservations, consider `auto_accept_any_time=True`

### Popular Restaurants

For very popular restaurants (Carbone, Don Angie, 4 Charles Prime Rib, etc.):
- Use the scheduled approach starting exactly at release time
- Set check interval to 2-3 seconds
- Have backup time preferences ready
- Ensure payment method is already saved in your Resy account

## Logs

All activity is logged to:
- Console output (real-time)
- `logs/monitor.log` (when using monitoring scripts)
- `logs/reservation_history.log` (all booking attempts)

## Troubleshooting

### Authentication Failed
- Double-check credentials in `.env`
- Ensure your Resy account is active
- Try logging in manually on Resy.com to verify

### No Payment Method Found
- Log into Resy.com and add a payment method
- The bot will automatically detect it on next login

### Restaurant Not Found
- Try different search terms (e.g., "Carbone" vs "Carbone NYC")
- Check the location code matches the restaurant's city
- Use `example_search.py` to test searches

### Booking Failed
- Reservation window might not be open yet
- Someone else may have booked the slot first
- Restaurant might require special booking conditions

### Rate Limiting
- If you get rate limited, increase check intervals
- Reduce the number of simultaneous monitoring sessions
- Wait a few minutes before retrying

## Important Notes

### Terms of Service
- This bot is for **personal use only**
- Book reservations for yourself, not for resale
- Use reasonable check intervals to avoid overwhelming Resy's servers
- Respect Resy's terms of service

### Limitations
- Cannot bypass Resy's booking policies or restrictions
- Cannot guarantee booking success (depends on availability)
- Some restaurants may have special requirements
- Success rate depends on competition and timing

### Security
- Never share your `.env` file (contains credentials)
- `.env` is in `.gitignore` to prevent accidental commits
- Payment information is handled by Resy's API (not stored locally)

## Advanced Usage

### Custom Integration

You can import and use the bot in your own scripts:

```python
from bot import ResyBot
from config import load_settings, ReservationConfig
from datetime import date

settings = load_settings()
bot = ResyBot(settings)

if bot.authenticate():
    # Search for venues
    venues = bot.client.search_venue("Carbone", "ny")

    # Check availability
    slots = bot.client.find_availability(
        venue_id=12345,
        party_size=2,
        reservation_date=date(2025, 11, 15)
    )

    # Book reservation
    confirmation = bot.attempt_booking(reservation_config)
```

### Multiple Reservations

To monitor multiple reservations simultaneously, run multiple instances:

```bash
# Terminal 1
python example_monitor.py  # Configured for Restaurant A

# Terminal 2
python example_monitor.py  # Configured for Restaurant B
```

## Support

For issues or questions:
1. Check the logs in the `logs/` directory
2. Review the troubleshooting section above
3. Ensure all dependencies are installed correctly

## License

For personal use only. Please respect Resy's terms of service and use responsibly.

## Disclaimer

This bot automates the reservation booking process for personal convenience. Users are responsible for:
- Complying with Resy's terms of service
- Using the bot ethically and responsibly
- Honoring all reservations made
- Not using the bot for commercial purposes

The authors are not responsible for any account restrictions, booking failures, or other issues arising from use of this bot.
