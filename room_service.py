from db_connection import get_connection
from datetime import date, datetime
from psycopg.errors import UniqueViolation
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

def reserve_room(user_id, room_id, slot_id, booking_date):
    try:
        booking_date = date.fromisoformat(str(booking_date))

        if booking_date < date.today():
            return "Cannot book a past date."
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT start_time
                    FROM time_slots
                    WHERE slot_id = %s
                """, (slot_id,))

                slot = cur.fetchone()

                if slot is None:
                    return "Invalid time slot."

                # Prevent booking a time that has already started
                start_datetime = datetime.combine(
                    booking_date, slot[0]
                )

                if start_datetime <= datetime.now():
                    return "Cannot book a past time."

    
                cur.execute("""
                    SELECT room_id
                    FROM rooms
                    WHERE room_id = %s
                      AND is_active = TRUE
                """, (room_id,))

                if cur.fetchone() is None:
                    return "Room not found or unavailable."

                cur.execute("""
                    SELECT reservation_id
                    FROM reservations
                    WHERE room_id = %s
                      AND slot_id = %s
                      AND reservation_date = %s
                      AND status = 'confirmed'
                """, (room_id, slot_id, booking_date))

                if cur.fetchone():
                    return "Room is already booked for this time."

                cur.execute("""
                    INSERT INTO reservations
                    (user_id, room_id, slot_id, reservation_date)
                    VALUES (%s, %s, %s, %s)
                    RETURNING reservation_id
                """, (user_id, room_id, slot_id, booking_date))

        reservation_id = cur.fetchone()[0]

        return f"Reservation successful! ID: {reservation_id}"

    except UniqueViolation:
        return "Room is already booked for this time."

    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."

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

