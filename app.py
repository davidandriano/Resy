"""
Resy Reservation Bot - Streamlit Web UI
"""
import streamlit as st
from datetime import date, datetime, timedelta
from bot import ResyBot
from config import ReservationConfig, load_settings
from resy_client import ResyClient
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'bot' not in st.session_state:
    st.session_state.bot = None
if 'booking_history' not in st.session_state:
    st.session_state.booking_history = []

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

def search_restaurant(restaurant_name, location):
    """Search for a restaurant and return venue ID"""
    if not st.session_state.authenticated:
        return None, "Please authenticate first"

    try:
        client = st.session_state.bot.client
        venues = client.search_venue(restaurant_name, location)

        if not venues:
            # Try direct venue lookup if search fails
            return None, f"Could not find '{restaurant_name}'. Try entering the Venue ID directly."

        venue = venues[0]
        venue_id = venue.get("id", {}).get("resy")
        venue_name = venue.get("name")

        return venue_id, f"Found: {venue_name} (ID: {venue_id})"
    except Exception as e:
        return None, f"Search error: {str(e)}"

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
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📅 Quick Book", "🔍 Search Restaurant", "ℹ️ Help"])

    with tab1:
        st.subheader("Book a Reservation")

        col1, col2 = st.columns(2)

        with col1:
            restaurant_name = st.text_input(
                "Restaurant Name",
                placeholder="e.g., Carbone, Don Angie, Izakaya Rintaro",
                help="Enter the restaurant name or use 'Search Restaurant' tab to find it"
            )

            venue_id_input = st.text_input(
                "Venue ID (optional)",
                placeholder="Leave empty to search by name",
                help="If you know the venue ID, enter it here to skip the search"
            )

            location = st.selectbox(
                "Location",
                ["ny", "sf", "la", "dc", "boston", "austin", "miami", "chicago"],
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
                    # Convert to 12-hour format for display
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
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔍 Check Availability", type="secondary"):
                if not restaurant_name and not venue_id_input:
                    st.error("Please enter a restaurant name or venue ID")
                elif not selected_times and not auto_accept:
                    st.error("Please select at least one preferred time or enable 'Accept any available time'")
                else:
                    with st.spinner("Checking availability..."):
                        # Get venue ID
                        if venue_id_input:
                            venue_id = venue_id_input
                        else:
                            venue_id, message = search_restaurant(restaurant_name, location)
                            if not venue_id:
                                st.error(message)
                                st.stop()
                            else:
                                st.info(message)

                        # Check availability
                        slots = check_availability(venue_id, party_size, reservation_date)

                        if slots:
                            st.success(f"Found {len(slots)} available time(s)!")

                            # Display available times
                            st.write("**Available Times:**")
                            for slot in slots:
                                st.write(f"- {slot['display_time']} ({slot['type']})")
                        else:
                            st.warning("No availability found for selected date/times")

        with col2:
            if st.button("📅 Book Now", type="primary"):
                if not restaurant_name and not venue_id_input:
                    st.error("Please enter a restaurant name or venue ID")
                elif not selected_times and not auto_accept:
                    st.error("Please select at least one preferred time or enable 'Accept any available time'")
                else:
                    with st.spinner("Booking reservation..."):
                        # Get venue ID
                        if venue_id_input:
                            venue_id = int(venue_id_input)
                        else:
                            venue_id, message = search_restaurant(restaurant_name, location)
                            if not venue_id:
                                st.error(message)
                                st.stop()

                        # Create reservation config
                        config = ReservationConfig(
                            restaurant_name=restaurant_name,
                            party_size=party_size,
                            reservation_date=reservation_date,
                            preferred_times=selected_times,
                            location=location,
                            auto_accept_any_time=auto_accept
                        )
                        config.venue_id = venue_id

                        # Attempt booking
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

                            # Add to history
                            st.session_state.booking_history.append({
                                'restaurant': restaurant_name,
                                'date': str(reservation_date),
                                'time': datetime.now().strftime("%H:%M:%S"),
                                'status': 'Success'
                            })
                        else:
                            st.markdown(f"""
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

                            # Add to history
                            st.session_state.booking_history.append({
                                'restaurant': restaurant_name,
                                'date': str(reservation_date),
                                'time': datetime.now().strftime("%H:%M:%S"),
                                'status': 'Failed'
                            })

        with col3:
            if st.button("🔄 Monitor", help="Continuously check until available"):
                st.info("Monitor mode coming soon! For now, use the command line script.")

    with tab2:
        st.subheader("Search for a Restaurant")

        search_name = st.text_input("Restaurant Name", key="search_input")
        search_location = st.selectbox(
            "Location",
            ["ny", "sf", "la", "dc", "boston", "austin", "miami", "chicago"],
            key="search_location"
        )

        if st.button("Search", type="primary"):
            if search_name:
                with st.spinner("Searching..."):
                    venue_id, message = search_restaurant(search_name, search_location)

                    if venue_id:
                        st.success(message)
                        st.code(f"Venue ID: {venue_id}", language="text")
                        st.info("Copy this Venue ID and use it in the 'Quick Book' tab for faster booking!")
                    else:
                        st.error(message)
                        st.info("💡 Tip: Try finding the restaurant on resy.com and look for the venue ID in the URL")
            else:
                st.warning("Please enter a restaurant name")

    with tab3:
        st.subheader("How to Use")

        st.markdown("""
        ### Quick Start Guide

        1. **Quick Book Tab**
           - Enter the restaurant name and details
           - Select your preferred times
           - Click "Check Availability" to see what's open
           - Click "Book Now" to make the reservation

        2. **Search Restaurant Tab**
           - Find the venue ID for a restaurant
           - Use this ID for faster future bookings

        ### Tips for Success

        - **Multiple Times**: Select several preferred times to increase your chances
        - **Venue ID**: If you know the venue ID, enter it directly to skip the search
        - **Auto-Accept**: Enable this for very popular restaurants when any time works
        - **Early Bird**: For midnight releases, run the monitor script from command line

        ### Time Format Reference

        | 12-Hour | 24-Hour | | 12-Hour | 24-Hour |
        |---------|---------|---|---------|---------|
        | 5:00 PM | 17:00   | | 8:00 PM | 20:00   |
        | 5:30 PM | 17:30   | | 8:30 PM | 20:30   |
        | 6:00 PM | 18:00   | | 9:00 PM | 21:00   |
        | 6:30 PM | 18:30   | | 9:30 PM | 21:30   |
        | 7:00 PM | 19:00   | | 10:00 PM | 22:00   |
        | 7:30 PM | 19:30   | | 10:30 PM | 22:30   |

        ### Need Help?

        - Make sure your `.env` file has your Resy credentials
        - Ensure you have a payment method saved on your Resy account
        - Check the sidebar for connection status
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Made with ❤️ for food lovers | "
    "For personal use only</div>",
    unsafe_allow_html=True
)
