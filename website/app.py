import streamlit as st
import sys
import os
import datetime
import calendar as month_calendar

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

    # Login page styling
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(
                135deg,
                #0032A0 0%,
                #001f66 100%
            );
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 100%;
            padding-top: 5rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff !important;
            border: 1px solid #ffffff !important;
            border-radius: 18px;
            padding: 2rem;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
        }

        /* White login card */
.st-key-login_card {
    background-color: #ffffff !important;
    border: 1px solid #ffffff !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25);
}

/* Keep the inside of the card white */
.st-key-login_card [data-testid="stVerticalBlock"] {
    background-color: #ffffff !important;
}

/* Card text */
.st-key-login_card .login-heading {
    color: #0032A0 !important;
}

.st-key-login_card .login-subtitle {
    color: #52606d !important;
}

.st-key-login_card .login-label {
    color: #0032A0 !important;
}

        .login-heading {
            color: #0032A0;
            font-size: 2rem;
            font-weight: 750;
            text-align: center;
            line-height: 1.2;
            margin-bottom: 0.75rem;
        }

        .login-subtitle {
            color: #52606d;
            text-align: center;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .login-label {
            color: #0032A0;
            text-align: center;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 1rem;
        }

        div.stButton > button {
            background-color: #0032A0;
            color: white;
            border: none;
            border-radius: 8px;
            min-height: 3rem;
            font-weight: 600;
            transition: background-color 0.2s ease;
        }

        div.stButton > button:hover {
            background-color: #002477;
            color: white;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Center the login card
    left, center, right = st.columns([1, 1.4, 1])

    with center:
        with st.container(border=True, key="login_card"):

            st.markdown(
                '<div class="login-label">GVSU LIBRARY</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="login-heading">'
                'Find your space.<br>Focus on what matters.'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="login-subtitle">'
                'Sign in to reserve your library study space.'
                '</div>',
                unsafe_allow_html=True
            )

            st.button(
                "Continue with Google",
                on_click=st.login,
                use_container_width=True
            )

    st.stop()



# -------------------------------------------------
# GET LOGGED-IN GOOGLE USER
# -------------------------------------------------

google_user = st.user

# Make sure the Google account email is verified.
if not getattr(google_user, "email_verified", False):
    st.error("Your Google account email must be verified.")
    st.stop()

# Create or retrieve the user in PostgreSQL.
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


# for the tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Book a Room",
    "View Reservations",
    "Reservation History",
    "Calendar"
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


# -------------------------------------------------
# RESERVATION CALENDAR
# -------------------------------------------------

with tab4:
    st.subheader("My Reservation Calendar")
    st.info("View your confirmed room reservations by month.")

    # Initialize the calendar to the current month.
    today = datetime.date.today()

    if "calendar_year" not in st.session_state:
        st.session_state.calendar_year = today.year
        st.session_state.calendar_month = today.month

    # Calendar navigation.
    nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])

    with nav_col1:
        if st.button("← Previous", use_container_width=True):
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1

            st.rerun()

    with nav_col2:
        month_name = datetime.date(
            st.session_state.calendar_year,
            st.session_state.calendar_month,
            1
        ).strftime("%B %Y")

        st.markdown(
            f"<h3 style='text-align: center;'>{month_name}</h3>",
            unsafe_allow_html=True
        )

    with nav_col3:
        if st.button("Next →", use_container_width=True):
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1

            st.rerun()

    # Return to the current month.
    if st.button("Today"):
        st.session_state.calendar_year = today.year
        st.session_state.calendar_month = today.month
        st.rerun()

    # Retrieve only this user's confirmed reservations.
    try:
        calendar_reservations = get_user_reservations(
            current_user_id,
            "confirmed"
        )
    except Exception as e:
        st.error(f"Unable to load calendar reservations: {e}")
        calendar_reservations = []

    # Organize reservations by date.
    reservations_by_date = {}

    for res_id, room, start, end, booking_date, status, cancelled_at in calendar_reservations:
        if (
            booking_date.year == st.session_state.calendar_year
            and booking_date.month == st.session_state.calendar_month
        ):
            reservations_by_date.setdefault(booking_date.day, []).append(
                (res_id, room, start, end)
            )

    # Weekday headings.
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]

    weekday_columns = st.columns(7)

    for column, weekday in zip(weekday_columns, weekdays):
        with column:
            st.markdown(f"**{weekday[:3]}**")

    # Generate the monthly calendar.
    month_weeks = month_calendar.monthcalendar(
        st.session_state.calendar_year,
        st.session_state.calendar_month
    )

    for week in month_weeks:
        day_columns = st.columns(7)

        for column, day in zip(day_columns, week):
            with column:
                with st.container(border=True):
                    if day == 0:
                        st.write(" ")
                    else:
                        # Highlight today's date.
                        if (
                            day == today.day
                            and st.session_state.calendar_month == today.month
                            and st.session_state.calendar_year == today.year
                        ):
                            st.markdown(f"**:blue[{day} · Today]**")
                        else:
                            st.markdown(f"**{day}**")

                        # Display reservations on this date.
                        day_reservations = reservations_by_date.get(day, [])

                        for res_id, room, start, end in day_reservations:
                            st.markdown(
                                f"**{room}**"
                            )

                            st.caption(
                                f"{start.strftime('%I:%M %p')} - "
                                f"{end.strftime('%I:%M %p')}"
                            )

                            st.caption(f"ID: {res_id}")

    if not calendar_reservations:
        st.write("You don't have any confirmed reservations yet.")
