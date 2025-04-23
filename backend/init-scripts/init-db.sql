-- Create database if it doesn't exist
-- CREATE DATABASE appdb;

-- Connect to the database
-- \c appdb;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create training_sessions table
CREATE TABLE IF NOT EXISTS training_sessions (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    coach_id INTEGER REFERENCES users(id),
    training_quality INTEGER,
    expectations INTEGER,
    team_condition INTEGER,
    notes TEXT,
    documentation TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create warming_ups table
CREATE TABLE IF NOT EXISTS warming_ups (
    id SERIAL PRIMARY KEY,
    training_session_id INTEGER REFERENCES training_sessions(id),
    notes TEXT,
    duration INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create main_trainings table
CREATE TABLE IF NOT EXISTS main_trainings (
    id SERIAL PRIMARY KEY,
    training_session_id INTEGER REFERENCES training_sessions(id),
    notes TEXT,
    duration INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create cooling_downs table
CREATE TABLE IF NOT EXISTS cooling_downs (
    id SERIAL PRIMARY KEY,
    training_session_id INTEGER REFERENCES training_sessions(id),
    notes TEXT,
    duration INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create performance_records table
CREATE TABLE IF NOT EXISTS performance_records (
    id SERIAL PRIMARY KEY,
    main_training_id INTEGER REFERENCES main_trainings(id),
    athlete_id INTEGER REFERENCES users(id),
    time TIME,
    repetitions INTEGER,
    sets INTEGER,
    weight FLOAT,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create attendances table
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    training_session_id INTEGER REFERENCES training_sessions(id),
    athlete_id INTEGER REFERENCES users(id),
    check_in_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create feedbacks table
CREATE TABLE IF NOT EXISTS feedbacks (
    id SERIAL PRIMARY KEY,
    training_session_id INTEGER REFERENCES training_sessions(id),
    athlete_id INTEGER REFERENCES users(id),
    training_quality INTEGER,
    expectations INTEGER,
    body_condition INTEGER,
    intensity INTEGER,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create notifications table for the notification system
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    recipient_id INTEGER REFERENCES users(id),
    sender_id INTEGER REFERENCES users(id),
    related_id INTEGER,
    link TEXT,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Insert sample data for users
INSERT INTO users (email, password, name, role, created_at, updated_at)
VALUES 
('coach@example.com', '$2b$12$1234567890123456789012uQSxnLYDIGgQe.XW3Ut.7t8oCxnK2UG', 'John Doe', 'coach', NOW(), NOW()),
('athlete1@example.com', '$2b$12$1234567890123456789012uQSxnLYDIGgQe.XW3Ut.7t8oCxnK2UG', 'Alice Smith', 'athlete', NOW(), NOW()),
('athlete2@example.com', '$2b$12$1234567890123456789012uQSxnLYDIGgQe.XW3Ut.7t8oCxnK2UG', 'Bob Johnson', 'athlete', NOW(), NOW());

-- Insert sample data for training_sessions
INSERT INTO training_sessions (type, date, start_time, end_time, coach_id, training_quality, expectations, team_condition, notes, documentation, created_at, updated_at)
VALUES 
('Regular', '2025-04-20', '2025-04-20 10:00:00', '2025-04-20 12:00:00', 1, 8, 7, 9, 'Great session', 'Detailed documentation here', NOW(), NOW()),
('Recovery', '2025-04-22', '2025-04-22 14:00:00', '2025-04-22 15:30:00', 1, 6, 7, 5, 'Recovery session', 'Focus on recovery', NOW(), NOW());

-- Insert sample data for warming_ups
INSERT INTO warming_ups (training_session_id, notes, duration, created_at, updated_at)
VALUES 
(1, 'Dynamic stretching', 15, NOW(), NOW()),
(2, 'Light jogging', 10, NOW(), NOW());

-- Insert sample data for main_trainings
INSERT INTO main_trainings (training_session_id, notes, duration, created_at, updated_at)
VALUES 
(1, 'Strength and conditioning', 90, NOW(), NOW()),
(2, 'Mobility work', 60, NOW(), NOW());

-- Insert sample data for cooling_downs
INSERT INTO cooling_downs (training_session_id, notes, duration, created_at, updated_at)
VALUES 
(1, 'Static stretching', 15, NOW(), NOW()),
(2, 'Light yoga', 20, NOW(), NOW());

-- Insert sample data for performance_records
INSERT INTO performance_records (main_training_id, athlete_id, time, repetitions, sets, weight, notes, created_at, updated_at)
VALUES 
(1, 2, '00:02:30', 10, 3, 70.5, 'Good form', NOW(), NOW()),
(1, 3, '00:02:45', 8, 3, 80.0, 'Could improve technique', NOW(), NOW()),
(2, 2, NULL, 15, 2, NULL, 'Better flexibility', NOW(), NOW());

-- Insert sample data for attendances
INSERT INTO attendances (training_session_id, athlete_id, check_in_time, created_at, updated_at)
VALUES 
(1, 2, '2025-04-20 09:50:00', NOW(), NOW()),
(1, 3, '2025-04-20 09:55:00', NOW(), NOW()),
(2, 2, '2025-04-22 13:55:00', NOW(), NOW());

-- Insert sample data for feedbacks
INSERT INTO feedbacks (training_session_id, athlete_id, training_quality, expectations, body_condition, intensity, notes, created_at, updated_at)
VALUES 
(1, 2, 9, 8, 7, 8, 'Felt great', NOW(), NOW()),
(1, 3, 7, 7, 6, 9, 'A bit difficult', NOW(), NOW()),
(2, 2, 8, 7, 8, 5, 'Good recovery session', NOW(), NOW());

-- Insert sample data for notifications
INSERT INTO notifications (title, message, notification_type, recipient_id, sender_id, related_id, link, is_read, created_at)
VALUES 
('New Training Session', 'You have a new training session scheduled', 'training', 2, 1, 1, '/training/1', FALSE, NOW()),
('Feedback Request', 'Please provide feedback for your recent training session', 'feedback', 3, 1, 1, '/feedback/1', FALSE, NOW()); 