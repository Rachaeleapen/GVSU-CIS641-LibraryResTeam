import streamlit as st
import sys
import os
import datetime

# Point Python to the parent folder for backend files
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from room_service import get_rooms, get_time_slots, reserve_room, cancel_reservation

# Configure the page settings
st.set_page_config(page_title="Library Rooms", page_icon="", layout="wide")

# Header Section
st.title("GVSU Library Room Reservation System")
st.markdown("Reserve a quiet space for individual study or group collaboration.")
st.divider()

# Fetch data 
try:
    rooms = get_rooms()
    time_slots = get_time_slots()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# Main App Tabs
tab1, tab2 = st.tabs(["Book a Room", "Cancel a Reservation"])

with tab1:
    st.subheader("New Reservation")
    st.info("Select your preferred room, date, and time slot below.")
    
    with st.form("reservation_form", border=True):
        # Create 2 side-by-side columns for a tighter layout
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.number_input("User ID", min_value=1, step=1, help="Enter your student or staff ID number.")
            reservation_date = st.date_input("Select Date", min_value=datetime.date.today())
            
        with col2:
            room_options = {name: room_id for room_id, name in rooms}
            selected_room_name = st.selectbox("Select a Room", options=list(room_options.keys()))
            
            slot_options = {f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}": slot_id 
                            for slot_id, start, end in time_slots}
            selected_slot_time = st.selectbox("Select a Time Slot", options=list(slot_options.keys()))
        
        st.markdown("<br>", unsafe_allow_html=True) # Adds a little breathing room
        submit_button = st.form_submit_button("Reserve Room", use_container_width=True)
        
        if submit_button:
            room_id = room_options[selected_room_name]
            slot_id = slot_options[selected_slot_time]
            
            result = reserve_room(user_id, room_id, slot_id, reservation_date)
            
            if "successful" in result.lower():
                st.success(f"**Success!** {result}")
                st.balloons() # Adds a nice visual flourish
            else:
                st.error(f"**Action Failed:** {result}")

with tab2:
    st.subheader("Cancel Reservation")
    st.warning("Cancellations are permanent and cannot be undone.")
    
    with st.form("cancel_form", border=True):
        res_id_to_cancel = st.number_input("Reservation ID", min_value=1, step=1)
        cancel_user_id = st.number_input("Confirm Your User ID", min_value=1, step=1)
        
        cancel_button = st.form_submit_button("Cancel Reservation", use_container_width=True)
        
        if cancel_button:
            cancel_result = cancel_reservation(res_id_to_cancel, cancel_user_id)
            
            if "successfully" in cancel_result.lower():
                st.success(f"**Cancelled:** {cancel_result}")
            else:
                st.error(f"**Notice:** {cancel_result}")