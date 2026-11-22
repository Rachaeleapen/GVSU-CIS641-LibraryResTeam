import streamlit as st
import sys
import os
import datetime

# Point Python to the parent folder for backend files
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Importing functions
from room_service import (
    get_rooms,
    get_time_slots,
    get_booking_start_times,
    get_available_start_times,
    reserve_room,
    cancel_reservation,
    get_user_reservations,
    get_or_create_google_user
)


st.set_page_config(page_title="Library Rooms", page_icon="", layout="wide")
# -------------------------------------------------
# GOOGLE AUTHENTICATION
# -------------------------------------------------

if not st.user.is_logged_in:

    st.title("Library Room Reservation System")
    st.write("Sign in with your Google account to continue.")

    st.button(
        "Continue with Google",
        on_click=st.login,
        use_container_width=True
    )

    st.stop()


google_user = st.user

if not getattr(google_user, "email_verified", False):
    st.error("Your Google account email must be verified.")
    st.stop()

try:
    current_user = get_or_create_google_user(
        google_sub=google_user.sub,
        email=google_user.email,
        full_name=google_user.name
    )

    current_user_id = current_user[0]
    current_user_name = current_user[1]
    current_user_email = current_user[2]
    current_user_role = current_user[3]

except Exception as e:
    st.error(f"Unable to load your account: {e}")
    st.stop()


st.title("Library Room Reservation System")

col1, col2 = st.columns([4, 1])

with col1:
    st.write(f"Welcome, **{current_user_name}**!")
    st.caption(f"{current_user_email} | Role: {current_user_role}")

with col2:
    if st.button("Log Out", use_container_width=True):
        st.logout()

st.markdown(
    "Reserve a quiet space for individual study or group collaboration."
)

st.divider()

try:
    rooms = get_rooms()
    time_slots = get_time_slots()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# Added the third tab here
tab1, tab2, tab3 = st.tabs([
    "Book a Room",
    "View Reservations",
    "Reservation History"
])


with tab1:
    st.subheader("New Reservation")
    st.info("Select a room, date, duration, and available start time.")

    if not rooms:
        st.warning("There are currently no rooms available.")

    else:
        from datetime import datetime as dt, timedelta

        # Room options
        room_options = {
            f"{name} (Capacity: {capacity})": room_id
            for room_id, name, capacity in rooms
        }

        col1, col2 = st.columns(2)

        with col1:
            reservation_date = st.date_input(
                "Select Date",
                min_value=datetime.date.today()
            )

            selected_room_name = st.selectbox(
                "Select a Room",
                options=list(room_options.keys())
            )

        with col2:
            duration_hours = st.selectbox(
                "Reservation Duration",
                options=[1, 2, 3],
                format_func=lambda hours: f"{hours} hour(s)"
            )

        # Get the selected room's database ID.
        room_id = room_options[selected_room_name]

        # Find start times that do not overlap existing reservations.
        available_start_times = get_available_start_times(
            room_id,
            reservation_date,
            duration_hours
        )

        st.markdown("---")

        if not available_start_times:
            st.warning(
                "There are no available start times for this room, "
                "date, and duration. Try another room, date, or duration."
            )

        else:
            selected_start_time = st.selectbox(
                "Select a Start Time",
                options=available_start_times,
                format_func=lambda start: start.strftime("%I:%M %p")
            )

            end_time = (
                dt.combine(reservation_date, selected_start_time)
                + timedelta(hours=duration_hours)
            ).time()

            st.write(
                f"**Your reservation:** "
                f"{selected_start_time.strftime('%I:%M %p')} - "
                f"{end_time.strftime('%I:%M %p')}"
            )

            if st.button("Reserve Room", use_container_width=True):
                result = reserve_room(
                    current_user_id,
                    room_id,
                    reservation_date,
                    selected_start_time,
                    duration_hours
                )

                if result.startswith("Reservation successful!"):
                    st.success(result)
                    st.balloons()
                else:
                    st.error(result)



# -------------------------------------------------
# VIEW ACTIVE RESERVATIONS
# -------------------------------------------------

with tab2:
    st.subheader("My Active Reservations")
    st.info("These are your current confirmed reservations.")

    try:
        reservations = get_user_reservations(
            current_user_id,
            "confirmed"
        )
    except Exception as e:
        st.error(f"Unable to load your reservations: {e}")
        reservations = []

    # Remove a pending cancellation if that reservation
    # is no longer in the active reservation list.
    active_reservation_ids = {res[0] for res in reservations}
    pending_cancel_id = st.session_state.get("pending_cancel_id")

    if pending_cancel_id not in active_reservation_ids:
        st.session_state.pop("pending_cancel_id", None)

    if not reservations:
        st.write("You do not have any active reservations.")

    else:
        for res_id, room, start, end, booking_date, status, cancelled_at in reservations:

            with st.container(border=True):
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"**{room}**")
                    st.write(f"Reservation ID: {res_id}")
                    st.write(f"Date: {booking_date.strftime('%B %d, %Y')}")
                    st.write(
                        f"Time: {start.strftime('%I:%M %p')} - "
                        f"{end.strftime('%I:%M %p')}"
                    )

                with col2:
                    if st.button(
                        "Cancel",
                        key=f"cancel_{res_id}",
                        use_container_width=True
                    ):
                        st.session_state["pending_cancel_id"] = res_id
                        st.rerun()

                # Second confirmation before cancelling.
                if st.session_state.get("pending_cancel_id") == res_id:
                    st.warning(
                        f"Are you sure you want to cancel your "
                        f"reservation for {room} on "
                        f"{booking_date.strftime('%B %d, %Y')}?"
                    )

                    confirm_col, keep_col = st.columns(2)

                    with confirm_col:
                        if st.button(
                            "Confirm Cancellation",
                            key=f"confirm_cancel_{res_id}",
                            type="primary",
                            use_container_width=True
                        ):
                            result = cancel_reservation(
                                res_id,
                                current_user_id
                            )

                            st.session_state.pop("pending_cancel_id", None)

                            if "successfully" in result.lower():
                                st.success(result)
                            else:
                                st.error(result)

                            st.rerun()

                    with keep_col:
                        if st.button(
                            "Keep Reservation",
                            key=f"keep_reservation_{res_id}",
                            use_container_width=True
                        ):
                            st.session_state.pop("pending_cancel_id", None)
                            st.rerun()


# -------------------------------------------------
# RESERVATION HISTORY
# -------------------------------------------------

with tab3:
    st.subheader("My Reservation History")
    st.info("These are your previously cancelled reservations.")

    try:
        cancelled_reservations = get_user_reservations(
            current_user_id,
            "cancelled"
        )
    except Exception as e:
        st.error(f"Unable to load your reservation history: {e}")
        cancelled_reservations = []

    if not cancelled_reservations:
        st.write("You do not have any cancelled reservations.")

    else:
        for res_id, room, start, end, booking_date, status, cancelled_at in cancelled_reservations:

            with st.container(border=True):
                st.markdown(f"**{room}**")
                st.write(f"Reservation ID: {res_id}")
                st.write(f"Date: {booking_date.strftime('%B %d, %Y')}")
                st.write(
                    f"Time: {start.strftime('%I:%M %p')} - "
                    f"{end.strftime('%I:%M %p')}"
                )
                st.write("Status: Cancelled")

                if cancelled_at:
                    st.caption(
                        f"Cancelled on: "
                        f"{cancelled_at.strftime('%B %d, %Y at %I:%M %p')}"
                    )
