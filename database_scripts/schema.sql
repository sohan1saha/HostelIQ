-- HostelIQ Relational Schema (SQL)
-- SDG 6: Clean Water and Sanitation | SDG 12: Responsible Consumption and Production

-- 1. Rooms Table
CREATE TABLE IF NOT EXISTS rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    block VARCHAR(10) NOT NULL,
    floor INTEGER NOT NULL,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    capacity INTEGER DEFAULT 2
);

-- 2. Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    room_id INTEGER,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE SET NULL
);

-- 3. Maintenance Staff Table
CREATE TABLE IF NOT EXISTS maintenance_staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(50) NOT NULL, -- Plumbing (SDG 6), Electrical (SDG 12), Sanitation
    contact_no VARCHAR(15) NOT NULL
);

-- 4. Water Consumption Logs (SDG 6 Monitoring)
CREATE TABLE IF NOT EXISTS water_consumption (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    log_date DATE NOT NULL,
    water_used_liters REAL NOT NULL,
    leak_flag INTEGER DEFAULT 0, -- 1 if unusual flow detected
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
);

-- 5. Electricity Consumption Logs (SDG 12 Monitoring)
CREATE TABLE IF NOT EXISTS electricity_consumption (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    log_date DATE NOT NULL,
    kwh_consumed REAL NOT NULL,
    peak_usage_flag INTEGER DEFAULT 0,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
);

-- 6. Trigger: Enforce Maximum Room Capacity
CREATE TRIGGER IF NOT EXISTS trg_enforce_room_capacity
BEFORE INSERT ON students
FOR EACH ROW
WHEN NEW.room_id IS NOT NULL
BEGIN
    SELECT CASE
        WHEN (SELECT COUNT(*) FROM students WHERE room_id = NEW.room_id) >= (SELECT capacity FROM rooms WHERE room_id = NEW.room_id)
        THEN RAISE(ABORT, 'Room has reached maximum resident capacity.')
    END;
END;
