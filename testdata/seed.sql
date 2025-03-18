-- Insert test users
INSERT INTO users (email, password, name, role, created_at, updated_at)
VALUES 
    ('coach1@test.com', '$2a$10$1234567890123456789012', 'John Coach', 'coach', NOW(), NOW()),
    ('coach2@test.com', '$2a$10$1234567890123456789012', 'Sarah Coach', 'coach', NOW(), NOW()),
    ('athlete1@test.com', '$2a$10$1234567890123456789012', 'Mike Athlete', 'athlete', NOW(), NOW()),
    ('athlete2@test.com', '$2a$10$1234567890123456789012', 'Lisa Athlete', 'athlete', NOW(), NOW()),
    ('athlete3@test.com', '$2a$10$1234567890123456789012', 'Tom Athlete', 'athlete', NOW(), NOW()),
    ('support1@test.com', '$2a$10$1234567890123456789012', 'Support Staff', 'support', NOW(), NOW()),
    ('stakeholder1@test.com', '$2a$10$1234567890123456789012', 'Stakeholder One', 'stakeholder', NOW(), NOW());

-- Insert test training sessions
INSERT INTO training_sessions (type, date, start_time, end_time, coach_id, training_quality, expectations, team_condition, notes, documentation, created_at, updated_at)
VALUES 
    ('core', '2024-03-15', '2024-03-15 09:00:00', '2024-03-15 10:30:00', 1, 4, 4, 5, 'Great core training session', '/uploads/sessions/2024-03-15-core-training.pdf', NOW(), NOW()),
    ('endurance', '2024-03-16', '2024-03-16 15:00:00', '2024-03-16 16:30:00', 2, 5, 4, 4, 'Intense endurance training', '/uploads/sessions/2024-03-16-endurance-training.pdf', NOW(), NOW()),
    ('core', '2024-03-17', '2024-03-17 10:00:00', '2024-03-17 11:30:00', 1, 3, 4, 4, 'Focus on technique', '/uploads/sessions/2024-03-17-core-training.pdf', NOW(), NOW());

-- Insert warming up sessions
INSERT INTO warming_ups (training_session_id, notes, duration, created_at, updated_at)
VALUES 
    (1, 'Light stretching and mobility exercises', 15, NOW(), NOW()),
    (2, 'Dynamic warm-up and light cardio', 20, NOW(), NOW()),
    (3, 'Joint mobility and activation exercises', 15, NOW(), NOW());

-- Insert main training sessions
INSERT INTO main_trainings (training_session_id, notes, duration, created_at, updated_at)
VALUES 
    (1, 'Core strength and stability exercises', 60, NOW(), NOW()),
    (2, 'High-intensity interval training', 45, NOW(), NOW()),
    (3, 'Technical drills and core exercises', 60, NOW(), NOW());

-- Insert cooling down sessions
INSERT INTO cooling_downs (training_session_id, notes, duration, created_at, updated_at)
VALUES 
    (1, 'Static stretching and breathing exercises', 15, NOW(), NOW()),
    (2, 'Light jogging and stretching', 15, NOW(), NOW()),
    (3, 'Mobility work and stretching', 15, NOW(), NOW());

-- Insert performance records (for endurance session)
INSERT INTO performance_records (main_training_id, athlete_id, time, repetitions, sets, weight, notes, created_at, updated_at)
VALUES 
    (2, 3, '00:45:00', 12, 3, 65.5, 'Good form maintained throughout all sets', NOW(), NOW()),
    (2, 4, '00:42:30', 15, 3, 55.0, 'Improved speed and maintained form', NOW(), NOW()),
    (2, 5, '00:44:15', 10, 3, 70.0, 'Strong performance, increased weight from last session', NOW(), NOW());

-- Insert attendance records with proper time validation
INSERT INTO attendances (training_session_id, athlete_id, check_in_time, created_at, updated_at)
VALUES 
    (1, 3, '2024-03-15 10:35:00', NOW(), NOW()), -- After session end
    (1, 4, '2024-03-15 10:35:00', NOW(), NOW()), -- After session end
    (2, 3, '2024-03-16 16:35:00', NOW(), NOW()), -- After session end
    (2, 4, '2024-03-16 16:35:00', NOW(), NOW()), -- After session end
    (2, 5, '2024-03-16 16:35:00', NOW(), NOW()), -- After session end
    (3, 4, '2024-03-17 11:35:00', NOW(), NOW()), -- After session end
    (3, 5, '2024-03-17 11:35:00', NOW(), NOW()); -- After session end

-- Insert feedback
INSERT INTO feedbacks (training_session_id, athlete_id, training_quality, expectations, body_condition, intensity, notes, created_at, updated_at)
VALUES 
    (1, 3, 4, 4, 8, 7, 'Great session, felt challenging but manageable', NOW(), NOW()),
    (1, 4, 5, 4, 7, 8, 'Really enjoyed the core exercises', NOW(), NOW()),
    (2, 3, 5, 5, 6, 9, 'Very intense but effective training', NOW(), NOW()),
    (2, 4, 4, 4, 7, 9, 'Challenging endurance session', NOW(), NOW()),
    (2, 5, 5, 4, 8, 8, 'Good balance of exercises', NOW(), NOW()),
    (3, 4, 4, 4, 8, 7, 'Technical focus was helpful', NOW(), NOW()),
    (3, 5, 3, 4, 7, 6, 'Would like more variety in exercises', NOW(), NOW()); 