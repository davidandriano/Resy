"""
Reservation Hunter - Resy-Inspired Modern Design
"""
import streamlit as st
from datetime import date, datetime, timedelta
from bot import ResyBot
from config import ReservationConfig, load_settings
import json
import os
import time

# Configure page
st.set_page_config(
    page_title="Reservation Hunter",
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

# Custom Header
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.markdown('<div class="logo">Reservation Hunter</div>', unsafe_allow_html=True)

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

    # Restaurant hero section
    st.markdown(f"""
    <div class="detail-hero">
        <div class="detail-title">{restaurant['name']}</div>
        <div class="detail-meta">
            <span>📍 {restaurant['neighborhood']}</span>
            <span>🍽️ {restaurant['cuisine']}</span>
            <span><span class="badge badge-{platform}">{platform.upper()}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
                    if st.button(time_str, key=f"slot_{idx}", use_container_width=True):
                        st.success(f"Selected {time_str}")
                        st.info("Booking functionality coming soon!")

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No availability for this date. Try another date or party size.")

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
    "<div style='text-align: center; color: #999; font-size: 0.9rem; padding: 2rem 0;'>Reservation Hunter • San Francisco</div>",
    unsafe_allow_html=True
)
