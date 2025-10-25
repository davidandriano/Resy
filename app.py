"""
Resy Reservation Bot - Streamlit Web UI with Restaurant Search
"""
import streamlit as st
from datetime import date, datetime, timedelta
from bot import ResyBot
from config import ReservationConfig, load_settings
import json
import os

# Configure page
st.set_page_config(
    page_title="Resy Reservation Bot",
    page_icon="🍽️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        color: #721c24;
        margin: 1rem 0;
    }
    .restaurant-card {
        padding: 0.5rem;
        border-left: 3px solid #007bff;
        background-color: #f8f9fa;
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
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'bot' not in st.session_state:
    st.session_state.bot = None
if 'booking_history' not in st.session_state:
    st.session_state.booking_history = []
if 'selected_restaurant' not in st.session_state:
    st.session_state.selected_restaurant = None

def authenticate_bot():
    """Authenticate the bot with Resy"""
    try:
        settings = load_settings()
        bot = ResyBot(settings)

        if bot.authenticate():
            st.session_state.bot = bot
            st.session_state.authenticated = True
            return True, "Successfully connected to Resy!"
        else:
            return False, "Authentication failed. Check your .env credentials."
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_availability(venue_id, party_size, reservation_date):
    """Check availability for a venue"""
    if not st.session_state.authenticated:
        return []

    try:
        client = st.session_state.bot.client
        slots = client.find_availability(
            venue_id=int(venue_id),
            party_size=party_size,
            reservation_date=reservation_date
        )
        return slots
    except Exception as e:
        st.error(f"Error checking availability: {str(e)}")
        return []

def add_new_restaurant(name, venue_id, neighborhood, cuisine):
    """Add a new restaurant to the database"""
    db = load_restaurants()

    # Check if already exists
    for restaurant in db["san_francisco"]:
        if restaurant["venue_id"] == venue_id:
            return False, "Restaurant already exists in database"

    new_restaurant = {
        "name": name,
        "venue_id": venue_id,
        "neighborhood": neighborhood,
        "cuisine": cuisine
    }

    db["san_francisco"].append(new_restaurant)
    db["san_francisco"] = sorted(db["san_francisco"], key=lambda x: x["name"])

    save_restaurants(db)
    st.cache_data.clear()  # Clear cache to reload data

    return True, f"Added {name} to database!"

# Header
st.markdown('<div class="main-header">🍽️ Resy Reservation Bot</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Status")

    if not st.session_state.authenticated:
        st.warning("Not connected to Resy")
        if st.button("Connect to Resy", type="primary"):
            with st.spinner("Connecting..."):
                success, message = authenticate_bot()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.success("✓ Connected to Resy")
        payment_methods = st.session_state.bot.client.payment_method_id
        if payment_methods:
            st.info("✓ Payment method found")

        if st.button("Disconnect"):
            st.session_state.authenticated = False
            st.session_state.bot = None
            st.rerun()

    st.divider()

    # Database stats
    db = load_restaurants()
    sf_count = len(db.get("san_francisco", []))
    st.metric("SF Restaurants", sf_count)

    st.divider()

    # Booking History
    if st.session_state.booking_history:
        st.header("Recent Bookings")
        for booking in reversed(st.session_state.booking_history[-3:]):
            status_icon = "✓" if booking['status'] == 'Success' else "✗"
            st.write(f"{status_icon} {booking['restaurant']}")
            st.caption(f"{booking['date']} at {booking['time']}")

# Main content
if not st.session_state.authenticated:
    st.info("👆 Click 'Connect to Resy' in the sidebar to get started")

    st.markdown("---")
    st.subheader("Quick Setup")
    st.markdown("""
    1. Make sure your `.env` file is configured with your Resy credentials
    2. Click "Connect to Resy" in the sidebar
    3. Start booking reservations!
    """)

else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📅 Book Reservation", "➕ Add Restaurant", "ℹ️ Help"])

    with tab1:
        st.subheader("Find & Book a Restaurant")

        # Load restaurant database
        db = load_restaurants()
        sf_restaurants = db.get("san_francisco", [])

        # Create searchable list
        restaurant_options = [""] + [
            f"{r['name']} - {r['neighborhood']} ({r['cuisine']})"
            for r in sf_restaurants
        ]

        # Searchable dropdown
        selected_option = st.selectbox(
            "🔍 Search for a Restaurant in San Francisco",
            options=restaurant_options,
            index=0,
            help="Start typing to search. Select a restaurant from the dropdown."
        )

        selected_restaurant = None
        if selected_option:
            # Extract restaurant name from selection
            restaurant_name = selected_option.split(" - ")[0]
            selected_restaurant = next(
                (r for r in sf_restaurants if r["name"] == restaurant_name),
                None
            )

        # Show selected restaurant details
        if selected_restaurant:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Restaurant", selected_restaurant["name"])
            with col2:
                st.metric("Neighborhood", selected_restaurant["neighborhood"])
            with col3:
                st.metric("Cuisine", selected_restaurant["cuisine"])

            st.divider()

            # Booking details
            col1, col2 = st.columns(2)

            with col1:
                party_size = st.number_input(
                    "Party Size",
                    min_value=1,
                    max_value=20,
                    value=2,
                    help="Number of people"
                )

                reservation_date = st.date_input(
                    "Reservation Date",
                    min_value=date.today(),
                    value=date.today() + timedelta(days=7),
                    help="Date for your reservation"
                )

            with col2:
                st.write("**Preferred Times** (select multiple)")

                times = [
                    "17:00", "17:30", "18:00", "18:30",
                    "19:00", "19:30", "20:00", "20:30",
                    "21:00", "21:30", "22:00", "22:30"
                ]

                time_cols = st.columns(3)
                selected_times = []

                for i, time_slot in enumerate(times):
                    col_idx = i % 3
                    with time_cols[col_idx]:
                        hour = int(time_slot.split(":")[0])
                        minute = time_slot.split(":")[1]
                        display_time = f"{hour if hour <= 12 else hour-12}:{minute} {'PM' if hour >= 12 else 'AM'}"

                        if st.checkbox(display_time, key=f"time_{time_slot}"):
                            selected_times.append(time_slot)

                auto_accept = st.checkbox(
                    "Accept any available time",
                    help="Book any time if preferred times are unavailable"
                )

            st.divider()

            # Action buttons
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔍 Check Availability", type="secondary", use_container_width=True):
                    if not selected_times and not auto_accept:
                        st.error("Select at least one time or enable 'Accept any time'")
                    else:
                        with st.spinner("Checking availability..."):
                            slots = check_availability(
                                selected_restaurant["venue_id"],
                                party_size,
                                reservation_date
                            )

                            if slots:
                                st.success(f"Found {len(slots)} available time(s)!")
                                st.write("**Available Times:**")
                                for slot in slots:
                                    st.write(f"✓ {slot['display_time']} - {slot['type']}")
                            else:
                                st.warning("No availability found for this date")

            with col2:
                if st.button("📅 Book Now", type="primary", use_container_width=True):
                    if not selected_times and not auto_accept:
                        st.error("Select at least one time or enable 'Accept any time'")
                    else:
                        with st.spinner("Booking reservation..."):
                            config = ReservationConfig(
                                restaurant_name=selected_restaurant["name"],
                                party_size=party_size,
                                reservation_date=reservation_date,
                                preferred_times=selected_times,
                                location="sf",
                                auto_accept_any_time=auto_accept
                            )
                            config.venue_id = selected_restaurant["venue_id"]

                            confirmation = st.session_state.bot.attempt_booking(config)

                            if confirmation:
                                st.balloons()
                                st.markdown(f"""
                                <div class="success-box">
                                    <h3>🎉 Reservation Booked!</h3>
                                    <p><strong>Restaurant:</strong> {selected_restaurant['name']}</p>
                                    <p><strong>Date:</strong> {reservation_date}</p>
                                    <p><strong>Party Size:</strong> {party_size}</p>
                                </div>
                                """, unsafe_allow_html=True)

                                st.session_state.booking_history.append({
                                    'restaurant': selected_restaurant['name'],
                                    'date': str(reservation_date),
                                    'time': datetime.now().strftime("%H:%M"),
                                    'status': 'Success'
                                })
                            else:
                                st.markdown("""
                                <div class="error-box">
                                    <h3>❌ Could Not Book</h3>
                                    <p>Try different times or enable 'Accept any time'</p>
                                </div>
                                """, unsafe_allow_html=True)

                                st.session_state.booking_history.append({
                                    'restaurant': selected_restaurant['name'],
                                    'date': str(reservation_date),
                                    'time': datetime.now().strftime("%H:%M"),
                                    'status': 'Failed'
                                })

        else:
            st.info("👆 Select a restaurant from the dropdown above to get started")

    with tab2:
        st.subheader("Add a New Restaurant to Database")

        st.markdown("""
        Can't find your restaurant? Add it here! You'll need to find the venue ID first:
        1. Go to the restaurant's page on resy.com
        2. Look at the URL or use browser dev tools to find the venue ID
        """)

        with st.form("add_restaurant"):
            new_name = st.text_input("Restaurant Name", placeholder="e.g., Zuni Cafe")
            new_venue_id = st.number_input("Venue ID", min_value=1, step=1)
            new_neighborhood = st.text_input("Neighborhood", placeholder="e.g., Hayes Valley")
            new_cuisine = st.text_input("Cuisine Type", placeholder="e.g., Mediterranean")

            submitted = st.form_submit_button("Add Restaurant", type="primary")

            if submitted:
                if new_name and new_venue_id and new_neighborhood and new_cuisine:
                    success, message = add_new_restaurant(
                        new_name,
                        new_venue_id,
                        new_neighborhood,
                        new_cuisine
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields")

        st.divider()

        st.subheader("Current Database")
        if sf_restaurants:
            for restaurant in sf_restaurants:
                st.markdown(f"""
                <div class="restaurant-card">
                    <strong>{restaurant['name']}</strong><br>
                    <small>{restaurant['neighborhood']} • {restaurant['cuisine']} • ID: {restaurant['venue_id']}</small>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        st.subheader("How to Use")

        st.markdown("""
        ### 🎯 Quick Start

        1. **Select a Restaurant**
           - Click the dropdown and start typing
           - Select your restaurant from the list

        2. **Choose Your Details**
           - Select date and party size
           - Pick preferred times (you can select multiple)

        3. **Book**
           - Click "Check Availability" to see what's open
           - Click "Book Now" to reserve

        ### ✨ Features

        - **Searchable Database**: Type to filter restaurants
        - **SF Focused**: Curated list of San Francisco restaurants
        - **Easy to Expand**: Add new restaurants as you discover them
        - **Auto-Complete**: Fast, responsive search

        ### 📍 Expanding the Database

        Don't see your favorite restaurant?
        - Go to the "Add Restaurant" tab
        - Enter the details and venue ID
        - It will be added to the searchable list!

        ### 💡 Tips

        - Select multiple preferred times for better chances
        - Enable "Accept any time" for very popular spots
        - Add restaurants you use frequently to build your database

        ### ⏰ Time Reference

        All times shown in 12-hour format (AM/PM) for convenience
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>🍽️ Resy Bot • San Francisco Edition</div>",
    unsafe_allow_html=True
)
