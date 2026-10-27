from db_connection import get_connection
def get_rooms():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT room_id, room_name FROM rooms"
            )
            return cur.fetchall()


def get_time_slots():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT slot_id, start_time, end_time FROM time_slots"
            )
            return cur.fetchall()

def reserve_room(user_id, room_id, slot_id, date):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO reservations
                    (user_id, room_id, slot_id, reservation_date)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, room_id, slot_id, date))

        return "Reservation successful!"

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
