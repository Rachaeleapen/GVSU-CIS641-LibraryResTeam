import streamlit as st
import sys
import os
import datetime

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from room_service import get_rooms, get_time_slots, reserve_room, cancel_reservation

st.set_page_config(page_title="Library Room Reservation", layout="centered")
st.title("Library Room Reservation System")

try:
    rooms = get_rooms()
    time_slots = get_time_slots()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

tab1, tab2 = st.tabs(["Make a Reservation", "Cancel a Reservation"])

with tab1:
    st.header("Book a Room")
    
    with st.form("reservation_form"):
        user_id = st.number_input("User ID", min_value=1, step=1)
        
        room_options = {name: room_id for room_id, name in rooms}
        selected_room_name = st.selectbox("Select a Room", options=list(room_options.keys()))
        
        slot_options = {f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}": slot_id 
                        for slot_id, start, end in time_slots}
        selected_slot_time = st.selectbox("Select a Time Slot", options=list(slot_options.keys()))
        
        reservation_date = st.date_input("Select Date", min_value=datetime.date.today())
        
        submit_button = st.form_submit_button("Reserve Room")
        
        if submit_button:
            room_id = room_options[selected_room_name]
            slot_id = slot_options[selected_slot_time]
            
            result = reserve_room(user_id, room_id, slot_id, reservation_date)
            
            if "successful" in result.lower():
                st.success(result)
            else:
                st.error(result)

with tab2:
    st.header("Cancel an Existing Reservation")
    
    with st.form("cancel_form"):
        res_id_to_cancel = st.number_input("Reservation ID", min_value=1, step=1)
        cancel_user_id = st.number_input("Confirm Your User ID", min_value=1, step=1)
        
        cancel_button = st.form_submit_button("Cancel Reservation")
        
        if cancel_button:
            cancel_result = cancel_reservation(res_id_to_cancel, cancel_user_id)
            
            if "successfully" in cancel_result.lower():
                st.success(cancel_result)
            else:
                st.warning(cancel_result)
                