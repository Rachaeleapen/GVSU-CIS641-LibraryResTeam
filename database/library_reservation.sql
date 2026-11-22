
-- =====================================================
-- Library Room Reservation System
-- PostgreSQL Database
-- =====================================================

-- Required for preventing overlapping reservations.
CREATE EXTENSION IF NOT EXISTS btree_gist;


-- =====================================================
-- 1. USERS TABLE
-- =====================================================

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT,
    google_sub TEXT,
    role VARCHAR(20) NOT NULL DEFAULT 'student'
        CHECK (role IN ('student', 'staff', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Each Google account can only be linked to one user.
CREATE UNIQUE INDEX users_google_sub_unique
    ON users (google_sub)
    WHERE google_sub IS NOT NULL;


-- =====================================================
-- 2. ROOMS TABLE
-- =====================================================

CREATE TABLE rooms (
    room_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    room_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(150) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT
);


-- =====================================================
-- 3. TIME SLOTS TABLE
-- Kept for compatibility with predefined time slots.
-- New reservations use start_time and end_time directly.
-- =====================================================

CREATE TABLE time_slots (
    slot_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,

    CHECK (start_time < end_time),
    CHECK (
        EXTRACT(EPOCH FROM (end_time - start_time)) IN (3600, 7200, 10800)
    ),
    UNIQUE (start_time, end_time),

    slot_period TSRANGE GENERATED ALWAYS AS (
        tsrange(
            DATE '2000-01-01' + start_time,
            DATE '2000-01-01' + end_time,
            '[)'
        )
    ) STORED,

    EXCLUDE USING GIST (slot_period WITH &&)
);


-- =====================================================
-- 4. RESERVATIONS TABLE
-- Reservations can now last 1, 2, or 3 hours.
-- =====================================================

CREATE TABLE reservations (
    reservation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(user_id) ON DELETE RESTRICT,

    room_id BIGINT NOT NULL
        REFERENCES rooms(room_id) ON DELETE RESTRICT,

    -- Nullable because reservations no longer require a predefined slot.
    slot_id BIGINT
        REFERENCES time_slots(slot_id) ON DELETE RESTRICT,

    reservation_date DATE NOT NULL,

    start_time TIME NOT NULL,
    end_time TIME NOT NULL,

    party_size INTEGER NOT NULL DEFAULT 1
        CHECK (party_size > 0),

    status VARCHAR(20) NOT NULL DEFAULT 'confirmed'
        CHECK (status IN ('confirmed', 'cancelled')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMPTZ,

    CHECK (start_time < end_time),

    -- Library hours are 9 AM to 5 PM.
    CHECK (
        start_time >= TIME '09:00'
        AND end_time <= TIME '17:00'
    ),

    -- Keep cancellation information consistent.
    CHECK (
        (status = 'confirmed' AND cancelled_at IS NULL)
        OR
        (status = 'cancelled' AND cancelled_at IS NOT NULL)
    )
);


-- =====================================================
-- 5. PREVENT OVERLAPPING CONFIRMED RESERVATIONS
-- A room cannot have overlapping confirmed reservations
-- on the same date.
-- Cancelled reservations do not block new bookings.
-- =====================================================

ALTER TABLE reservations
ADD CONSTRAINT no_overlapping_confirmed_room_reservations
EXCLUDE USING GIST (
    room_id WITH =,
    reservation_date WITH =,
    tsrange(
        reservation_date + start_time,
        reservation_date + end_time,
        '[)'
    ) WITH &&
)
WHERE (status = 'confirmed');


-- =====================================================
-- 6. INDEXES
-- =====================================================

CREATE INDEX reservations_by_user_date
    ON reservations (user_id, reservation_date);

CREATE INDEX reservations_by_date_status
    ON reservations (reservation_date, status);


-- =====================================================
-- SAMPLE DATA
-- =====================================================

-- USERS
-- Placeholder hashes are not real passwords.
-- Google users can have a NULL password_hash.

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
-- These examples use tomorrow's date.

-- Alex reserves Study Room A from 9 AM to 10 AM.

INSERT INTO reservations (
    user_id,
    room_id,
    slot_id,
    reservation_date,
    start_time,
    end_time,
    party_size
)
SELECT
    u.user_id,
    r.room_id,
    t.slot_id,
    CURRENT_DATE + 1,
    '09:00',
    '10:00',
    3
FROM users u
JOIN rooms r ON r.room_name = 'Study Room A'
JOIN time_slots t ON t.start_time = '09:00'
WHERE u.email = 'alex@example.edu';


-- Jordan reserves Study Room B from 10 AM to 11 AM.

INSERT INTO reservations (
    user_id,
    room_id,
    slot_id,
    reservation_date,
    start_time,
    end_time,
    party_size
)
SELECT
    u.user_id,
    r.room_id,
    t.slot_id,
    CURRENT_DATE + 1,
    '10:00',
    '11:00',
    5
FROM users u
JOIN rooms r ON r.room_name = 'Study Room B'
JOIN time_slots t ON t.start_time = '10:00'
WHERE u.email = 'jordan@example.edu';


-- =====================================================
-- END OF DATABASE SETUP
-- =====================================================
