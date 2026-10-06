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

-- Seed Data Insertion
INSERT OR IGNORE INTO rooms (room_id, block, floor, room_number, capacity) VALUES
(1, 'Block-A', 1, 'A-101', 2),
(2, 'Block-A', 1, 'A-102', 2),
(3, 'Block-A', 2, 'A-201', 2),
(4, 'Block-B', 1, 'B-101', 2),
(5, 'Block-B', 2, 'B-201', 3);

INSERT OR IGNORE INTO students (student_id, name, email, room_id) VALUES
('STU2025001', 'Aarav Sharma', 'aarav.sharma@sitpune.edu.in', 1),
('STU2025002', 'Riya Patel', 'riya.patel@sitpune.edu.in', 1),
('STU2025003', 'Rohan Verma', 'rohan.verma@sitpune.edu.in', 2),
('STU2025004', 'Ananya Gupta', 'ananya.gupta@sitpune.edu.in', 3),
('STU2025005', 'Siddharth Nair', 'siddharth.nair@sitpune.edu.in', 4);

INSERT OR IGNORE INTO maintenance_staff (staff_id, name, specialization, contact_no) VALUES
(101, 'Rajesh Kumar', 'Plumbing (SDG 6)', '+919876543210'),
(102, 'Suresh Yadav', 'Electrical (SDG 12)', '+919876543211'),
(103, 'Amit Shinde', 'Sanitation', '+919876543212');

INSERT OR IGNORE INTO water_consumption (log_id, room_id, log_date, water_used_liters, leak_flag) VALUES
(1, 1, '2026-10-01', 180.5, 0),
(2, 1, '2026-10-02', 450.0, 1), -- Potential leak
(3, 2, '2026-10-01', 150.0, 0),
(4, 3, '2026-10-01', 220.0, 0),
(5, 4, '2026-10-01', 510.0, 1), -- High consumption
(6, 5, '2026-10-01', 140.0, 0);

INSERT OR IGNORE INTO electricity_consumption (log_id, room_id, log_date, kwh_consumed, peak_usage_flag) VALUES
(1, 1, '2026-10-01', 12.5, 0),
(2, 1, '2026-10-02', 28.0, 1), -- High usage
(3, 2, '2026-10-01', 10.0, 0),
(4, 3, '2026-10-01', 35.5, 1),
(5, 4, '2026-10-01', 11.2, 0),
(6, 5, '2026-10-01', 9.8, 0);
