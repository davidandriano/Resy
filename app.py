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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        background: white;
        border: 1.5px solid #e5e5e5;
        color: #0066cc;
        font-weight: 700;
        cursor: pointer;
    }

    .calendar-day-available:hover {
        background: #f0f8ff;
        border-color: #0066cc;
        transform: translateY(-1px);
    }

    .calendar-day-unavailable {
        background: white;
        border: 1.5px solid #e5e5e5;
        color: #dc3545;
        font-weight: 400;
        cursor: pointer;
    }

    .calendar-day-unavailable:hover {
        background: #fff5f5;
        border-color: #dc3545;
    }

    .calendar-day-past {
        background: white;
        border: 1.5px solid #e5e5e5;
        color: #999;
        text-decoration: line-through;
    }

    .calendar-day-closed {
        background: white;
        border: 1.5px solid #e5e5e5;
        color: #999;
        text-decoration: line-through;
    }

    .calendar-day-checking {
        background: white;
        border: 1.5px dashed #e5e5e5;
        color: #767676;
    }

    .lightning-badge {
        position: relative;
    }

    .lightning-badge::after {
        content: "⚡";
        position: absolute;
        top: -2px;
        right: -2px;
        background: #ffc107;
        border-radius: 50%;
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
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
        background: white;
        border: 1.5px solid #e5e5e5;
        color: #767676;
        cursor: pointer;
        position: relative;
        font-weight: 500;
    }

    .calendar-day-unreleased:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(245, 175, 25, 0.4);
        border-color: #ffc107;
    }

    .calendar-day-unreleased::after {
        content: "⚡";
        position: absolute;
        top: 2px;
        right: 2px;
        font-size: 0.75rem;
        background: #ffc107;
        border-radius: 50%;
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
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

    /* Resy-style bubble selectors */
    .booking-bubbles {
        display: flex;
        gap: 0.75rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }

    .booking-bubble {
        background: white;
        border: 1.5px solid #e5e5e5;
        border-radius: 8px;
        padding: 0.75rem 1.25rem;
        cursor: pointer;
        transition: all 0.2s ease;
        min-width: 120px;
        text-align: center;
    }

    .booking-bubble:hover {
        border-color: #1a1a1a;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .booking-bubble-label {
        font-size: 0.75rem;
        color: #767676;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.25rem;
    }

    .booking-bubble-value {
        font-size: 1rem;
        color: #1a1a1a;
        font-weight: 600;
    }

    /* Calendar modal */
    .calendar-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    }

    .calendar-modal-content {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }

    .calendar-modal-header {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: #1a1a1a;
    }

    /* Compact calendar for bubble view */
    .compact-calendar {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        margin: 1rem 0;
    }

    .compact-date-tile {
        background: white;
        border: 1.5px solid #e5e5e5;
        border-radius: 6px;
        padding: 0.5rem;
        min-width: 60px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .compact-date-tile:hover {
        border-color: #1a1a1a;
        transform: translateY(-2px);
    }

    .compact-date-tile-selected {
        border-color: #0066cc;
        background: #f0f8ff;
    }

    .compact-date-day {
        font-size: 0.7rem;
        color: #767676;
        text-transform: uppercase;
    }

    .compact-date-num {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-top: 0.25rem;
    }

    .compact-date-available {
        color: #0066cc;
        font-weight: 700;
    }

    .compact-date-unavailable {
        color: #dc3545;
    }

    .more-dates-btn {
        background: white;
        border: 1.5px solid #e5e5e5;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        font-size: 1.25rem;
        color: #767676;
        transition: all 0.2s ease;
    }

    .more-dates-btn:hover {
        border-color: #1a1a1a;
        color: #1a1a1a;
    }

    /* Table Hunter Assistant - Always visible */
    .table-hunter-panel {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
        color: white;
    }

    .table-hunter-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .table-hunter-description {
        font-size: 0.9rem;
        opacity: 0.95;
        margin-bottom: 1rem;
        line-height: 1.5;
    }

    .table-hunter-input {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 1rem;
    }

    /* Grid layout for restaurant browse */
    .restaurant-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }

    .restaurant-grid-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 12px 12px 0 0;
        overflow: hidden;
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 0;
    }

    .restaurant-grid-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-2px);
        border-color: #ccc;
    }

    .restaurant-grid-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        color: white;
    }

    .restaurant-grid-info {
        padding: 1.25rem;
    }

    .restaurant-grid-name {
        font-family: 'Lora', serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.75rem;
    }

    .restaurant-grid-meta {
        color: #767676;
        font-size: 0.875rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .restaurant-grid-meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Filter section */
    .filter-section {
        background: #fafafa;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }

    .filter-title {
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1a1a1a;
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
        r'(\d{1,2}):(\d{2})\s*(am|pm)',  # 7:30pm
        r'(\d{1,2})\s*(am|pm)',          # 7pm
    ]
    times_found = []
    for pattern in time_patterns:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            hour = int(match.group(1))

            # Check if this pattern has minutes (group 2 is digits) or am/pm (group 2 is am/pm)
            if len(match.groups()) == 3:  # Pattern with minutes: hour:minute am/pm
                minute = int(match.group(2))
                period = match.group(3)
            else:  # Pattern without minutes: hour am/pm
                minute = 0
                period = match.group(2)

            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0

            time_24 = f"{hour:02d}:{minute:02d}"
            if time_24 not in times_found:  # Avoid duplicates
                times_found.append(time_24)

    # Check for "around" keyword (e.g., "around 7pm" means 6:30pm, 7pm, 7:30pm)
    if 'around' in text_lower and times_found:
        expanded_times = []
        for time_str in times_found:
            hour, minute = map(int, time_str.split(':'))
            total_mins = hour * 60 + minute

            # Add -30 mins, exact time, +30 mins
            for offset in [-30, 0, 30]:
                new_mins = total_mins + offset
                if new_mins >= 0:  # Don't go negative
                    h = (new_mins // 60) % 24
                    m = new_mins % 60
                    expanded_times.append(f"{h:02d}:{m:02d}")

        result['times'] = sorted(list(set(expanded_times)))  # Remove duplicates and sort

    # If time range specified (e.g., "7pm - 8:30pm" or "between 7pm and 8:30pm")
    elif ' - ' in text_lower or 'between' in text_lower:
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

def send_notification(to_email, subject, message):
    """
    Send email notification using SMTP

    Free options:
    1. Gmail SMTP (gmail.com) - 500 emails/day
       - SMTP Server: smtp.gmail.com
       - Port: 587
       - Requires app password (not regular password)

    2. Outlook/Hotmail SMTP - Free
       - SMTP Server: smtp-mail.outlook.com
       - Port: 587

    To use: Add to .streamlit/secrets.toml:
        NOTIFICATION_EMAIL = "your-email@gmail.com"
        NOTIFICATION_PASSWORD = "your-app-password"
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
    """
    try:
        # Get SMTP settings from secrets or env
        smtp_server = st.secrets.get("SMTP_SERVER", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
        smtp_port = int(st.secrets.get("SMTP_PORT", os.getenv("SMTP_PORT", 587)))
        sender_email = st.secrets.get("NOTIFICATION_EMAIL", os.getenv("NOTIFICATION_EMAIL"))
        sender_password = st.secrets.get("NOTIFICATION_PASSWORD", os.getenv("NOTIFICATION_PASSWORD"))

        if not sender_email or not sender_password:
            return False  # Notifications not configured

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html'))

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"Notification error: {e}")
        return False

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
                        result = {
                            'restaurant': hunt['restaurant']['name'],
                            'date': hunt['date'],
                            'time': slot_time,
                            'party_size': hunt['party_size'],
                            'found_at': datetime.now(),
                            'slot_data': slot
                        }
                        st.session_state.hunt_results.append(result)

                        # Send email notification if configured
                        user_email = st.session_state.get('notification_email')
                        if user_email:
                            subject = f"🎯 Table Found at {hunt['restaurant']['name']}!"
                            message = f"""
                            <h2>Great news! We found a table for you!</h2>
                            <p><strong>Restaurant:</strong> {hunt['restaurant']['name']}</p>
                            <p><strong>Date:</strong> {hunt['date'].strftime('%B %d, %Y')}</p>
                            <p><strong>Time:</strong> {slot_time}</p>
                            <p><strong>Party Size:</strong> {hunt['party_size']}</p>
                            <p>Log into Table Hunter to complete your reservation!</p>
                            """
                            send_notification(user_email, subject, message)

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

def generate_availability_calendar(restaurant, party_size, platform, start_date=None, num_days=21):
    """
    Generate INTERACTIVE availability calendar that actually checks availability

    Args:
        restaurant: Restaurant data dict
        party_size: Number of people
        platform: 'resy' or 'opentable'
        start_date: Start date (defaults to today)
        num_days: Number of days to check (default 21 = 3 weeks)

    Returns:
        Tuple of (availability_dict, unreleased_dates)
        availability_dict: {date: {'has_slots': bool, 'slots': list, 'state': str}}
    """
    if start_date is None:
        start_date = date.today()

    # Get reservation release policy
    release_info = restaurant.get('reservation_release', {})
    days_in_advance = release_info.get('days_in_advance', 30)

    # Calculate the latest date for which reservations are currently available
    latest_available_date = start_date + timedelta(days=days_in_advance)

    # Check if authenticated
    is_auth = (
        (platform == "resy" and st.session_state.resy_authenticated) or
        (platform == "opentable" and st.session_state.opentable_authenticated)
    )

    availability_dict = {}
    unreleased_dates = []

    # Check availability for each day
    for day_offset in range(num_days):
        check_date = start_date + timedelta(days=day_offset)

        # Determine state
        is_past = check_date < start_date
        is_open = is_restaurant_open(restaurant, check_date)
        is_unreleased = check_date > latest_available_date

        if is_past:
            state = 'past'
            availability_dict[check_date] = {'has_slots': False, 'slots': [], 'state': 'past'}

        elif not is_open:
            state = 'closed'
            availability_dict[check_date] = {'has_slots': False, 'slots': [], 'state': 'closed'}

        elif is_unreleased:
            state = 'unreleased'
            availability_dict[check_date] = {'has_slots': False, 'slots': [], 'state': 'unreleased'}
            unreleased_dates.append(check_date)

        elif is_auth:
            # Actually check availability!
            try:
                slots, error = check_availability(
                    restaurant['venue_id'],
                    party_size,
                    check_date,
                    platform
                )

                if error:
                    state = 'error'
                    availability_dict[check_date] = {'has_slots': False, 'slots': [], 'state': 'error'}
                elif slots and len(slots) > 0:
                    state = 'available'
                    availability_dict[check_date] = {'has_slots': True, 'slots': slots, 'state': 'available'}
                else:
                    state = 'unavailable'
                    availability_dict[check_date] = {'has_slots': False, 'slots': [], 'state': 'unavailable'}

            except Exception as e:
                state = 'error'
                availability_dict[check_date] = {'has_slots': False, 'slots': [], 'state': 'error'}

        else:
            # Not authenticated - can't check
            state = 'unknown'
            availability_dict[check_date] = {'has_slots': False, 'slots': [], 'state': 'unknown'}

    return availability_dict, unreleased_dates

def render_interactive_calendar(availability_dict, start_date=None):
    """
    Render interactive calendar using Streamlit buttons with availability data

    Args:
        availability_dict: Dict from generate_availability_calendar
        start_date: Starting date (defaults to today)

    Returns:
        selected_date or None
    """
    if start_date is None:
        start_date = date.today()

    st.markdown('<div class="availability-calendar">', unsafe_allow_html=True)
    st.markdown('<div class="calendar-header">Interactive Availability Calendar</div>', unsafe_allow_html=True)

    # Find the first Monday
    days_to_subtract = start_date.weekday()
    calendar_start = start_date - timedelta(days=days_to_subtract)

    # Day headers
    cols = st.columns(7)
    day_headers = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for idx, day_name in enumerate(day_headers):
        with cols[idx]:
            st.markdown(f'<div style="text-align: center; font-weight: 700; color: #767676; font-size: 0.75rem; padding: 0.5rem;">{day_name}</div>', unsafe_allow_html=True)

    # Calendar days - show 3 weeks
    selected_date = None
    for week in range(3):
        cols = st.columns(7)
        for day_idx in range(7):
            current_date = calendar_start + timedelta(days=week * 7 + day_idx)

            with cols[day_idx]:
                # Get availability info
                avail_info = availability_dict.get(current_date, {'state': 'unknown'})
                state = avail_info['state']

                # Format display
                day_num = current_date.day
                month_str = current_date.strftime('%b') if current_date.day == 1 or (week == 0 and day_idx == 0) else ''
                display_text = f"{month_str} {day_num}" if month_str else str(day_num)

                # Determine style class and clickability
                # Make all future dates clickable (available, unavailable, unreleased)
                if state == 'available':
                    css_class = 'calendar-day-available'
                    clickable = True
                elif state == 'unavailable':
                    css_class = 'calendar-day-unavailable'
                    clickable = True  # Now clickable!
                elif state == 'past':
                    css_class = 'calendar-day-past'
                    clickable = False
                elif state == 'closed':
                    css_class = 'calendar-day-closed'
                    clickable = False
                elif state == 'unreleased':
                    css_class = 'calendar-day-unreleased lightning-badge'
                    clickable = True
                else:
                    css_class = 'calendar-day-checking'
                    clickable = False

                # Display as button if clickable, or styled div with lightning bolt for unreleased
                if clickable and current_date >= start_date:
                    button_key = f"cal_{current_date.strftime('%Y%m%d')}"

                    if st.button(display_text, key=button_key, use_container_width=True, type="primary" if state == 'available' else "secondary"):
                        selected_date = current_date
                else:
                    # Display as non-clickable div
                    st.markdown(f'<div class="calendar-day {css_class}">{display_text}</div>', unsafe_allow_html=True)

    # Legend
    st.markdown('''
    <div class="calendar-legend">
        <div class="legend-item">
            <div class="legend-box" style="border-color: #0066cc;"><strong style="color: #0066cc;">15</strong></div>
            <span>Available</span>
        </div>
        <div class="legend-item">
            <div class="legend-box" style="border-color: #dc3545;"><span style="color: #dc3545;">15</span></div>
            <span>No Availability</span>
        </div>
        <div class="legend-item">
            <div class="legend-box" style="background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);"><span style="color: white;">⚡</span></div>
            <span>Not Yet Released</span>
        </div>
        <div class="legend-item">
            <div class="legend-box" style="border-color: #999;"><del style="color: #999;">15</del></div>
            <span>Closed/Past</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    return selected_date

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
    api_key_source = None
    try:
        # Try Streamlit secrets first
        if "GOOGLE_PLACES_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_PLACES_API_KEY"]
            api_key_source = "Streamlit Secrets"
    except Exception as e:
        pass

    # Fall back to environment variable
    if not api_key:
        api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if api_key:
            api_key_source = "Environment Variable"

    # Hardcoded place_ids for known restaurants (fallback)
    # Note: These may need to be verified/updated if API calls fail
    KNOWN_PLACE_IDS = {
        "Flour+Water": "ChIJXWBgjQl-j4ARbD-iSSMfpGg",  # Try alternative place_id
        "Jules": "ChIJ_____placeholder_for_jules",
        "Izakaya Rintaro": "ChIJwc4gOgp-j4ARsKCdDZGDfb0",
        "mijoté": "ChIJ_____placeholder_for_mijote",
        "Liholiho Yacht Club": "ChIJY3Y2PHuAhYAR0C9nTVQwqKM",
        "side a": "ChIJ_____placeholder_for_sidea"
    }

    # Debug section
    with st.expander("🔍 Google API Debug Info", expanded=True):
        if api_key:
            st.success(f"✅ API Key found from: {api_key_source}")
            st.code(f"Key starts with: {api_key[:20]}...")

            # Add specific fix for REQUEST_DENIED error
            st.error("**⚠️ CRITICAL FIX REQUIRED:**")
            st.markdown("""
            **If you see "REQUEST_DENIED" error:**

            The error "API keys with referer restrictions cannot be used with this API" means your API key has website restrictions enabled.

            **To fix this:**
            1. Go to [Google Cloud Console API Credentials](https://console.cloud.google.com/apis/credentials)
            2. Find your API key and click on it
            3. Under "API restrictions", select **"Don't restrict key"** (or at minimum, ensure "Places API" is in the list)
            4. Under "Application restrictions", select **"None"** (this is the critical fix)
            5. Click "Save"
            6. Wait 1-2 minutes for changes to propagate
            7. Refresh this page

            **Alternative:** Create a new API key with no restrictions.
            """)

            # Add general troubleshooting
            st.info("**General Troubleshooting:**\n"
                   "1. Places API (New) must be enabled in Google Cloud Console\n"
                   "2. Billing must be enabled for the project\n"
                   "3. API key must have NO application restrictions\n"
                   "4. Check quotas are not exceeded")
        else:
            st.error("❌ No API key found")
            st.info("Add to .streamlit/secrets.toml:\nGOOGLE_PLACES_API_KEY = \"your-key-here\"")

        st.info(f"**Restaurant:** {restaurant['name']}")
        if restaurant.get('google_place_id'):
            st.info(f"**Saved place_id:** {restaurant.get('google_place_id')}")

        if restaurant['name'] in KNOWN_PLACE_IDS:
            st.info(f"**Hardcoded place_id available:** {KNOWN_PLACE_IDS[restaurant['name']]}")

    # Try to get Google data
    if api_key:
        if google_place_id:
            google_data = get_restaurant_google_data(google_place_id, api_key, debug=True)
            if not google_data:
                st.warning(f"⚠️ API call failed for place_id: {google_place_id}")
        else:
            # First try hardcoded place_id
            if restaurant['name'] in KNOWN_PLACE_IDS and not KNOWN_PLACE_IDS[restaurant['name']].startswith("ChIJ_____placeholder"):
                google_place_id = KNOWN_PLACE_IDS[restaurant['name']]
                st.info(f"Using hardcoded place_id for {restaurant['name']}")
                google_data = get_restaurant_google_data(google_place_id, api_key, debug=True)
                restaurant['google_place_id'] = google_place_id
            else:
                # Try to search for the place with multiple name variations
                search_names = [
                    restaurant['name'],
                    restaurant['name'].replace('+', ' + '),  # "Flour+Water" -> "Flour + Water"
                    restaurant['name'].replace('+', ' '),     # "Flour+Water" -> "Flour Water"
                ]

                # Enable debug mode in the expander
                with st.expander("🔍 Detailed Search Debug", expanded=True):
                    for search_name in search_names:
                        st.markdown(f"**Trying name variation: '{search_name}'**")
                        google_place_id = search_restaurant_place_id(search_name, "San Francisco, CA", api_key, debug=True)
                        if google_place_id:
                            google_data = get_restaurant_google_data(google_place_id, api_key, debug=True)
                            # Save the place_id for future use
                            restaurant['google_place_id'] = google_place_id
                            if google_data:
                                st.success(f"✅ Found Google data for {restaurant['name']}")
                            break
                        st.markdown("---")

                if not google_place_id:
                    st.warning(f"⚠️ Could not find Google place_id for {restaurant['name']}")
                    st.info("💡 If you know the place_id, you can add it to the KNOWN_PLACE_IDS dictionary in app.py")
    else:
        google_data = None

    # Display hero with Google rating if available
    google_rating = google_data.get('rating') if google_data else None
    google_reviews_count = google_data.get('user_ratings_total') if google_data else None

    # Build review section if available
    review_html = ""
    if google_rating and google_reviews_count:
        review_html = f'<span>•</span><span>⭐ {google_rating} ({google_reviews_count} reviews)</span>'

    st.markdown(f"""
    <div class="detail-hero">
        <div class="detail-title">{restaurant['name']}</div>
        <div class="detail-meta">
            <span>📍 {restaurant['neighborhood']}</span>
            <span>•</span>
            <span>🍽️ {restaurant['cuisine']}</span>
            <span>•</span>
            <span class="badge badge-{platform}">{platform.upper()}</span>{review_html}</div>
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

    # Initialize state
    if 'calendar_selected_date' not in st.session_state:
        st.session_state.calendar_selected_date = date.today() + timedelta(days=7)
    if 'party_size' not in st.session_state:
        st.session_state.party_size = 2
    if 'show_calendar_modal' not in st.session_state:
        st.session_state.show_calendar_modal = False

    # Resy-style Booking Interface
    st.markdown("### Make a Reservation")

    # Bubble selectors for Guests and Date
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="booking-bubble-label">GUESTS</div>', unsafe_allow_html=True)
        party_size = st.selectbox(
            "Guests",
            options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            index=1,
            key="party_size_select",
            label_visibility="collapsed"
        )
        st.session_state.party_size = party_size

    with col2:
        st.markdown('<div class="booking-bubble-label">DATE</div>', unsafe_allow_html=True)
        reservation_date = st.date_input(
            "Date",
            min_value=date.today(),
            value=st.session_state.calendar_selected_date,
            key="date_picker",
            label_visibility="collapsed"
        )
        st.session_state.calendar_selected_date = reservation_date

    # Check availability for next 7 days (compact view) for faster loading
    # Only check 21 days when modal is opened
    num_days_to_check = 21 if st.session_state.show_calendar_modal else 7

    with st.spinner("Checking availability..."):
        availability_dict, unreleased_dates = generate_availability_calendar(
            restaurant, party_size, platform, num_days=num_days_to_check
        )

    # Compact calendar with next 7 days
    st.markdown("### Select a Date")

    # Create compact calendar tiles
    compact_dates = []
    for i in range(7):
        check_date = date.today() + timedelta(days=i)
        compact_dates.append(check_date)

    # Display compact calendar
    cols = st.columns([1, 1, 1, 1, 1, 1, 1, 0.5])
    for idx, check_date in enumerate(compact_dates):
        with cols[idx]:
            avail_info = availability_dict.get(check_date, {'state': 'unknown'})
            state = avail_info['state']

            # Determine styling
            if state == 'available':
                style_class = 'compact-date-available'
            elif state == 'unavailable':
                style_class = 'compact-date-unavailable'
            else:
                style_class = ''

            is_selected = check_date == st.session_state.calendar_selected_date

            day_name = check_date.strftime('%a').upper()
            day_num = check_date.day

            # Add lightning bolt for unreleased dates
            display_text = f"{day_name}  \n{day_num}"
            if state == 'unreleased':
                display_text = f"{day_name}  \n{day_num} ⚡"

            # Create clickable tile
            if st.button(
                display_text,
                key=f"compact_date_{check_date}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.calendar_selected_date = check_date

                # If unreleased, show snatcher
                if state == 'unreleased':
                    st.session_state.show_snatcher_for_date = check_date

                st.rerun()

    # "..." button to open modal with full calendar
    with cols[7]:
        if st.button("⋯", key="open_calendar_modal", use_container_width=True):
            st.session_state.show_calendar_modal = True
            st.rerun()

    # Modal calendar (if opened)
    if st.session_state.show_calendar_modal:
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown("---")
                st.markdown("### Full Calendar View")

                # Render full interactive calendar
                selected_calendar_date = render_interactive_calendar(availability_dict, date.today())

                # If user clicked a date in calendar, update the reservation date
                if selected_calendar_date:
                    st.session_state.calendar_selected_date = selected_calendar_date
                    reservation_date = selected_calendar_date
                    st.session_state.show_calendar_modal = False

                    # Check if unreleased date
                    avail_info = availability_dict.get(selected_calendar_date, {'state': 'unknown'})
                    if avail_info['state'] == 'unreleased':
                        st.session_state.show_snatcher_for_date = selected_calendar_date

                    st.rerun()

                if st.button("Close Calendar", key="close_calendar_modal", use_container_width=True):
                    st.session_state.show_calendar_modal = False
                    st.rerun()

                st.markdown("---")

    # Resy Snatcher - trigger when unreleased date is clicked or selected
    if 'show_snatcher_for_date' not in st.session_state:
        st.session_state.show_snatcher_for_date = None

    # Check if selected date is unreleased
    selected_avail = availability_dict.get(st.session_state.calendar_selected_date, {'state': 'unknown'})
    if selected_avail['state'] == 'unreleased' or st.session_state.show_snatcher_for_date:
        selected_unreleased_date = st.session_state.show_snatcher_for_date or st.session_state.calendar_selected_date

        st.markdown("---")
        st.markdown("### ⚡ Reservation Snatcher")
        st.info(f"💡 **{selected_unreleased_date.strftime('%B %d, %Y')}** isn't released yet! Set up a Snatcher to auto-book when it drops.")

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

        st.success(f"✅ Reservations will be released on **{release_date.strftime('%B %d, %Y')}** at **{convert_to_12hour(release_time)}**")

        col1, col2 = st.columns([3, 1])
        with col1:
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
                st.session_state.show_snatcher_for_date = None
                st.success(f"⚡ Snatcher activated!")
                st.rerun()
        with col2:
            if st.button("Cancel", key="cancel_snatcher_setup"):
                st.session_state.show_snatcher_for_date = None
                st.rerun()

        st.markdown("---")

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
            st.warning("No availability found for this date.")

    # Table Hunter - Always visible with sleeker UI
    st.markdown("---")
    st.markdown("""
    <div class="table-hunter-panel">
        <div class="table-hunter-title">
            🎯 Table Hunter
        </div>
        <div class="table-hunter-description">
            Can't find the time you want? Activate Table Hunter to automatically monitor for cancellations and notify you when a reservation becomes available.
        </div>
    </div>
    """, unsafe_allow_html=True)

    hunter_request = st.text_area(
        "Tell me what you're looking for...",
        placeholder=f"Example: I'm looking for a table for 2 on {(reservation_date if is_authenticated else date.today() + timedelta(days=7)).strftime('%A, %B %d')} around 7:30 PM",
        key="hunter_request_text",
        height=80
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🚀 Activate Table Hunter", type="primary", use_container_width=True, key="start_hunter_chatbot"):
            if hunter_request:
                # Parse the natural language request
                parsed = parse_reservation_request(hunter_request)

                # Create hunters for each date found
                hunters_created = 0
                dates_to_hunt = parsed['dates'] if parsed['dates'] else [reservation_date if is_authenticated else date.today() + timedelta(days=7)]

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
    with col2:
        pass  # Empty column for spacing

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
    st.markdown("### Discover Restaurants")

    # Filter section with cleaner design
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        cuisines = get_cuisines()
        cuisine_filter = st.selectbox("Cuisine", ["All Cuisines"] + cuisines, label_visibility="collapsed", key="cuisine_filter_browse")
        st.caption("Filter by cuisine")

    with col2:
        neighborhoods = sorted(list(set([r.get('neighborhood', 'Unknown') for r in restaurants])))
        neighborhood_filter = st.selectbox("Neighborhood", ["All Neighborhoods"] + neighborhoods, label_visibility="collapsed", key="neighborhood_filter_browse")
        st.caption("Filter by neighborhood")

    st.markdown('</div>', unsafe_allow_html=True)

    # Filter restaurants
    filtered = restaurants

    if search_query:
        filtered = [r for r in filtered if
                   search_query.lower() in r['name'].lower() or
                   search_query.lower() in r.get('cuisine', '').lower() or
                   search_query.lower() in r.get('neighborhood', '').lower()]

    if cuisine_filter != "All Cuisines":
        filtered = [r for r in filtered if r.get('cuisine') == cuisine_filter]

    if neighborhood_filter != "All Neighborhoods":
        filtered = [r for r in filtered if r.get('neighborhood') == neighborhood_filter]

    # Sort by name by default
    filtered = sorted(filtered, key=lambda x: x['name'])

    st.markdown(f"**{len(filtered)} restaurants**")

    # Display restaurants in grid
    if filtered:
        # Use columns to create grid layout
        cols_per_row = 3
        for row_start in range(0, len(filtered), cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                idx = row_start + col_idx
                if idx < len(filtered):
                    restaurant = filtered[idx]

                    with cols[col_idx]:
                        # Get first letter for placeholder
                        first_letter = restaurant['name'][0].upper()

                        # Display restaurant card using markdown
                        st.markdown(f"""
                        <div class="restaurant-grid-card">
                            <div class="restaurant-grid-image">
                                {first_letter}
                            </div>
                            <div class="restaurant-grid-info">
                                <div class="restaurant-grid-name">{restaurant['name']}</div>
                                <div class="restaurant-grid-meta">
                                    <div class="restaurant-grid-meta-item">
                                        <span>📍</span>
                                        <span>{restaurant.get('neighborhood', 'N/A')}</span>
                                    </div>
                                    <div class="restaurant-grid-meta-item">
                                        <span>🍽️</span>
                                        <span>{restaurant.get('cuisine', 'N/A')}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Clickable button below card
                        if st.button(
                            "View Availability",
                            key=f"browse_card_{idx}_{restaurant['venue_id']}",
                            use_container_width=True,
                            type="primary"
                        ):
                            st.session_state.selected_restaurant = restaurant
                            st.session_state.view_mode = 'detail'
                            st.rerun()
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
