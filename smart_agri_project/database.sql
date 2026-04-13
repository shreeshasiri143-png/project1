--------------------------------------------------
-- USERS TABLE (Login System)
--------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

--------------------------------------------------
-- SOIL DATA TABLE (ML Prediction Storage)
--------------------------------------------------

CREATE TABLE IF NOT EXISTS soil_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    temperature REAL,
    humidity REAL,
    moisture REAL,
    soil_type TEXT,
    crop_type TEXT,
    nitrogen INTEGER,
    potassium INTEGER,
    phosphorous INTEGER,
    fertilizer TEXT
);

--------------------------------------------------
-- SAMPLE USERS (OPTIONAL)
--------------------------------------------------

INSERT INTO users (username, password) VALUES
('admin', '1234'),
('farmer1', '1111');

--------------------------------------------------
-- SAMPLE SOIL DATA (OPTIONAL)
--------------------------------------------------

INSERT INTO soil_data
(temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous, fertilizer)
VALUES
(30, 60, 40, 'Loamy', 'Rice', 40, 30, 20, 'Urea'),
(28, 55, 35, 'Sandy', 'Wheat', 35, 25, 15, 'Compost');