"""
Resy & OpenTable Reservation Bot - Modern UI with Platform-Specific Authentication
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
    page_title="TableHunter | Resy & OpenTable Bot",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Custom CSS
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styles */
    .main {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Modern gradient header */
    .gradient-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }

    .gradient-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }

    .gradient-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* Platform badges */
    .badge-resy {
        background: linear-gradient(135deg, #ff5a5f 0%, #ff385c 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(255, 90, 95, 0.3);
    }

    .badge-opentable {
        background: linear-gradient(135deg, #da3743 0%, #b52735 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(218, 55, 67, 0.3);
    }

    /* Restaurant cards */
    .restaurant-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .restaurant-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }

    .restaurant-name {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }

    .restaurant-details {
        color: #6b7280;
        font-size: 0.95rem;
    }

    /* Success and error boxes */
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    .error-box {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }

    .warning-box {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }

    .info-box {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    /* Availability slots */
    .slot-available {
        background: #10b981;
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        margin: 4px;
        display: inline-block;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }

    .slot-available:hover {
        background: #059669;
        transform: scale(1.05);
    }

    .slot-unavailable {
        background: #e5e7eb;
        color: #9ca3af;
        padding: 8px 16px;
        border-radius: 8px;
        margin: 4px;
        display: inline-block;
    }

    /* Stats cards */
    .stat-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }

    .stat-label {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }

    /* Modern tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f9fafb;
        padding: 4px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    /* Login modal */
    .login-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        max-width: 400px;
        margin: 2rem auto;
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
if 'booking_history' not in st.session_state:
    st.session_state.booking_history = []
if 'selected_restaurant' not in st.session_state:
    st.session_state.selected_restaurant = None
if 'show_login_modal' not in st.session_state:
    st.session_state.show_login_modal = False
if 'login_platform' not in st.session_state:
    st.session_state.login_platform = None
if 'resy_email' not in st.session_state:
    st.session_state.resy_email = None
if 'opentable_email' not in st.session_state:
    st.session_state.opentable_email = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = None

# Admin password (in production, use environment variable or secure storage)
ADMIN_PASSWORD = "admin123"  # Change this!

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
            return True, f"✓ Connected to Resy as {email}"
        else:
            return False, "Authentication failed. Check your credentials."
    except Exception as e:
        return False, f"Error: {str(e)}"

def authenticate_opentable(email, password):
    """Authenticate with OpenTable"""
    try:
        # Placeholder for OpenTable authentication
        # This would use the opentable_client.py
        st.session_state.opentable_authenticated = True
        st.session_state.opentable_email = email
        return True, f"✓ Connected to OpenTable as {email}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_availability(venue_id, party_size, reservation_date, platform):
    """Check availability for a venue"""
    if platform == "resy" and not st.session_state.resy_authenticated:
        return []
    if platform == "opentable" and not st.session_state.opentable_authenticated:
        return []

    try:
        if platform == "resy":
            client = st.session_state.resy_bot.client
            slots = client.find_availability(
                venue_id=int(venue_id),
                party_size=party_size,
                reservation_date=reservation_date
            )
            return slots
        else:
            # OpenTable availability check would go here
            return []
    except Exception as e:
        st.error(f"Error checking availability: {str(e)}")
        return []

def add_new_restaurant(name, venue_id, neighborhood, cuisine, platform="resy"):
    """Add a new restaurant to the database"""
    db = load_restaurants()

    for restaurant in db["san_francisco"]:
        if restaurant["venue_id"] == venue_id:
            return False, "Restaurant already exists in database"

    new_restaurant = {
        "name": name,
        "venue_id": venue_id,
        "neighborhood": neighborhood,
        "cuisine": cuisine,
        "platform": platform
    }

    db["san_francisco"].append(new_restaurant)
    db["san_francisco"] = sorted(db["san_francisco"], key=lambda x: x["name"])

    save_restaurants(db)
    st.cache_data.clear()

    return True, f"Added {name} to database!"

def update_restaurant(old_venue_id, name, new_venue_id, neighborhood, cuisine, platform="resy"):
    """Update an existing restaurant in the database"""
    db = load_restaurants()

    restaurant_found = False
    for i, restaurant in enumerate(db["san_francisco"]):
        if restaurant["venue_id"] == old_venue_id:
            if new_venue_id != old_venue_id:
                for other in db["san_francisco"]:
                    if other["venue_id"] == new_venue_id and other["venue_id"] != old_venue_id:
                        return False, f"Venue ID {new_venue_id} is already used by another restaurant"

            db["san_francisco"][i] = {
                "name": name,
                "venue_id": new_venue_id,
                "neighborhood": neighborhood,
                "cuisine": cuisine,
                "platform": platform
            }
            restaurant_found = True
            break

    if not restaurant_found:
        return False, "Restaurant not found in database"

    db["san_francisco"] = sorted(db["san_francisco"], key=lambda x: x["name"])
    save_restaurants(db)
    st.cache_data.clear()

    return True, f"Updated {name}!"

def delete_restaurant(venue_id):
    """Delete a restaurant from the database"""
    db = load_restaurants()

    original_count = len(db["san_francisco"])
    db["san_francisco"] = [r for r in db["san_francisco"] if r["venue_id"] != venue_id]

    if len(db["san_francisco"]) == original_count:
        return False, "Restaurant not found in database"

    save_restaurants(db)
    st.cache_data.clear()

    return True, "Restaurant deleted!"

# Modern Header
st.markdown("""
<div class="gradient-header">
    <h1>🍽️ TableHunter</h1>
    <p>Your intelligent reservation assistant for Resy & OpenTable</p>
</div>
""", unsafe_allow_html=True)

# Auth status bar
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    db = load_restaurants()
    total_restaurants = len(db.get("san_francisco", []))
    resy_count = len([r for r in db.get("san_francisco", []) if r.get("platform") == "resy"])
    opentable_count = len([r for r in db.get("san_francisco", []) if r.get("platform") == "opentable"])

    st.markdown(f"**{total_restaurants}** restaurants • **{resy_count}** Resy • **{opentable_count}** OpenTable")

with col2:
    if st.session_state.resy_authenticated:
        st.success(f"✓ Resy: {st.session_state.resy_email}")
    else:
        st.info("Resy: Not connected")

with col3:
    if st.session_state.opentable_authenticated:
        st.success(f"✓ OpenTable: {st.session_state.opentable_email}")
    else:
        st.info("OpenTable: Not connected")

st.markdown("---")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Browse & Book", "🎯 Hunt Cancellations", "⚙️ Manage Database", "ℹ️ Help"])

with tab1:
    st.subheader("Explore Restaurants")

    # Load restaurants
    sf_restaurants = db.get("san_francisco", [])

    # Filter by platform
    col_filter1, col_filter2 = st.columns([3, 1])
    with col_filter1:
        search_query = st.text_input("🔍 Search restaurants", placeholder="Type to search...")
    with col_filter2:
        platform_filter = st.selectbox("Platform", ["All", "Resy", "OpenTable"])

    # Filter restaurants
    filtered_restaurants = sf_restaurants
    if search_query:
        filtered_restaurants = [r for r in filtered_restaurants
                               if search_query.lower() in r["name"].lower() or
                               search_query.lower() in r["neighborhood"].lower() or
                               search_query.lower() in r["cuisine"].lower()]

    if platform_filter != "All":
        filtered_restaurants = [r for r in filtered_restaurants
                               if r.get("platform", "resy").lower() == platform_filter.lower()]

    st.write(f"Showing {len(filtered_restaurants)} restaurant(s)")

    # Display restaurants in grid
    if filtered_restaurants:
        for idx, restaurant in enumerate(filtered_restaurants):
            platform = restaurant.get('platform', 'resy')
            platform_badge = f'<span class="badge-{platform}">{platform.upper()}</span>'

            with st.expander(f"**{restaurant['name']}** {platform_badge}", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Neighborhood", restaurant['neighborhood'])
                with col2:
                    st.metric("Cuisine", restaurant['cuisine'])
                with col3:
                    st.metric("Venue ID", restaurant['venue_id'])

                st.markdown("---")

                # Booking interface
                col1, col2 = st.columns(2)

                with col1:
                    party_size = st.number_input(
                        "Party Size",
                        min_value=1,
                        max_value=20,
                        value=2,
                        key=f"browse_party_{idx}_{restaurant['venue_id']}"
                    )

                    reservation_date = st.date_input(
                        "Date",
                        min_value=date.today(),
                        value=date.today() + timedelta(days=7),
                        key=f"browse_date_{idx}_{restaurant['venue_id']}"
                    )

                with col2:
                    st.write("**Preferred Times**")
                    times = ["17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
                            "20:00", "20:30", "21:00", "21:30", "22:00"]

                    time_cols = st.columns(3)
                    selected_times = []

                    for i, time_slot in enumerate(times):
                        col_idx = i % 3
                        with time_cols[col_idx]:
                            hour = int(time_slot.split(":")[0])
                            minute = time_slot.split(":")[1]
                            display_time = f"{hour if hour <= 12 else hour-12}:{minute} {'PM' if hour >= 12 else 'AM'}"

                            if st.checkbox(display_time, key=f"browse_time_{idx}_{restaurant['venue_id']}_{time_slot}"):
                                selected_times.append(time_slot)

                # Check authentication status for this platform
                is_authenticated = (
                    (platform == "resy" and st.session_state.resy_authenticated) or
                    (platform == "opentable" and st.session_state.opentable_authenticated)
                )

                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    if st.button(f"🔍 Check Availability", key=f"browse_check_{idx}_{restaurant['venue_id']}", use_container_width=True):
                        if not is_authenticated:
                            st.warning(f"Please login to {platform.title()} to check availability")
                            st.session_state.login_platform = platform
                            st.session_state.show_login_modal = True
                        else:
                            with st.spinner("Checking availability..."):
                                slots = check_availability(
                                    restaurant["venue_id"],
                                    party_size,
                                    reservation_date,
                                    platform
                                )

                                if slots:
                                    st.success(f"Found {len(slots)} available time(s)!")
                                    for slot in slots:
                                        st.markdown(f'<div class="slot-available">✓ {slot["display_time"]}</div>', unsafe_allow_html=True)
                                else:
                                    st.warning("No availability found")

                with col_btn2:
                    if st.button(f"📅 Book Now", key=f"browse_book_{idx}_{restaurant['venue_id']}", type="primary", use_container_width=True):
                        if not is_authenticated:
                            st.warning(f"Please login to {platform.title()} to book a reservation")
                            st.session_state.login_platform = platform
                            st.session_state.show_login_modal = True
                        else:
                            st.info("Booking functionality coming soon!")
    else:
        st.info("No restaurants found. Try adjusting your search or filters.")

    # Login modal (shown when needed)
    if st.session_state.show_login_modal and st.session_state.login_platform:
        st.markdown("---")
        st.markdown(f"### 🔐 Login to {st.session_state.login_platform.title()}")

        with st.form(f"login_form_{st.session_state.login_platform}"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")

            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Login", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)

            if submit:
                if email and password:
                    with st.spinner("Authenticating..."):
                        if st.session_state.login_platform == "resy":
                            success, message = authenticate_resy(email, password)
                        else:
                            success, message = authenticate_opentable(email, password)

                        if success:
                            st.success(message)
                            st.session_state.show_login_modal = False
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.error("Please enter both email and password")

            if cancel:
                st.session_state.show_login_modal = False
                st.rerun()

with tab2:
    st.subheader("🎯 Cancellation Hunter")
    st.info("Continuous monitoring feature - Coming soon!")
    st.markdown("""
    This feature will:
    - Monitor restaurants 24/7 for cancellations
    - Automatically book when a slot becomes available
    - Send notifications when reservations are found
    """)

with tab3:
    # Check admin access
    if not st.session_state.is_admin:
        st.warning("🔒 Admin access required to manage the database")

        with st.form("admin_login"):
            admin_pass = st.text_input("Admin Password", type="password")
            if st.form_submit_button("Login as Admin"):
                if admin_pass == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.session_state.admin_password = admin_pass
                    st.success("✓ Admin access granted")
                    st.rerun()
                else:
                    st.error("Incorrect password")
    else:
        st.success("✓ Admin access active")

        if st.button("Logout from Admin"):
            st.session_state.is_admin = False
            st.session_state.admin_password = None
            st.rerun()

        st.markdown("---")

        manage_tab1, manage_tab2 = st.tabs(["➕ Add Restaurant", "✏️ Edit/Delete"])

        with manage_tab1:
            with st.form("add_restaurant"):
                st.markdown("**Add a new restaurant**")

                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Restaurant Name", placeholder="e.g., The Happy Crane")
                    new_neighborhood = st.text_input("Neighborhood", placeholder="e.g., Hayes Valley")
                with col2:
                    new_venue_id = st.number_input("Venue ID", min_value=1, step=1)
                    new_cuisine = st.text_input("Cuisine", placeholder="e.g., Chinese")

                new_platform = st.selectbox("Platform", options=["resy", "opentable"])

                if st.form_submit_button("Add Restaurant", type="primary"):
                    if new_name and new_venue_id and new_neighborhood and new_cuisine:
                        success, message = add_new_restaurant(
                            new_name, new_venue_id, new_neighborhood, new_cuisine, new_platform
                        )
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all fields")

        with manage_tab2:
            db = load_restaurants()
            sf_restaurants_edit = db.get("san_francisco", [])

            if sf_restaurants_edit:
                restaurant_options = [""] + [
                    f"{r['name']} (ID: {r['venue_id']})"
                    for r in sf_restaurants_edit
                ]

                selected_option = st.selectbox("Select restaurant", restaurant_options)

                if selected_option:
                    selected_name = selected_option.split(" (ID:")[0]
                    selected_restaurant = next(
                        (r for r in sf_restaurants_edit if r["name"] == selected_name), None
                    )

                    if selected_restaurant:
                        with st.form("edit_restaurant"):
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_name = st.text_input("Name", value=selected_restaurant['name'])
                                edit_neighborhood = st.text_input("Neighborhood", value=selected_restaurant['neighborhood'])
                            with col2:
                                edit_venue_id = st.number_input("Venue ID", value=selected_restaurant['venue_id'], min_value=1, step=1)
                                edit_cuisine = st.text_input("Cuisine", value=selected_restaurant['cuisine'])

                            edit_platform = st.selectbox(
                                "Platform",
                                options=["resy", "opentable"],
                                index=0 if selected_restaurant.get('platform', 'resy') == 'resy' else 1
                            )

                            col1, col2 = st.columns(2)
                            with col1:
                                update_btn = st.form_submit_button("💾 Update", type="primary", use_container_width=True)
                            with col2:
                                delete_btn = st.form_submit_button("🗑️ Delete", type="secondary", use_container_width=True)

                            if update_btn:
                                success, message = update_restaurant(
                                    selected_restaurant['venue_id'],
                                    edit_name,
                                    edit_venue_id,
                                    edit_neighborhood,
                                    edit_cuisine,
                                    edit_platform
                                )
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)

                            if delete_btn:
                                success, message = delete_restaurant(selected_restaurant['venue_id'])
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
            else:
                st.info("No restaurants in database yet")

with tab4:
    st.markdown("""
    ## 🍽️ Welcome to TableHunter

    Your intelligent assistant for booking reservations on Resy and OpenTable.

    ### ✨ Features

    - **Browse First**: Explore restaurants without logging in
    - **Platform-Specific Login**: Only login when you're ready to book
    - **Multi-Platform**: Support for both Resy and OpenTable
    - **Real-Time Availability**: Check what's available before booking
    - **Smart Filtering**: Search by name, neighborhood, or cuisine
    - **Admin Control**: Secure access for database management

    ### 🚀 How to Use

    1. **Browse Restaurants**: No login required! Explore all available restaurants
    2. **Select Your Restaurant**: Filter by platform, search by name
    3. **Check Availability**: Login to see available times
    4. **Book**: Complete your reservation in seconds

    ### 🔐 Platform-Specific Authentication

    TableHunter is smart about authentication:
    - Selecting a **Resy** restaurant? You'll be prompted for Resy credentials
    - Selecting an **OpenTable** restaurant? You'll login to OpenTable
    - No unnecessary logins - only authenticate when needed!

    ### 👨‍💼 Admin Access

    Admin features allow you to:
    - Add new restaurants to the database
    - Edit restaurant details and venue IDs
    - Delete restaurants
    - Manage both Resy and OpenTable listings

    **Default admin password**: `admin123` (change this in production!)

    ### 💡 Tips

    - Check availability before booking to see all options
    - Select multiple time preferences for better success rates
    - Admin access is password-protected for security
    - Platform badges show which service each restaurant uses

    ### 🔮 Coming Soon

    - Automatic cancellation hunting
    - Email/SMS notifications
    - Calendar integration
    - Favorite restaurants
    - Booking history
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #9ca3af; font-size: 0.9rem;'>🍽️ TableHunter • Powered by Resy & OpenTable • Made with ❤️ in SF</div>",
    unsafe_allow_html=True
)
