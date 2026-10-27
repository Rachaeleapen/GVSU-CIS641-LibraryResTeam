
from datetime import date, timedelta
from db_connection import get_connection
from room_service import (
    get_rooms,
    get_time_slots,
    reserve_room,
    cancel_reservation
)

# Test 1: Display rooms
print("ROOMS:", get_rooms())

# Test 2: Display time slots
print("TIME SLOTS:", get_time_slots())

# Find a real sample user, room, and slot
with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT user_id FROM users WHERE email = %s",
            ("alex@example.edu",)
        )
        user = cur.fetchone()

rooms = get_rooms()
slots = get_time_slots()

if user is None or not rooms or not slots:
    raise RuntimeError("Missing sample users, rooms, or time slots")

user_id = user[0]
room_id = rooms[0][0]
slot_id = slots[0][0]
booking_date = date.today() + timedelta(days=7)

# Test 3: Reserve room
print("\nRESERVATION:")
print(reserve_room(user_id, room_id, slot_id, booking_date))

# Find the reservation we just created
with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT reservation_id
            FROM reservations
            WHERE user_id = %s
              AND room_id = %s
              AND slot_id = %s
              AND reservation_date = %s
              AND status = 'confirmed'
            ORDER BY reservation_id DESC
            LIMIT 1
        """, (user_id, room_id, slot_id, booking_date))

        reservation = cur.fetchone()

# Test 4: Cancel reservation
if reservation:
    print("\nCANCELLATION:")
    print(cancel_reservation(reservation[0], user_id))
else:
    print("No confirmed reservation found")
