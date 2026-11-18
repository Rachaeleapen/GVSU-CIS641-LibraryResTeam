from db_connection import get_connection
from psycopg.errors import UniqueViolation
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

def reserve_room(user_id, room_id, slot_id, date):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                # Check if the room is already reserved
                cur.execute("""
                    SELECT reservation_id
                    FROM reservations
                    WHERE room_id = %s
                    AND slot_id = %s
                    AND reservation_date = %s
                    AND status = 'confirmed'
                """, (room_id, slot_id, date))

                if cur.fetchone():
                    return "This room is already reserved for the selected date and time."

                # Create a new reservation
                cur.execute("""
                    INSERT INTO reservations
                    (user_id, room_id, slot_id, reservation_date, status)
                    VALUES (%s, %s, %s, %s, 'confirmed')
                """, (user_id, room_id, slot_id, date))

        return "Reservation successful!"

    except UniqueViolation:
        return "This room is already reserved for the selected date and time."

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


def get_all_reservations():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT r.reservation_id, rm.room_name, 
                           t.start_time, t.end_time, 
                           r.reservation_date, r.status
                    FROM reservations r
                    JOIN rooms rm ON r.room_id = rm.room_id
                    JOIN time_slots t ON r.slot_id = t.slot_id
                    ORDER BY r.reservation_date, t.start_time;
                """)
                return cur.fetchall()
    except Exception as e:
        return []
