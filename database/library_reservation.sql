
-- =====================================================
-- Library Room Reservation System
-- PostgreSQL Database
-- =====================================================

-- 1. USERS TABLE
-- Stores students, staff, and administrators.

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student'
        CHECK (role IN ('student', 'staff', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 2. ROOMS TABLE
-- Stores information about each reservable room.

CREATE TABLE rooms (
    room_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    room_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(150) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT
);


-- 3. TIME SLOTS TABLE
-- Stores predefined booking times.
-- Example: 09:00-10:00, 10:00-11:00.

CREATE TABLE time_slots (
    slot_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,

    CHECK (start_time < end_time),
    UNIQUE (start_time, end_time),

    -- Allows PostgreSQL to detect overlapping time slots.
    slot_period TSRANGE GENERATED ALWAYS AS (
        tsrange(
            DATE '2000-01-01' + start_time,
            DATE '2000-01-01' + end_time,
            '[)'
        )
    ) STORED,

    EXCLUDE USING GIST (slot_period WITH &&)
);


-- 4. RESERVATIONS TABLE
-- Connects users, rooms, dates, and time slots.

CREATE TABLE reservations (
    reservation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(user_id) ON DELETE RESTRICT,

    room_id BIGINT NOT NULL
        REFERENCES rooms(room_id) ON DELETE RESTRICT,

    slot_id BIGINT NOT NULL
        REFERENCES time_slots(slot_id) ON DELETE RESTRICT,

    reservation_date DATE NOT NULL,
    party_size INTEGER NOT NULL DEFAULT 1
        CHECK (party_size > 0),

    status VARCHAR(20) NOT NULL DEFAULT 'confirmed'
        CHECK (status IN ('confirmed', 'cancelled')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMPTZ,

    -- Keep cancellation information consistent.
    CHECK (
        (status = 'confirmed' AND cancelled_at IS NULL)
        OR
        (status = 'cancelled' AND cancelled_at IS NOT NULL)
    )
);


-- 5. PREVENT DOUBLE-BOOKING
-- A room can have only one confirmed reservation
-- for a given date and time slot.
-- Cancelled reservations do not block new bookings.

CREATE UNIQUE INDEX one_confirmed_booking_per_room_slot
    ON reservations (room_id, reservation_date, slot_id)
    WHERE status = 'confirmed';


-- 6. INDEXES
-- Help common reservation searches run efficiently.

CREATE INDEX reservations_by_user_date
    ON reservations (user_id, reservation_date);

CREATE INDEX reservations_by_date_status
    ON reservations (reservation_date, status);


-- =====================================================
-- SAMPLE DATA
-- =====================================================

-- USERS
-- Placeholder hashes only; these are not real passwords.
-- Generate actual password hashes in your Python app.

INSERT INTO users (full_name, email, password_hash, role)
VALUES
    ('Alex Student', 'alex@example.edu',
     'REPLACE_WITH_HASH', 'student'),

    ('Jordan Student', 'jordan@example.edu',
     'REPLACE_WITH_HASH', 'student'),

    ('Taylor Staff', 'taylor@example.edu',
     'REPLACE_WITH_HASH', 'staff'),

    ('Morgan Admin', 'morgan@example.edu',
     'REPLACE_WITH_HASH', 'admin');


-- ROOMS

INSERT INTO rooms (room_name, location, capacity, description)
VALUES
    ('Study Room A', 'Library - First Floor', 4,
     'Small room for individual or group study'),

    ('Study Room B', 'Library - First Floor', 6,
     'Medium group study room'),

    ('Study Room C', 'Library - Second Floor', 10,
     'Large room for group study');


-- TIME SLOTS

INSERT INTO time_slots (start_time, end_time)
VALUES
    ('09:00', '10:00'),
    ('10:00', '11:00'),
    ('11:00', '12:00'),
    ('12:00', '13:00'),
    ('13:00', '14:00'),
    ('14:00', '15:00'),
    ('15:00', '16:00'),
    ('16:00', '17:00');


-- SAMPLE RESERVATIONS
-- The date is tomorrow, so the examples remain useful
-- whenever you initially run this script.

INSERT INTO reservations
    (user_id, room_id, slot_id, reservation_date, party_size)
SELECT
    u.user_id,
    r.room_id,
    t.slot_id,
    CURRENT_DATE + 1,
    3
FROM users u
JOIN rooms r ON r.room_name = 'Study Room A'
JOIN time_slots t ON t.start_time = '09:00'
WHERE u.email = 'alex@example.edu';


INSERT INTO reservations
    (user_id, room_id, slot_id, reservation_date, party_size)
SELECT
    u.user_id,
    r.room_id,
    t.slot_id,
    CURRENT_DATE + 1,
    5
FROM users u
JOIN rooms r ON r.room_name = 'Study Room B'
JOIN time_slots t ON t.start_time = '10:00'
WHERE u.email = 'jordan@example.edu';

