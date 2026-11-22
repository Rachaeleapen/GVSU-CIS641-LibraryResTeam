from db_connection import get_connection
from datetime import date, datetime, time, timedelta
from psycopg.errors import UniqueViolation, ExclusionViolation

def get_rooms():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT room_id, room_name, capacity
                FROM rooms
                WHERE is_active = TRUE
                ORDER BY room_id
            """)
            return cur.fetchall()


def get_time_slots():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT slot_id, start_time, end_time
                FROM time_slots
                ORDER BY start_time
            """)
            return cur.fetchall()


def get_booking_start_times(duration_hours):
    """
    Return valid start times based on the requested duration.
    Library hours are 9 AM to 5 PM.
    """

    if duration_hours not in (1, 2, 3):
        raise ValueError("Duration must be 1, 2, or 3 hours.")

    opening_hour = 9
    closing_hour = 17

    latest_start_hour = closing_hour - duration_hours

    return [
        time(hour)
        for hour in range(opening_hour, latest_start_hour + 1)
    ]


def get_available_start_times(room_id, booking_date, duration_hours):
    # Get all possible start times for the selected duration.
    possible_start_times = get_booking_start_times(duration_hours)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT start_time, end_time
                FROM reservations
                WHERE room_id = %s
                  AND reservation_date = %s
                  AND status = 'confirmed'
            """, (room_id, booking_date))

            booked_times = cur.fetchall()

    available_times = []

    for start_time in possible_start_times:
        proposed_end_time = (
            datetime.combine(booking_date, start_time)
            + timedelta(hours=duration_hours)
        ).time()

        # Check whether the proposed reservation overlaps an existing one.
        has_conflict = any(
            start_time < booked_end and proposed_end_time > booked_start
            for booked_start, booked_end in booked_times
        )

        if not has_conflict:
            available_times.append(start_time)

    return available_times

def get_available_rooms(booking_date, slot_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.room_id, r.room_name, r.capacity
                FROM rooms r
                WHERE r.is_active = TRUE
                  AND NOT EXISTS (
                    SELECT 1
                    FROM reservations res
                    WHERE res.room_id = r.room_id
                      AND res.reservation_date = %s
                      AND res.slot_id = %s
                      AND res.status = 'confirmed'
                  )
                ORDER BY r.room_id
            """, (booking_date, slot_id))
            return cur.fetchall()


def reserve_room(user_id, room_id, booking_date, start_time, duration_hours):
    try:
        booking_date = date.fromisoformat(str(booking_date))

        if isinstance(start_time, str):
            start_time = time.fromisoformat(start_time)

        if duration_hours not in (1, 2, 3):
            return "Please select a duration of 1, 2, or 3 hours."

        if start_time.minute != 0 or start_time.second != 0:
            return "Start times must be on the hour."

        # Calculate the reservation end time.
        start_datetime = datetime.combine(booking_date, start_time)
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        end_time = end_datetime.time()

        # Enforce library hours: 9 AM to 5 PM.
        if start_time < time(9, 0) or end_time > time(17, 0):
            return "Reservations must be between 9:00 AM and 5:00 PM."

        # Prevent reservations in the past.
        if start_datetime <= datetime.now():
            return "Cannot book a past date or time."

        with get_connection() as conn:
            with conn.cursor() as cur:

                # Verify that the room exists and is active.
                cur.execute("""
                    SELECT room_id
                    FROM rooms
                    WHERE room_id = %s
                      AND is_active = TRUE
                """, (room_id,))

                if cur.fetchone() is None:
                    return "Room not found or unavailable."

                # Check for overlapping confirmed reservations.
                cur.execute("""
                    SELECT reservation_id
                    FROM reservations
                    WHERE room_id = %s
                      AND reservation_date = %s
                      AND status = 'confirmed'
                      AND start_time < %s
                      AND end_time > %s
                """, (
                    room_id,
                    booking_date,
                    end_time,
                    start_time
                ))

                if cur.fetchone():
                    return "Room is already booked during part of this time."

                # Insert the new reservation.
                cur.execute("""
                    INSERT INTO reservations (
                        user_id,
                        room_id,
                        reservation_date,
                        start_time,
                        end_time
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING reservation_id
                """, (
                    user_id,
                    room_id,
                    booking_date,
                    start_time,
                    end_time
                ))

                reservation_id = cur.fetchone()[0]

        return f"Reservation successful! ID: {reservation_id}"

    except ExclusionViolation:
        return "Room is already booked during part of this time."

    except UniqueViolation:
        return "Room is already booked during this time."

    except ValueError:
        return "Invalid date, time, or reservation duration."

    except Exception as e:
        return f"Reservation failed: {e}"


def cancel_reservation(reservation_id, user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE reservations
                    SET status = 'cancelled',
                        cancelled_at = CURRENT_TIMESTAMP
                    WHERE reservation_id = %s
                      AND user_id = %s
                      AND status = 'confirmed'
                """, (reservation_id, user_id))

                if cur.rowcount == 0:
                    return "Reservation not found or already cancelled"

        return "Reservation cancelled successfully!"

    except Exception as e:
        return f"Cancellation failed: {e}"



def get_user_reservations(user_id, status):
    """
    Return reservations belonging only to the specified user.
    Status must be either 'confirmed' or 'cancelled'.
    """

    if status not in ("confirmed", "cancelled"):
        raise ValueError("Invalid reservation status.")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    r.reservation_id,
                    rm.room_name,
                    r.start_time,
                    r.end_time,
                    r.reservation_date,
                    r.status,
                    r.cancelled_at
                FROM reservations r
                JOIN rooms rm ON r.room_id = rm.room_id
                WHERE r.user_id = %s
                  AND r.status = %s
                ORDER BY r.reservation_date, r.start_time
            """, (user_id, status))

            return cur.fetchall()


def get_or_create_google_user(google_sub, email, full_name):
    """
    Find an existing user by Google account ID or email.
    Create a new student account if no matching account exists.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            # 1. Check whether this Google account is already linked.
            cur.execute("""
                SELECT user_id, full_name, email, role
                FROM users
                WHERE google_sub = %s
            """, (google_sub,))

            user = cur.fetchone()

            if user:
                return user

            # 2. Check whether this email already has an account.
            cur.execute("""
                SELECT user_id, full_name, email, role, google_sub
                FROM users
                WHERE LOWER(email) = LOWER(%s)
            """, (email,))

            user = cur.fetchone()

            if user:
                user_id, name, user_email, role, existing_google_sub = user

                if existing_google_sub and existing_google_sub != google_sub:
                    raise ValueError(
                        "This email is already linked to another Google account."
                    )

                # Link Google to the existing database account.
                cur.execute("""
                    UPDATE users
                    SET google_sub = %s
                    WHERE user_id = %s
                """, (google_sub, user_id))

                return user_id, name, user_email, role

            # 3. Create a new account if no matching user exists.
            cur.execute("""
                INSERT INTO users
                    (full_name, email, google_sub, role)
                VALUES (%s, %s, %s, 'student')
                RETURNING user_id, full_name, email, role
            """, (full_name, email, google_sub))

            return cur.fetchone()
