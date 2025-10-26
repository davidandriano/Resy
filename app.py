"""
Resy Reservation Bot - Streamlit Web UI with Restaurant Search
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
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'monitoring_config' not in st.session_state:
    st.session_state.monitoring_config = None
if 'attempt_count' not in st.session_state:
    st.session_state.attempt_count = 0
if 'last_check_time' not in st.session_state:
    st.session_state.last_check_time = None
if 'monitoring_status' not in st.session_state:
    st.session_state.monitoring_status = ""
if 'scheduled_start_time' not in st.session_state:
    st.session_state.scheduled_start_time = None
if 'waiting_for_scheduled_start' not in st.session_state:
    st.session_state.waiting_for_scheduled_start = False
if 'check_interval' not in st.session_state:
    st.session_state.check_interval = 5

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

def perform_monitoring_check():
    """Perform a single monitoring check and attempt booking"""
    if not st.session_state.monitoring_active or not st.session_state.monitoring_config:
        return False

    st.session_state.attempt_count += 1
    st.session_state.last_check_time = datetime.now().strftime("%H:%M:%S")

    try:
        config = st.session_state.monitoring_config
        confirmation = st.session_state.bot.attempt_booking(config)

        if confirmation:
            st.session_state.monitoring_active = False
            st.session_state.monitoring_status = "SUCCESS"
            return True
        else:
            st.session_state.monitoring_status = f"No availability found (Attempt #{st.session_state.attempt_count})"
            return False
    except Exception as e:
        st.session_state.monitoring_status = f"Error: {str(e)}"
        return False

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

    # Monitoring Status
    if st.session_state.monitoring_active:
        st.success("🟢 Monitoring Active")
        if st.session_state.monitoring_config:
            st.write(f"**{st.session_state.monitoring_config.restaurant_name}**")
            st.caption(f"{st.session_state.attempt_count} attempts")
    elif st.session_state.waiting_for_scheduled_start:
        st.info("⏰ Scheduled Start")
        if st.session_state.monitoring_config:
            st.write(f"**{st.session_state.monitoring_config.restaurant_name}**")

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
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Book Reservation", "🔍 Monitor & Hunt", "➕ Add Restaurant", "ℹ️ Help"])

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
        st.subheader("🔍 Continuous Monitoring & Cancellation Hunter")

        st.markdown("""
        This feature continuously monitors for availability and automatically books when a reservation becomes available.
        Perfect for **cancellation hunting** at popular restaurants!
        """)

        # Check if waiting for scheduled start
        if st.session_state.waiting_for_scheduled_start:
            current_time = datetime.now()
            scheduled_time = st.session_state.scheduled_start_time

            st.markdown("""
            <div class="info-box">
                <h3>⏰ Waiting for Scheduled Start Time</h3>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Time", current_time.strftime("%H:%M:%S"))
            with col2:
                st.metric("Start Time", scheduled_time.strftime("%H:%M:%S"))
            with col3:
                time_diff = (scheduled_time - current_time).total_seconds()
                minutes_left = int(time_diff // 60)
                seconds_left = int(time_diff % 60)
                st.metric("Time Until Start", f"{minutes_left}m {seconds_left}s")

            if st.button("⏹️ Cancel Scheduled Start", type="secondary", use_container_width=True):
                st.session_state.waiting_for_scheduled_start = False
                st.session_state.scheduled_start_time = None
                st.session_state.monitoring_config = None
                st.rerun()

            # Check if it's time to start
            if current_time >= scheduled_time:
                st.session_state.waiting_for_scheduled_start = False
                st.session_state.monitoring_active = True
                st.session_state.attempt_count = 0
                st.session_state.monitoring_status = "Starting monitoring..."
                st.rerun()
            else:
                # Wait and refresh
                time.sleep(1)
                st.rerun()

        # Monitoring status display
        elif st.session_state.monitoring_active:
            st.markdown("""
            <div class="success-box">
                <h3>🟢 Monitoring Active</h3>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Attempts", st.session_state.attempt_count)
            with col2:
                st.metric("Last Check", st.session_state.last_check_time or "Starting...")
            with col3:
                if st.button("⏹️ Stop Monitoring", type="secondary", use_container_width=True):
                    st.session_state.monitoring_active = False
                    st.session_state.monitoring_config = None
                    st.rerun()

            st.info(st.session_state.monitoring_status)

            # Auto-refresh for continuous monitoring
            time.sleep(st.session_state.check_interval)
            success = perform_monitoring_check()

            if success:
                st.balloons()
                config = st.session_state.monitoring_config
                st.markdown(f"""
                <div class="success-box">
                    <h3>🎉 RESERVATION BOOKED!</h3>
                    <p><strong>Restaurant:</strong> {config.restaurant_name}</p>
                    <p><strong>Date:</strong> {config.reservation_date}</p>
                    <p><strong>Party Size:</strong> {config.party_size}</p>
                    <p><strong>Total Attempts:</strong> {st.session_state.attempt_count}</p>
                </div>
                """, unsafe_allow_html=True)

                st.session_state.booking_history.append({
                    'restaurant': config.restaurant_name,
                    'date': str(config.reservation_date),
                    'time': datetime.now().strftime("%H:%M"),
                    'status': 'Success'
                })
            else:
                st.rerun()

        else:
            # Setup monitoring
            st.markdown("### Set Up Monitoring")

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
                "🔍 Select Restaurant to Monitor",
                options=restaurant_options,
                index=0,
                help="Select a restaurant to monitor for availability"
            )

            selected_restaurant = None
            if selected_option:
                restaurant_name = selected_option.split(" - ")[0]
                selected_restaurant = next(
                    (r for r in sf_restaurants if r["name"] == restaurant_name),
                    None
                )

            if selected_restaurant:
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

                    check_interval = st.number_input(
                        "Check Interval (seconds)",
                        min_value=3,
                        max_value=60,
                        value=5,
                        help="How often to check (5 seconds recommended for cancellation hunting)"
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

                            if st.checkbox(display_time, key=f"monitor_time_{time_slot}"):
                                selected_times.append(time_slot)

                    auto_accept = st.checkbox(
                        "Accept any available time",
                        value=True,
                        help="Recommended: Book any time if preferred times are unavailable"
                    )

                st.divider()

                # Scheduled start option
                use_scheduled_start = st.checkbox(
                    "⏰ Schedule Start Time",
                    help="Start monitoring at a specific time (e.g., midnight when reservations release)"
                )

                scheduled_time_input = None
                if use_scheduled_start:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        scheduled_date = st.date_input(
                            "Start Date",
                            value=date.today(),
                            min_value=date.today(),
                            help="Date to start monitoring"
                        )
                    with col_b:
                        scheduled_time = st.time_input(
                            "Start Time",
                            value=datetime.strptime("00:00", "%H:%M").time(),
                            help="Time to start monitoring (e.g., 00:00 for midnight)"
                        )

                    scheduled_time_input = datetime.combine(scheduled_date, scheduled_time)

                    if scheduled_time_input <= datetime.now():
                        st.warning("⚠️ Scheduled time must be in the future")

                st.divider()

                # Action buttons
                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    if st.button("🚀 Start Now", type="primary", use_container_width=True):
                        if not selected_times and not auto_accept:
                            st.error("Select at least one time or enable 'Accept any time'")
                        else:
                            # Create reservation config
                            config = ReservationConfig(
                                restaurant_name=selected_restaurant["name"],
                                party_size=party_size,
                                reservation_date=reservation_date,
                                preferred_times=selected_times,
                                location="sf",
                                auto_accept_any_time=auto_accept
                            )
                            config.venue_id = selected_restaurant["venue_id"]

                            # Start monitoring immediately
                            st.session_state.monitoring_active = True
                            st.session_state.monitoring_config = config
                            st.session_state.attempt_count = 0
                            st.session_state.check_interval = check_interval
                            st.session_state.monitoring_status = "Starting monitoring..."
                            st.rerun()

                with col_btn2:
                    if use_scheduled_start:
                        if st.button("⏰ Schedule Start", type="secondary", use_container_width=True):
                            if not selected_times and not auto_accept:
                                st.error("Select at least one time or enable 'Accept any time'")
                            elif not scheduled_time_input or scheduled_time_input <= datetime.now():
                                st.error("Scheduled time must be in the future")
                            else:
                                # Create reservation config
                                config = ReservationConfig(
                                    restaurant_name=selected_restaurant["name"],
                                    party_size=party_size,
                                    reservation_date=reservation_date,
                                    preferred_times=selected_times,
                                    location="sf",
                                    auto_accept_any_time=auto_accept
                                )
                                config.venue_id = selected_restaurant["venue_id"]

                                # Schedule monitoring
                                st.session_state.waiting_for_scheduled_start = True
                                st.session_state.scheduled_start_time = scheduled_time_input
                                st.session_state.monitoring_config = config
                                st.session_state.check_interval = check_interval
                                st.session_state.attempt_count = 0
                                st.rerun()

            else:
                st.info("👆 Select a restaurant to start monitoring")

    with tab3:
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

    with tab4:
        st.subheader("How to Use")

        st.markdown("""
        ### 🎯 Quick Start - Manual Booking

        1. **Select a Restaurant** (Book Reservation tab)
           - Click the dropdown and start typing
           - Select your restaurant from the list

        2. **Choose Your Details**
           - Select date and party size
           - Pick preferred times (you can select multiple)

        3. **Book**
           - Click "Check Availability" to see what's open
           - Click "Book Now" to reserve immediately

        ### 🔍 Cancellation Hunting - Automated

        Perfect for popular restaurants that are fully booked!

        1. **Go to "Monitor & Hunt" tab**
        2. **Select your restaurant and preferences**
        3. **Click "Start Monitoring"**
        4. **Keep browser open** - the bot will continuously check every 5 seconds
        5. **Automatic booking** when a spot opens up!

        ### ✨ Features

        - **Searchable Database**: Type to filter restaurants
        - **Manual Booking**: Instant one-time reservations
        - **Continuous Monitoring**: Automated cancellation hunting
        - **Auto-Accept Option**: Grab any available time slot
        - **Real-time Status**: See attempt count and last check time
        - **SF Focused**: Curated list of San Francisco restaurants
        - **Expandable**: Add new restaurants as you discover them

        ### 📍 Expanding the Database

        Don't see your favorite restaurant?
        - Go to the "Add Restaurant" tab
        - Enter the details and venue ID
        - It will be added to the searchable list!

        ### 💡 Tips for Success

        - **Manual Booking**: Best for dates with existing availability
        - **Monitoring Mode**: Essential for fully-booked popular restaurants
        - **Multiple Times**: Select several preferred times to increase success rate
        - **Auto-Accept**: Enable for best results when hunting cancellations
        - **Check Interval**: 5 seconds is optimal (faster may trigger rate limits)
        - **Keep Browser Open**: Monitoring stops if you close the tab

        ### ⏰ Time Reference

        All times shown in 12-hour format (AM/PM) for convenience

        ### 🎯 Best Use Cases

        - **Manual Booking**: Restaurant has availability, you want a specific time
        - **Monitoring Mode**: Restaurant is fully booked, waiting for cancellations
        - **Scheduled Monitoring**: Set it up before release times (e.g., midnight)
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>🍽️ Resy Bot • San Francisco Edition</div>",
    unsafe_allow_html=True
)
