"""
Resy Reservation Bot - Streamlit Web UI (Updated with URL parser)
"""
import streamlit as st
from datetime import date, datetime, timedelta
from bot import ResyBot
from config import ReservationConfig, load_settings
from resy_client import ResyClient
import re
import logging

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
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        color: #0c5460;
        margin: 1rem 0;
    }
    .url-helper {
        padding: 1.5rem;
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'bot' not in st.session_state:
    st.session_state.bot = None
if 'booking_history' not in st.session_state:
    st.session_state.booking_history = []
if 'venue_id' not in st.session_state:
    st.session_state.venue_id = None
if 'restaurant_name' not in st.session_state:
    st.session_state.restaurant_name = None

def extract_venue_from_url(url):
    """Extract venue info from Resy URL"""
    # Extract slug from URL
    slug_match = re.search(r'/venues/([a-z0-9-]+)', url)
    if slug_match:
        slug = slug_match.group(1)
        # Clean up restaurant name from slug
        name = slug.replace('-', ' ').title()
        return slug, name

    return None, None

def get_venue_id_from_slug(slug, location):
    """Get venue ID from slug using the API"""
    if not st.session_state.authenticated:
        return None

    try:
        client = st.session_state.bot.client
        url = f"{client.BASE_URL}/3/venue?url_slug={slug}&location={location}"

        response = client.session.get(url)
        response.raise_for_status()

        data = response.json()
        venue_id = data.get("id", {}).get("resy")
        return venue_id
    except:
        return None

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

# Header
st.markdown('<div class="main-header">🍽️ Resy Reservation Bot</div>', unsafe_allow_html=True)

# Sidebar - Authentication Status
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

    # Quick venue lookup
    if st.session_state.authenticated:
        st.header("Quick Venue Lookup")
        st.markdown("**Known Venue IDs:**")
        st.code("Izakaya Rintaro (SF): 339")

    st.divider()

    # Booking History
    if st.session_state.booking_history:
        st.header("Recent Attempts")
        for i, booking in enumerate(reversed(st.session_state.booking_history[-5:])):
            with st.expander(f"{booking['restaurant']} - {booking['date']}", expanded=False):
                st.write(f"**Status:** {booking['status']}")
                st.write(f"**Time:** {booking['time']}")
                if booking['status'] == 'Success':
                    st.success("Booked!")

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
    # URL Helper Box at the top
    st.markdown("""
    <div class="url-helper">
        <h3>💡 Easy Way to Find Restaurants</h3>
        <p><strong>Can't find a restaurant by name?</strong> Just paste the Resy URL below!</p>
        <ol>
            <li>Go to <a href="https://resy.com" target="_blank">resy.com</a> and find your restaurant</li>
            <li>Copy the URL from your browser</li>
            <li>Paste it below to automatically extract the venue info</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # URL Input
    resy_url = st.text_input(
        "📋 Paste Resy URL Here (Optional but Recommended)",
        placeholder="https://resy.com/cities/san-francisco-ca/venues/izakaya-rintaro",
        help="Paste the full Resy URL to automatically fill in restaurant details"
    )

    if resy_url:
        slug, name = extract_venue_from_url(resy_url)
        if slug:
            # Extract location from URL
            location = "sf" if "san-francisco" in resy_url else "ny"
            if "los-angeles" in resy_url:
                location = "la"
            elif "washington-dc" in resy_url:
                location = "dc"

            with st.spinner("Looking up venue..."):
                venue_id = get_venue_id_from_slug(slug, location)

                if venue_id:
                    st.session_state.venue_id = venue_id
                    st.session_state.restaurant_name = name
                    st.success(f"✓ Found: {name} (Venue ID: {venue_id})")
                else:
                    st.warning("Could not look up venue ID automatically. Try entering it manually below.")

    st.divider()

    # Create tabs
    tab1, tab2 = st.tabs(["📅 Quick Book", "ℹ️ Help"])

    with tab1:
        st.subheader("Book a Reservation")

        col1, col2 = st.columns(2)

        with col1:
            # Pre-fill if we got it from URL
            restaurant_name = st.text_input(
                "Restaurant Name",
                value=st.session_state.restaurant_name or "",
                placeholder="e.g., Carbone, Don Angie, Izakaya Rintaro",
                help="Enter the restaurant name"
            )

            venue_id_input = st.text_input(
                "Venue ID",
                value=str(st.session_state.venue_id) if st.session_state.venue_id else "",
                placeholder="Required - paste Resy URL above to auto-fill",
                help="Venue ID is required. Use the URL box above to find it easily!"
            )

            location = st.selectbox(
                "Location",
                ["sf", "ny", "la", "dc", "boston", "austin", "miami", "chicago"],
                help="City where the restaurant is located"
            )

            party_size = st.number_input(
                "Party Size",
                min_value=1,
                max_value=20,
                value=2,
                help="Number of people"
            )

        with col2:
            reservation_date = st.date_input(
                "Reservation Date",
                min_value=date.today(),
                value=date.today() + timedelta(days=7),
                help="Date for your reservation"
            )

            # Time selection
            st.write("Preferred Times (select multiple)")
            time_cols = st.columns(4)

            times = [
                "17:00", "17:30", "18:00", "18:30",
                "19:00", "19:30", "20:00", "20:30",
                "21:00", "21:30", "22:00", "22:30"
            ]

            selected_times = []
            for i, time_slot in enumerate(times):
                col_idx = i % 4
                with time_cols[col_idx]:
                    hour = int(time_slot.split(":")[0])
                    minute = time_slot.split(":")[1]
                    display_time = f"{hour if hour <= 12 else hour-12}:{minute} {'PM' if hour >= 12 else 'AM'}"

                    if st.checkbox(display_time, key=f"time_{time_slot}"):
                        selected_times.append(time_slot)

            auto_accept = st.checkbox(
                "Accept any available time",
                help="If enabled, will book any available time if preferred times are full"
            )

        st.divider()

        # Action buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Check Availability", type="secondary", use_container_width=True):
                if not venue_id_input:
                    st.error("⚠️ Venue ID is required! Paste a Resy URL above to get it automatically.")
                elif not selected_times and not auto_accept:
                    st.error("Please select at least one preferred time or enable 'Accept any available time'")
                else:
                    with st.spinner("Checking availability..."):
                        slots = check_availability(venue_id_input, party_size, reservation_date)

                        if slots:
                            st.success(f"Found {len(slots)} available time(s)!")
                            st.write("**Available Times:**")
                            for slot in slots:
                                st.write(f"- {slot['display_time']} ({slot['type']})")
                        else:
                            st.warning("No availability found for selected date/times")

        with col2:
            if st.button("📅 Book Now", type="primary", use_container_width=True):
                if not venue_id_input:
                    st.error("⚠️ Venue ID is required! Paste a Resy URL above to get it automatically.")
                elif not selected_times and not auto_accept:
                    st.error("Please select at least one preferred time or enable 'Accept any available time'")
                else:
                    with st.spinner("Booking reservation..."):
                        config = ReservationConfig(
                            restaurant_name=restaurant_name or "Restaurant",
                            party_size=party_size,
                            reservation_date=reservation_date,
                            preferred_times=selected_times,
                            location=location,
                            auto_accept_any_time=auto_accept
                        )
                        config.venue_id = int(venue_id_input)

                        confirmation = st.session_state.bot.attempt_booking(config)

                        if confirmation:
                            st.balloons()
                            st.markdown(f"""
                            <div class="success-box">
                                <h3>🎉 Reservation Booked Successfully!</h3>
                                <p><strong>Restaurant:</strong> {restaurant_name}</p>
                                <p><strong>Date:</strong> {reservation_date}</p>
                                <p><strong>Party Size:</strong> {party_size}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            st.session_state.booking_history.append({
                                'restaurant': restaurant_name,
                                'date': str(reservation_date),
                                'time': datetime.now().strftime("%H:%M:%S"),
                                'status': 'Success'
                            })
                        else:
                            st.markdown("""
                            <div class="error-box">
                                <h3>❌ Could Not Book Reservation</h3>
                                <p>Possible reasons:</p>
                                <ul>
                                    <li>No availability at preferred times</li>
                                    <li>Someone else booked it first</li>
                                    <li>Try different times or enable 'Accept any available time'</li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)

                            st.session_state.booking_history.append({
                                'restaurant': restaurant_name,
                                'date': str(reservation_date),
                                'time': datetime.now().strftime("%H:%M:%S"),
                                'status': 'Failed'
                            })

    with tab2:
        st.subheader("How to Use")

        st.markdown("""
        ### 🎯 Easiest Way to Book

        1. **Go to Resy.com** and search for your restaurant
        2. **Copy the URL** from your browser's address bar
           - Example: `https://resy.com/cities/san-francisco-ca/venues/izakaya-rintaro`
        3. **Paste the URL** in the box at the top of this page
        4. The restaurant name and venue ID will be automatically filled in!
        5. Select your date, times, and click **Book Now**

        ### 📋 Example URLs

        Here are examples of Resy URLs (you can find these on resy.com):
        - San Francisco: `https://resy.com/cities/san-francisco-ca/venues/izakaya-rintaro`
        - New York: `https://resy.com/cities/new-york-ny/venues/carbone`
        - Los Angeles: `https://resy.com/cities/los-angeles-ca/venues/gjelina`

        ### 💡 Tips for Success

        - **Use the URL method** - It's the most reliable way to find restaurants
        - **Multiple Times**: Select several preferred times to increase your chances
        - **Auto-Accept**: Enable this for very popular restaurants
        - **Known Venue IDs**: Check the sidebar for quick reference

        ### ⏰ Time Format Reference

        | 12-Hour | 24-Hour | | 12-Hour | 24-Hour |
        |---------|---------|---|---------|---------|
        | 5:00 PM | 17:00   | | 8:00 PM | 20:00   |
        | 6:00 PM | 18:00   | | 9:00 PM | 21:00   |
        | 7:00 PM | 19:00   | | 10:00 PM | 22:00   |
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Made with ❤️ for food lovers | "
    "For personal use only</div>",
    unsafe_allow_html=True
)
