"""
Table Hunter - Resy-Inspired Modern Design
"""
import streamlit as st
from datetime import date, datetime, timedelta
from bot import ResyBot
from config import ReservationConfig, load_settings
import json
import os
import time
import re
import dateparser
from google_places import GooglePlacesClient, get_restaurant_google_data, search_restaurant_place_id

# Configure page
st.set_page_config(
    page_title="Table Hunter",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Resy-Inspired Modern CSS
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap');

    /* Global styles */
    * {
        font-family: 'Montserrat', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Lora', serif;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Custom header */
    .custom-header {
        background: white;
        padding: 1.5rem 3rem;
        border-bottom: 1px solid #e5e5e5;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    .logo {
        font-family: 'Lora', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a1a;
        letter-spacing: -0.5px;
    }

    .search-container {
        flex: 1;
        max-width: 500px;
        margin: 0 2rem;
    }

    /* Restaurant cards - Resy style */
    .restaurant-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        overflow: hidden;
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 1.5rem;
    }

    .restaurant-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-4px);
    }

    .restaurant-header {
        padding: 1.5rem;
        border-bottom: 1px solid #f5f5f5;
    }

    .restaurant-name {
        font-family: 'Lora', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0 0 0.5rem 0;
    }

    .restaurant-meta {
        color: #767676;
        font-size: 0.9rem;
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    .badge {
        background: #1a1a1a;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-resy {
        background: #c8102e;
    }

    .badge-opentable {
        background: #da3743;
    }

    .rating {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        color: #1a1a1a;
        font-weight: 500;
    }

    /* Availability slots - Resy style */
    .slots-container {
        padding: 1.5rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
    }

    .time-slot {
        background: white;
        border: 1.5px solid #1a1a1a;
        color: #1a1a1a;
        padding: 12px 20px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
        min-width: 100px;
        text-align: center;
    }

    .time-slot:hover {
        background: #1a1a1a;
        color: white;
    }

    .time-slot-unavailable {
        background: #f5f5f5;
        border: 1.5px solid #e5e5e5;
        color: #bbb;
        cursor: not-allowed;
    }

    .time-slot-unavailable:hover {
        background: #f5f5f5;
        color: #bbb;
    }

    /* Booking section */
    .booking-section {
        padding: 1.5rem;
        background: #fafafa;
        border-top: 1px solid #e5e5e5;
    }

    /* Buttons */
    .stButton > button {
        background: #1a1a1a;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: #333;
        border: none;
    }

    /* Search bar */
    .stTextInput > div > div > input {
        border-radius: 24px;
        border: 1.5px solid #e5e5e5;
        padding: 12px 20px;
        font-size: 0.95rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #1a1a1a;
        box-shadow: none;
    }

    /* Date/Party size inputs */
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        border: 1.5px solid #e5e5e5;
        border-radius: 4px;
        padding: 10px 14px;
    }

    /* Filters */
    .filter-chip {
        display: inline-block;
        background: white;
        border: 1.5px solid #e5e5e5;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .filter-chip:hover {
        border-color: #1a1a1a;
        background: #fafafa;
    }

    .filter-chip-active {
        background: #1a1a1a;
        color: white;
        border-color: #1a1a1a;
    }

    /* Login modal */
    .login-modal {
        background: white;
        border-radius: 8px;
        padding: 2.5rem;
        max-width: 400px;
        margin: 3rem auto;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    }

    .login-title {
        font-family: 'Lora', serif;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: #1a1a1a;
    }

    /* No results */
    .no-results {
        text-align: center;
        padding: 4rem 2rem;
        color: #767676;
    }

    .no-results-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.3;
    }

    /* Restaurant detail view */
    .detail-hero {
        background: #fafafa;
        padding: 3rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
    }

    .detail-title {
        font-family: 'Lora', serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 1rem;
    }

    .detail-meta {
        display: flex;
        gap: 2rem;
        color: #767676;
        font-size: 1rem;
    }

    /* Review section */
    .review-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .review-author {
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .review-text {
        color: #555;
        line-height: 1.6;
    }

    /* Availability Calendar */
    .availability-calendar {
        background: #fafafa;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .calendar-header {
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1a1a1a;
    }

    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin-bottom: 1rem;
    }

    .calendar-day {
        text-align: center;
        padding: 0.75rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .calendar-day-header {
        font-weight: 700;
        color: #767676;
        font-size: 0.75rem;
        padding: 0.5rem;
    }

    .calendar-day-available {
        background: #e8f5e9;
        border: 1.5px solid #4caf50;
        color: #2e7d32;
        cursor: pointer;
    }

    .calendar-day-available:hover {
        background: #c8e6c9;
        transform: translateY(-2px);
    }

    .calendar-day-unavailable {
        background: #ffebee;
        border: 1.5px solid #f44336;
        color: #c62828;
    }

    .calendar-day-closed {
        background: #f5f5f5;
        border: 1.5px solid #e0e0e0;
        color: #9e9e9e;
        text-decoration: line-through;
    }

    .calendar-day-checking {
        background: white;
        border: 1.5px dashed #e5e5e5;
        color: #767676;
    }

    .calendar-legend {
        display: flex;
        gap: 1.5rem;
        justify-content: center;
        font-size: 0.85rem;
        margin-top: 1rem;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .legend-box {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        border: 1.5px solid;
    }

    /* Chatbot Assistant */
    .chatbot-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
        color: white;
    }

    .chatbot-message {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        line-height: 1.6;
    }

    .chatbot-input {
        background: white;
        border-radius: 8px;
        padding: 0.75rem;
    }

    /* Calendar improvements */
    .calendar-day-unreleased {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        border: 2px solid #f5af19;
        color: white;
        cursor: pointer;
        position: relative;
        font-weight: 700;
    }

    .calendar-day-unreleased:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(245, 175, 25, 0.4);
    }

    .calendar-day-unreleased::after {
        content: "⚡";
        position: absolute;
        top: 2px;
        right: 4px;
        font-size: 0.9rem;
    }

    .active-monitor-badge {
        background: #4caf50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.5rem 0;
    }

    .hunter-active-badge {
        background: #667eea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load restaurant database
@st.cache_data
def load_restaurants():
    """Load restaurant database from JSON file"""
    db_path = "restaurants_db.json"
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            return json.load(f)
    return {"san_francisco": []}

def save_restaurants(db):
    """Save restaurant database to JSON file"""
    with open("restaurants_db.json", 'w') as f:
        json.dump(db, f, indent=2)

# Initialize session state
if 'resy_authenticated' not in st.session_state:
    st.session_state.resy_authenticated = False
if 'opentable_authenticated' not in st.session_state:
    st.session_state.opentable_authenticated = False
if 'resy_bot' not in st.session_state:
    st.session_state.resy_bot = None
if 'opentable_bot' not in st.session_state:
    st.session_state.opentable_bot = None
if 'selected_restaurant' not in st.session_state:
    st.session_state.selected_restaurant = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'browse'  # 'browse' or 'detail'
if 'resy_email' not in st.session_state:
    st.session_state.resy_email = None
if 'opentable_email' not in st.session_state:
    st.session_state.opentable_email = None
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'login_platform' not in st.session_state:
    st.session_state.login_platform = None
if 'active_hunters' not in st.session_state:
    st.session_state.active_hunters = {}  # {hunt_id: {restaurant, date, times, party_size, ...}}
if 'active_snatchers' not in st.session_state:
    st.session_state.active_snatchers = {}  # {snatch_id: {restaurant, target_date, time, party_size, ...}}
if 'hunt_results' not in st.session_state:
    st.session_state.hunt_results = []  # List of successful hunts

def authenticate_resy(email, password):
    """Authenticate with Resy"""
    try:
        from config import Settings
        settings = Settings(resy_email=email, resy_password=password)
        bot = ResyBot(settings)
        if bot.authenticate():
            st.session_state.resy_bot = bot
            st.session_state.resy_authenticated = True
            st.session_state.resy_email = email
            return True, f"Connected to Resy"
        else:
            return False, "Authentication failed"
    except Exception as e:
        return False, f"Error: {str(e)}"

def authenticate_opentable(email, password):
    """Authenticate with OpenTable"""
    try:
        st.session_state.opentable_authenticated = True
        st.session_state.opentable_email = email
        return True, f"Connected to OpenTable"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_availability(venue_id, party_size, reservation_date, platform):
    """Check real-time availability"""
    if platform == "resy":
        if not st.session_state.resy_authenticated:
            return None, "Please login to Resy"

        try:
            client = st.session_state.resy_bot.client
            slots = client.find_availability(
                venue_id=int(venue_id),
                party_size=party_size,
                reservation_date=reservation_date
            )
            return slots, None
        except Exception as e:
            return None, f"Error: {str(e)}"

    elif platform == "opentable":
        if not st.session_state.opentable_authenticated:
            return None, "Please login to OpenTable"
        return [], None

    return None, "Unknown platform"

def get_cuisines():
    """Get list of unique cuisines"""
    db = load_restaurants()
    cuisines = set()
    for restaurant in db.get("san_francisco", []):
        cuisines.add(restaurant.get('cuisine', 'Unknown'))
    return sorted(list(cuisines))

def convert_to_12hour(time_24):
    """Convert 24-hour time to 12-hour format with AM/PM"""
    try:
        # Handle both "HH:MM" and datetime objects
        if isinstance(time_24, str):
            if ':' in time_24:
                hour, minute = time_24.split(':')[:2]
                hour = int(hour)
                minute = int(minute)
            else:
                return time_24  # Return as-is if not in expected format
        else:
            hour = time_24.hour
            minute = time_24.minute

        period = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        display_hour = 12 if display_hour == 0 else display_hour

        return f"{display_hour}:{minute:02d} {period}"
    except:
        return str(time_24)

def format_reservation_release_info(release_info):
    """Format reservation release information for display"""
    if not release_info:
        return "Contact restaurant for reservation policy"

    days = release_info.get('days_in_advance', 'N/A')
    time_24 = release_info.get('time', '')
    time_12 = convert_to_12hour(time_24)

    return f"Reservations released {days} days in advance at {time_12}"

def parse_reservation_request(text):
    """
    Parse natural language reservation request

    Returns: dict with 'dates', 'times', 'party_size'
    """
    result = {
        'dates': [],
        'times': [],
        'party_size': 2
    }

    text_lower = text.lower()

    # Extract party size
    party_patterns = [
        r'table\s+for\s+(\d+)',
        r'(\d+)\s+people',
        r'(\d+)\s+guests',
        r'party\s+of\s+(\d+)'
    ]
    for pattern in party_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result['party_size'] = int(match.group(1))
            break

    # Extract times
    time_patterns = [
        r'(\d{1,2}):?(\d{2})?\s*(am|pm)',
        r'(\d{1,2})\s*(am|pm)',
    ]
    times_found = []
    for pattern in time_patterns:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            period = match.group(3) if len(match.groups()) >= 3 else match.group(2)

            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0

            times_found.append(f"{hour:02d}:{minute:02d}")

    # If time range specified (e.g., "7pm - 8:30pm" or "between 7pm and 8:30pm")
    if ' - ' in text_lower or 'between' in text_lower:
        if len(times_found) >= 2:
            # Generate 30-minute intervals between times
            start_time = times_found[0]
            end_time = times_found[-1]
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))

            current = start_hour * 60 + start_min
            end = end_hour * 60 + end_min

            while current <= end:
                h = current // 60
                m = current % 60
                result['times'].append(f"{h:02d}:{m:02d}")
                current += 30
        else:
            result['times'] = times_found
    else:
        result['times'] = times_found

    # Extract dates using dateparser
    # Look for date-related phrases
    date_phrases = []

    # Check for day of week patterns
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for day in days_of_week:
        if day in text_lower:
            date_phrases.append(day)

    # Check for specific date patterns
    month_pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}'
    month_matches = re.findall(month_pattern, text_lower)
    date_phrases.extend(month_matches)

    # Check for "any Saturday in November" type patterns
    any_day_month_pattern = r'any\s+(\w+)\s+in\s+(\w+)'
    match = re.search(any_day_month_pattern, text_lower)
    if match:
        day_name = match.group(1)
        month_name = match.group(2)

        # Parse the month
        month_date = dateparser.parse(f"{month_name} 1, {datetime.now().year}")
        if month_date:
            # If month is in the past, use next year
            if month_date.month < datetime.now().month:
                month_date = month_date.replace(year=datetime.now().year + 1)

            # Find all occurrences of the day in that month
            current = month_date.replace(day=1)
            while current.month == month_date.month:
                if current.strftime('%A').lower() == day_name:
                    result['dates'].append(current.date())
                current += timedelta(days=1)
    else:
        # Parse other date phrases
        for phrase in date_phrases:
            parsed = dateparser.parse(phrase, settings={'PREFER_DATES_FROM': 'future'})
            if parsed:
                result['dates'].append(parsed.date())

    # If no specific dates found, try parsing the whole text
    if not result['dates']:
        parsed = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
        if parsed:
            result['dates'].append(parsed.date())

    # Default to 7:00 PM, 7:30 PM, 8:00 PM if no times specified
    if not result['times']:
        result['times'] = ['19:00', '19:30', '20:00']

    return result

def is_restaurant_open(restaurant, check_date):
    """Check if restaurant is open on a given date"""
    if not restaurant.get('hours'):
        return True  # Assume open if no hours specified

    day_name = check_date.strftime('%A').lower()
    day_hours = restaurant['hours'].get(day_name, {})

    return not day_hours.get('closed', False)

def run_active_hunters():
    """Check and execute active hunters"""
    if not st.session_state.active_hunters:
        return

    for hunt_id, hunt in list(st.session_state.active_hunters.items()):
        # Increment check counter
        hunt['checks'] = hunt.get('checks', 0) + 1

        # Check if authenticated for this platform
        platform = hunt['platform']
        is_auth = (
            (platform == "resy" and st.session_state.resy_authenticated) or
            (platform == "opentable" and st.session_state.opentable_authenticated)
        )

        if not is_auth:
            continue

        try:
            # Check availability
            slots, error = check_availability(
                hunt['restaurant']['venue_id'],
                hunt['party_size'],
                hunt['date'],
                platform
            )

            if slots:
                # Found availability! Check if any slots match preferred times
                for slot in slots:
                    slot_time = slot.get('time', slot.get('display_time', ''))
                    if any(pref_time in slot_time for pref_time in hunt['times']):
                        # Match found! Notify user
                        st.session_state.hunt_results.append({
                            'restaurant': hunt['restaurant']['name'],
                            'date': hunt['date'],
                            'time': slot_time,
                            'party_size': hunt['party_size'],
                            'found_at': datetime.now(),
                            'slot_data': slot
                        })

                        # Remove hunter after finding a slot
                        del st.session_state.active_hunters[hunt_id]
                        break

        except Exception as e:
            # Continue monitoring even if there's an error
            pass

def run_active_snatchers():
    """Check and execute active snatchers"""
    if not st.session_state.active_snatchers:
        return

    now = datetime.now()

    for snatch_id, snatch in list(st.session_state.active_snatchers.items()):
        release_date = snatch['release_date']
        release_time = snatch['release_time']

        # Parse release time
        release_hour, release_minute = map(int, release_time.split(':'))
        release_datetime = datetime.combine(release_date, datetime.min.time().replace(hour=release_hour, minute=release_minute))

        # Check if it's time to execute (within 1 minute window)
        time_diff = (release_datetime - now).total_seconds()

        if -60 < time_diff < 60:
            # It's time to snatch!
            platform = snatch['platform']
            is_auth = (
                (platform == "resy" and st.session_state.resy_authenticated) or
                (platform == "opentable" and st.session_state.opentable_authenticated)
            )

            if is_auth:
                try:
                    # Attempt to book
                    slots, error = check_availability(
                        snatch['restaurant']['venue_id'],
                        snatch['party_size'],
                        snatch['target_date'],
                        platform
                    )

                    if slots:
                        # Find matching time slot
                        target_time = snatch['time']
                        for slot in slots:
                            slot_time = slot.get('time', slot.get('display_time', ''))
                            if target_time in slot_time:
                                # Found the slot! Add to results
                                st.session_state.hunt_results.append({
                                    'restaurant': snatch['restaurant']['name'],
                                    'date': snatch['target_date'],
                                    'time': slot_time,
                                    'party_size': snatch['party_size'],
                                    'found_at': datetime.now(),
                                    'slot_data': slot,
                                    'type': 'snatcher'
                                })
                                break

                except Exception as e:
                    pass

            # Remove snatcher after execution attempt
            del st.session_state.active_snatchers[snatch_id]

def generate_availability_calendar(restaurant, party_size, platform, start_date=None, num_days=14):
    """
    Generate HTML for availability calendar with color coding including unreleased dates

    Args:
        restaurant: Restaurant data dict
        party_size: Number of people
        platform: 'resy' or 'opentable'
        start_date: Start date (defaults to today)
        num_days: Number of days to show

    Returns:
        Tuple of (html_string, availability_data, unreleased_dates)
    """
    if start_date is None:
        start_date = date.today()

    # Get reservation release policy
    release_info = restaurant.get('reservation_release', {})
    days_in_advance = release_info.get('days_in_advance', 30)

    # Calculate the latest date for which reservations are currently available
    latest_available_date = start_date + timedelta(days=days_in_advance)

    # Build calendar HTML
    html = '<div class="availability-calendar">'
    html += '<div class="calendar-header">Availability Calendar (Next 2 Weeks)</div>'
    html += '<div class="calendar-grid">'

    # Day headers
    day_headers = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for day_header in day_headers:
        html += f'<div class="calendar-day calendar-day-header">{day_header}</div>'

    # Find the first Monday to start the calendar
    days_to_subtract = start_date.weekday()  # 0 = Monday, 6 = Sunday
    calendar_start = start_date - timedelta(days=days_to_subtract)

    # Generate calendar days
    availability_data = {}
    unreleased_dates = []
    current_date = calendar_start

    # Show enough weeks to cover num_days
    total_days_to_show = ((num_days + days_to_subtract) // 7 + 1) * 7

    for i in range(total_days_to_show):
        current_date = calendar_start + timedelta(days=i)

        # Check if this date is in the future or today
        is_past = current_date < start_date
        is_open = is_restaurant_open(restaurant, current_date)
        is_unreleased = current_date > latest_available_date

        # Format date for display
        day_num = current_date.day
        month_str = current_date.strftime('%b') if current_date.day == 1 or i == 0 else ''
        display_text = f"{month_str} {day_num}" if month_str else str(day_num)

        if is_past:
            # Past dates - show as disabled
            html += f'<div class="calendar-day calendar-day-closed">{display_text}</div>'
        elif not is_open:
            # Restaurant closed
            html += f'<div class="calendar-day calendar-day-closed" title="Closed">{display_text}</div>'
            availability_data[current_date] = 'closed'
        elif is_unreleased:
            # Reservations not yet released - show with lightning bolt
            date_str = current_date.strftime('%Y-%m-%d')
            html += f'<div class="calendar-day calendar-day-unreleased" data-date="{date_str}" title="Reservations not yet released - click to set up Snatcher">{display_text}</div>'
            availability_data[current_date] = 'unreleased'
            unreleased_dates.append(current_date)
        else:
            # Will check availability (shows as "checking" initially)
            html += f'<div class="calendar-day calendar-day-checking" title="Click to check">{display_text}</div>'
            availability_data[current_date] = 'checking'

    html += '</div>'

    # Legend
    html += '''
    <div class="calendar-legend">
        <div class="legend-item">
            <div class="legend-box" style="background: #e8f5e9; border-color: #4caf50;"></div>
            <span>Available</span>
        </div>
        <div class="legend-item">
            <div class="legend-box" style="background: #ffebee; border-color: #f44336;"></div>
            <span>No Availability</span>
        </div>
        <div class="legend-item">
            <div class="legend-box" style="background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%); border-color: #f5af19;"></div>
            <span>⚡ Not Yet Released</span>
        </div>
        <div class="legend-item">
            <div class="legend-box" style="background: #f5f5f5; border-color: #e0e0e0;"></div>
            <span>Closed</span>
        </div>
    </div>
    '''

    html += '</div>'

    return html, availability_data, unreleased_dates

# Run background monitors
run_active_hunters()
run_active_snatchers()

# Auto-refresh if there are active monitors
if st.session_state.active_hunters or st.session_state.active_snatchers:
    # Refresh every 60 seconds when monitors are active
    st_autorefresh = st.empty()
    with st_autorefresh:
        time.sleep(0.1)  # Small delay to prevent too frequent refreshes

# Display hunt results/success notifications
if st.session_state.hunt_results:
    for result in st.session_state.hunt_results[-3:]:  # Show last 3 results
        result_type = result.get('type', 'hunter')
        icon = "⚡" if result_type == "snatcher" else "🎯"
        st.success(f"{icon} **Success!** Found reservation at **{result['restaurant']}** for **{result['party_size']}** on **{result['date'].strftime('%B %d')}** at **{result['time']}**")

# Custom Header
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.markdown('<div class="logo">Table Hunter</div>', unsafe_allow_html=True)

with col2:
    search_query = st.text_input(
        "Search",
        placeholder="Search restaurants, cuisines, neighborhoods...",
        label_visibility="collapsed"
    )

with col3:
    if st.session_state.resy_authenticated:
        st.success(f"🟢 Resy: {st.session_state.resy_email}")
    elif st.session_state.opentable_authenticated:
        st.success(f"🟢 OpenTable: {st.session_state.opentable_email}")
    else:
        st.info("Not logged in")

st.markdown("---")

# Main content
if st.session_state.view_mode == 'detail' and st.session_state.selected_restaurant:
    # Restaurant Detail View
    restaurant = st.session_state.selected_restaurant
    platform = restaurant.get('platform', 'resy')

    # Back button
    if st.button("← Back to all restaurants"):
        st.session_state.view_mode = 'browse'
        st.session_state.selected_restaurant = None
        st.rerun()

    # Restaurant hero section with Google data
    google_place_id = restaurant.get('google_place_id')
    google_data = None

    # Get API key from Streamlit secrets or environment variable
    api_key = None
    try:
        # Try Streamlit secrets first
        if "GOOGLE_PLACES_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_PLACES_API_KEY"]
    except Exception as e:
        pass

    # Fall back to environment variable
    if not api_key:
        api_key = os.getenv('GOOGLE_PLACES_API_KEY')

    # Try to get Google data
    if api_key:
        if google_place_id:
            google_data = get_restaurant_google_data(google_place_id, api_key)
        else:
            # Try to search for the place
            google_place_id = search_restaurant_place_id(restaurant['name'], "San Francisco, CA", api_key)
            if google_place_id:
                google_data = get_restaurant_google_data(google_place_id, api_key)
                # Save the place_id for future use
                restaurant['google_place_id'] = google_place_id
    else:
        google_data = None

    # Display hero with Google rating if available
    google_rating = google_data.get('rating') if google_data else None
    google_reviews_count = google_data.get('user_ratings_total') if google_data else None

    st.markdown(f"""
    <div class="detail-hero">
        <div class="detail-title">{restaurant['name']}</div>
        <div class="detail-meta">
            <span>📍 {restaurant['neighborhood']}</span>
            <span>•</span>
            <span>🍽️ {restaurant['cuisine']}</span>
            <span>•</span>
            <span class="badge badge-{platform}">{platform.upper()}</span>
            {f'<span>•</span><span>⭐ {google_rating} ({google_reviews_count} reviews)</span>' if google_rating else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Google Photos Section
    if google_data and google_data.get('photos'):
        st.markdown("### Photos")
        photos = google_data['photos'][:6]  # Show up to 6 photos
        cols = st.columns(3)

        client = GooglePlacesClient(api_key)
        for idx, photo in enumerate(photos):
            col_idx = idx % 3
            with cols[col_idx]:
                photo_ref = photo.get('photo_reference')
                if photo_ref:
                    photo_url = client.get_photo_url(photo_ref, max_width=400)
                    if photo_url:
                        st.image(photo_url, use_column_width=True)

    # Restaurant Information Section
    st.markdown("### Restaurant Information")

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        # Reservation release information
        release_info = restaurant.get('reservation_release')
        release_text = format_reservation_release_info(release_info)
        st.info(f"📅 **Reservation Policy**\n\n{release_text}")

    with info_col2:
        # Restaurant hours
        hours = restaurant.get('hours', {})
        if hours:
            st.info("🕒 **Hours**")
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                day_hours = hours.get(day, {})
                day_display = day.capitalize()[:3]
                if day_hours.get('closed'):
                    st.caption(f"**{day_display}**: Closed")
                else:
                    open_time = convert_to_12hour(day_hours.get('open', ''))
                    close_time = convert_to_12hour(day_hours.get('close', ''))
                    st.caption(f"**{day_display}**: {open_time} - {close_time}")

    # Booking interface
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        party_size = st.number_input("Party Size", min_value=1, max_value=20, value=2)

    with col2:
        reservation_date = st.date_input(
            "Date",
            min_value=date.today(),
            value=date.today() + timedelta(days=7)
        )

    # Display availability calendar
    calendar_html, availability_data, unreleased_dates = generate_availability_calendar(
        restaurant, party_size, platform
    )
    st.markdown(calendar_html, unsafe_allow_html=True)

    # Show unreleased dates clickable section
    if unreleased_dates:
        st.markdown("### ⚡ Set up Reservation Snatcher")
        st.info(f"💡 Click on dates with ⚡ to automatically book when reservations are released")

        selected_unreleased_date = st.selectbox(
            "Select a date to set up Snatcher",
            options=[None] + unreleased_dates,
            format_func=lambda x: "Choose a date..." if x is None else x.strftime('%B %d, %Y'),
            key="unreleased_date_select"
        )

        if selected_unreleased_date:
            release_info = restaurant.get('reservation_release', {})
            days_in_advance = release_info.get('days_in_advance', 30)
            release_time = release_info.get('time', '00:00')
            release_date = selected_unreleased_date - timedelta(days=days_in_advance)

            col1, col2 = st.columns(2)
            with col1:
                snatch_time = st.selectbox(
                    "Preferred Time",
                    ["17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30"],
                    format_func=convert_to_12hour,
                    key="snatch_time_quick"
                )
            with col2:
                snatch_party = st.number_input("Party Size", min_value=1, max_value=20, value=party_size, key="snatch_party_quick")

            st.success(f"✅ Reservations for {selected_unreleased_date.strftime('%B %d')} will be released on **{release_date.strftime('%B %d, %Y')}** at **{convert_to_12hour(release_time)}**")

            if st.button("⚡ Activate Snatcher", type="primary", use_container_width=True, key="activate_snatcher_quick"):
                snatch_id = f"{restaurant['venue_id']}_{selected_unreleased_date}_{int(time.time())}"
                st.session_state.active_snatchers[snatch_id] = {
                    'restaurant': restaurant,
                    'target_date': selected_unreleased_date,
                    'release_date': release_date,
                    'release_time': release_time,
                    'time': snatch_time,
                    'party_size': snatch_party,
                    'platform': platform,
                    'created': datetime.now()
                }
                st.success(f"⚡ Snatcher activated! Will attempt to book on {release_date.strftime('%B %d')} at {convert_to_12hour(release_time)}")
                st.rerun()

    # Check if authenticated for this platform
    is_authenticated = (
        (platform == "resy" and st.session_state.resy_authenticated) or
        (platform == "opentable" and st.session_state.opentable_authenticated)
    )

    if not is_authenticated:
        st.warning(f"Please login to {platform.title()} to see available times")

        with st.expander("🔐 Login", expanded=True):
            with st.form(f"login_{platform}"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")

                if st.form_submit_button("Login", use_container_width=True):
                    if email and password:
                        if platform == "resy":
                            success, msg = authenticate_resy(email, password)
                        else:
                            success, msg = authenticate_opentable(email, password)

                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    else:
        # Check availability
        with st.spinner("Checking availability..."):
            slots, error = check_availability(
                restaurant['venue_id'],
                party_size,
                reservation_date,
                platform
            )

        if error:
            st.error(error)
        elif slots:
            st.markdown("### Available Times")
            st.markdown('<div class="slots-container">', unsafe_allow_html=True)

            # Display time slots
            cols = st.columns(6)
            for idx, slot in enumerate(slots):
                col_idx = idx % 6
                with cols[col_idx]:
                    time_str = slot.get('display_time', slot.get('time', 'Unknown'))
                    # Convert to 12-hour format
                    time_12hr = convert_to_12hour(time_str)
                    if st.button(time_12hr, key=f"slot_{idx}", use_container_width=True):
                        st.success(f"Selected {time_12hr}")
                        st.info("Booking functionality coming soon!")

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # No availability - show chatbot assistant
            st.markdown("""
            <div class="chatbot-container">
                <div class="chatbot-message">
                    <strong>🎯 Table Hunter Assistant</strong><br><br>
                    Don't see a reservation for the date or time you're looking for? I can help!<br><br>
                    Use my <strong>Table Hunter</strong> feature to automatically snag reservations when they become available from cancellations.
                    Just tell me what date, time, and number of guests you're looking for, and I'll do the rest of the work and let you know when I find something!
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Chatbot-style input
            hunter_request = st.text_area(
                "Tell me what you're looking for...",
                placeholder=f"Example: I'm looking for a table for 2 on {(reservation_date + timedelta(days=1)).strftime('%A, %B %d')} around 7:30 PM",
                key="hunter_request_text",
                height=100
            )

            if st.button("🚀 Activate Table Hunter", type="primary", use_container_width=True, key="start_hunter_chatbot"):
                if hunter_request:
                    # Parse the natural language request
                    parsed = parse_reservation_request(hunter_request)

                    # Create hunters for each date found
                    hunters_created = 0
                    dates_to_hunt = parsed['dates'] if parsed['dates'] else [reservation_date]

                    for hunt_date in dates_to_hunt[:5]:  # Limit to 5 dates to avoid too many hunters
                        hunt_id = f"{restaurant['venue_id']}_{hunt_date}_{int(time.time())}_{hunters_created}"
                        st.session_state.active_hunters[hunt_id] = {
                            'restaurant': restaurant,
                            'date': hunt_date,
                            'times': parsed['times'],
                            'party_size': parsed['party_size'],
                            'platform': platform,
                            'started': datetime.now(),
                            'checks': 0,
                            'interval': "Every 1 minute",
                            'user_request': hunter_request
                        }
                        hunters_created += 1

                    # Show what was parsed
                    dates_str = ", ".join([d.strftime('%b %d') for d in dates_to_hunt[:5]])
                    times_str = ", ".join([convert_to_12hour(t) for t in parsed['times'][:3]])
                    if len(parsed['times']) > 3:
                        times_str += f" +{len(parsed['times'])-3} more"

                    st.success(f"🎯 Table Hunter activated for {parsed['party_size']} guests!")
                    st.info(f"**Hunting on:** {dates_str}\n\n**Times:** {times_str}")
                    st.info("💡 Tip: Keep this page open or check back periodically for updates.")
                    st.rerun()
                else:
                    st.warning("Please tell me what you're looking for!")

    # Display active monitors
    if is_authenticated and (st.session_state.active_hunters or st.session_state.active_snatchers):
        st.markdown("---")
        st.markdown("### 🔔 Active Monitors")

        # Show active hunters
        for hunt_id, hunt in list(st.session_state.active_hunters.items()):
            if hunt['restaurant']['venue_id'] == restaurant['venue_id']:
                time_str = ", ".join([convert_to_12hour(t) for t in hunt['times'][:3]])
                if len(hunt['times']) > 3:
                    time_str += f" +{len(hunt['times'])-3} more"

                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f'<span class="hunter-active-badge">🎯 Table Hunter</span>', unsafe_allow_html=True)
                    st.caption(f"Hunting for {hunt['party_size']} on {hunt['date'].strftime('%b %d')} at {time_str} • {hunt['checks']} checks")
                with col2:
                    if st.button("⏹️ Stop", key=f"stop_hunt_{hunt_id}"):
                        del st.session_state.active_hunters[hunt_id]
                        st.rerun()

        # Show active snatchers
        for snatch_id, snatch in list(st.session_state.active_snatchers.items()):
            if snatch['restaurant']['venue_id'] == restaurant['venue_id']:
                days_until = (snatch['release_date'] - date.today()).days

                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f'<span class="active-monitor-badge">⚡ Reservation Snatcher</span>', unsafe_allow_html=True)
                    st.caption(f"Set for {snatch['party_size']} on {snatch['target_date'].strftime('%b %d')} at {convert_to_12hour(snatch['time'])} • Releases in {days_until} days")
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_snatch_{snatch_id}"):
                        del st.session_state.active_snatchers[snatch_id]
                        st.rerun()

    # Google Reviews Section
    if google_data and google_data.get('reviews'):
        st.markdown("---")
        st.markdown("### Reviews from Google")

        reviews = google_data['reviews'][:5]  # Top 5 reviews
        for review in reviews:
            author = review.get('author_name', 'Anonymous')
            rating = review.get('rating', 0)
            text = review.get('text', '')
            time_desc = review.get('relative_time_description', '')

            # Star rating display
            stars = "⭐" * int(rating) + "☆" * (5 - int(rating))

            st.markdown(f"""
            <div class="review-card">
                <div class="review-author">
                    <strong>{author}</strong> • {stars} • {time_desc}
                </div>
                <div class="review-text">
                    {text}
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    # Browse View
    db = load_restaurants()
    restaurants = db.get("san_francisco", [])

    # Filters
    st.markdown("### Explore Restaurants")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        cuisines = get_cuisines()
        cuisine_filter = st.selectbox("Cuisine", ["All Cuisines"] + cuisines)

    with col2:
        platform_filter = st.selectbox("Platform", ["All", "Resy", "OpenTable"])

    with col3:
        sort_by = st.selectbox("Sort by", ["Name (A-Z)", "Neighborhood", "Cuisine"])

    # Filter restaurants
    filtered = restaurants

    if search_query:
        filtered = [r for r in filtered if
                   search_query.lower() in r['name'].lower() or
                   search_query.lower() in r.get('cuisine', '').lower() or
                   search_query.lower() in r.get('neighborhood', '').lower()]

    if cuisine_filter != "All Cuisines":
        filtered = [r for r in filtered if r.get('cuisine') == cuisine_filter]

    if platform_filter != "All":
        filtered = [r for r in filtered if r.get('platform', 'resy').lower() == platform_filter.lower()]

    # Sort
    if sort_by == "Name (A-Z)":
        filtered = sorted(filtered, key=lambda x: x['name'])
    elif sort_by == "Neighborhood":
        filtered = sorted(filtered, key=lambda x: x.get('neighborhood', ''))
    elif sort_by == "Cuisine":
        filtered = sorted(filtered, key=lambda x: x.get('cuisine', ''))

    st.markdown(f"**{len(filtered)} restaurants**")
    st.markdown("---")

    # Display restaurants
    if filtered:
        for idx, restaurant in enumerate(filtered):
            platform = restaurant.get('platform', 'resy')

            # Restaurant card
            with st.container():
                st.markdown(f"""
                <div class="restaurant-card">
                    <div class="restaurant-header">
                        <h3 class="restaurant-name">{restaurant['name']}</h3>
                        <div class="restaurant-meta">
                            <span>📍 {restaurant['neighborhood']}</span>
                            <span>•</span>
                            <span>🍽️ {restaurant['cuisine']}</span>
                            <span>•</span>
                            <span class="badge badge-{platform}">{platform.upper()}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"View availability →", key=f"browse_view_{idx}_{restaurant['venue_id']}", use_container_width=True):
                    st.session_state.selected_restaurant = restaurant
                    st.session_state.view_mode = 'detail'
                    st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="no-results">
            <div class="no-results-icon">🔍</div>
            <h3>No restaurants found</h3>
            <p>Try adjusting your search or filters</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #999; font-size: 0.9rem; padding: 2rem 0;'>Table Hunter • San Francisco</div>",
    unsafe_allow_html=True
)
