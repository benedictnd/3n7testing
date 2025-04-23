# Database Schema Documentation

This document outlines the database schema for the 3&7 Training Platform.

## Entity Relationship Diagram

```
┌─────────────┐     ┌───────────────────┐     ┌──────────────┐
│    User     │     │  TrainingSession  │     │  WarmingUp   │
├─────────────┤     ├───────────────────┤     ├──────────────┤
│ id          │     │ id                │     │ id           │
│ email       │     │ type              │     │ training_session_id
│ password    │     │ date              │     │ notes        │
│ name        │     │ start_time        │     │ duration     │
│ role        │     │ end_time          │     │ created_at   │
│ created_at  │     │ coach_id          │     │ updated_at   │
│ updated_at  │     │ training_quality  │     └──────────────┘
└─────────────┘     │ expectations      │
      ▲ │           │ team_condition    │     ┌──────────────┐
      │ │           │ notes             │     │ MainTraining │
      │ │           │ documentation     │     ├──────────────┤
      │ │           │ created_at        │     │ id           │
      │ │           │ updated_at        │     │ training_session_id
      │ │           └───────────────────┘     │ notes        │
      │ │                   ▲ │                │ duration     │
      │ │                   │ │                │ created_at   │
      │ │                   │ │                │ updated_at   │
      │ │                   │ │                └──────────────┘
      │ │                   │ │                      │ ▲
      │ │                   │ │                      │ │
      │ │                   │ │                      ▼ │
      │ │                   │ │               ┌──────────────┐
      │ │                   │ │               │PerformanceRecord
      │ │                   │ │               ├──────────────┤
      │ │                   │ │               │ id           │
      │ │                   │ │               │ main_training_id
      │ │                   │ │               │ athlete_id   │
      │ │                   │ │               │ time         │
      │ │                   │ │               │ repetitions  │
      │ │                   │ │               │ sets         │
      │ │                   │ │               │ weight       │
      │ │                   │ │               │ notes        │
      │ │                   │ │               │ created_at   │
      │ │                   │ │               │ updated_at   │
      │ │                   │ │               └──────────────┘
      │ │                   │ │
      │ │                   │ │               ┌──────────────┐
      │ │                   │ │               │ CoolingDown  │
      │ │                   │ ▼               ├──────────────┤
      │ │           ┌───────────────┐         │ id           │
      │ │           │   Attendance  │         │ training_session_id
      │ │           ├───────────────┤         │ notes        │
      │ │           │ id            │         │ duration     │
      │ │           │ training_session_id     │ created_at   │
      │ │           │ athlete_id    │         │ updated_at   │
      │ │           │ check_in_time │         └──────────────┘
      │ │           │ created_at    │
      │ │           │ updated_at    │
      │ │           └───────────────┘
      │ │                   ▲ │
      │ │                   │ │
      │ │                   │ │
      │ │                   │ │
      │ │                   │ │
      │ ▼           ┌───────────────┐
┌─────────────┐     │    Feedback   │
│ Notification│     ├───────────────┤
├─────────────┤     │ id            │
│ id          │     │ training_session_id
│ title       │     │ athlete_id    │
│ message     │     │ training_quality
│ type        │     │ expectations  │
│ recipient_id│     │ body_condition│
│ sender_id   │     │ intensity     │
│ related_id  │     │ notes         │
│ link        │     │ created_at    │
│ is_read     │     │ updated_at    │
│ created_at  │     └───────────────┘
└─────────────┘
      ▲ │
      │ │
      │ ▼
┌─────────────────────────┐
│ IndependentTrainingSession
├─────────────────────────┤
│ id                      │
│ athlete_id              │
│ title                   │
│ description             │
│ date                    │
│ duration                │
│ intensity               │
│ notes                   │
│ created_at              │
│ updated_at              │
└─────────────────────────┘
```

## Tables

### User

Represents users of the system, who can be athletes, coaches, or administrators.

| Column     | Type      | Description                           |
|------------|-----------|---------------------------------------|
| id         | Integer   | Primary key                           |
| email      | String    | User's email address (unique)         |
| password   | String    | Hashed password                       |
| name       | String    | User's full name                      |
| role       | String    | User role (admin, coach, athlete)     |
| created_at | DateTime  | Timestamp of creation                 |
| updated_at | DateTime  | Timestamp of last update              |

### TrainingSession

Represents scheduled training sessions led by coaches.

| Column           | Type      | Description                           |
|------------------|-----------|---------------------------------------|
| id               | Integer   | Primary key                           |
| type             | String    | Type of training session              |
| date             | Date      | Date of the session                   |
| start_time       | DateTime  | Start time of the session             |
| end_time         | DateTime  | End time of the session               |
| coach_id         | Integer   | Foreign key to User (coach)           |
| training_quality | Integer   | Rating of training quality (1-10)     |
| expectations     | Integer   | Rating of expectations met (1-10)     |
| team_condition   | Integer   | Rating of team condition (1-10)       |
| notes            | Text      | General notes about the session       |
| documentation    | Text      | Detailed documentation                |
| created_at       | DateTime  | Timestamp of creation                 |
| updated_at       | DateTime  | Timestamp of last update              |

### WarmingUp

Represents the warming up phase of a training session.

| Column             | Type      | Description                           |
|--------------------|-----------|---------------------------------------|
| id                 | Integer   | Primary key                           |
| training_session_id| Integer   | Foreign key to TrainingSession        |
| notes              | Text      | Notes about the warming up activities |
| duration           | Integer   | Duration in minutes                   |
| created_at         | DateTime  | Timestamp of creation                 |
| updated_at         | DateTime  | Timestamp of last update              |

### MainTraining

Represents the main phase of a training session.

| Column             | Type      | Description                           |
|--------------------|-----------|---------------------------------------|
| id                 | Integer   | Primary key                           |
| training_session_id| Integer   | Foreign key to TrainingSession        |
| notes              | Text      | Notes about the main training activities |
| duration           | Integer   | Duration in minutes                   |
| created_at         | DateTime  | Timestamp of creation                 |
| updated_at         | DateTime  | Timestamp of last update              |

### CoolingDown

Represents the cooling down phase of a training session.

| Column             | Type      | Description                           |
|--------------------|-----------|---------------------------------------|
| id                 | Integer   | Primary key                           |
| training_session_id| Integer   | Foreign key to TrainingSession        |
| notes              | Text      | Notes about the cooling down activities |
| duration           | Integer   | Duration in minutes                   |
| created_at         | DateTime  | Timestamp of creation                 |
| updated_at         | DateTime  | Timestamp of last update              |

### PerformanceRecord

Records performance metrics for athletes during main training.

| Column           | Type      | Description                           |
|------------------|-----------|---------------------------------------|
| id               | Integer   | Primary key                           |
| main_training_id | Integer   | Foreign key to MainTraining           |
| athlete_id       | Integer   | Foreign key to User (athlete)         |
| time             | Time      | Time measurement (optional)           |
| repetitions      | Integer   | Number of repetitions (optional)      |
| sets             | Integer   | Number of sets (optional)             |
| weight           | Float     | Weight used in kg (optional)          |
| notes            | Text      | Additional notes (optional)           |
| created_at       | DateTime  | Timestamp of creation                 |
| updated_at       | DateTime  | Timestamp of last update              |

### Attendance

Records attendance of athletes at training sessions.

| Column             | Type      | Description                           |
|--------------------|-----------|---------------------------------------|
| id                 | Integer   | Primary key                           |
| training_session_id| Integer   | Foreign key to TrainingSession        |
| athlete_id         | Integer   | Foreign key to User (athlete)         |
| check_in_time      | DateTime  | Time when attendance was marked       |
| created_at         | DateTime  | Timestamp of creation                 |
| updated_at         | DateTime  | Timestamp of last update              |

### Feedback

Records feedback from athletes about training sessions.

| Column             | Type      | Description                           |
|--------------------|-----------|---------------------------------------|
| id                 | Integer   | Primary key                           |
| training_session_id| Integer   | Foreign key to TrainingSession        |
| athlete_id         | Integer   | Foreign key to User (athlete)         |
| training_quality   | Integer   | Rating of training quality (1-10)     |
| expectations       | Integer   | Rating of expectations met (1-10)     |
| body_condition     | Integer   | Rating of body condition (1-10)       |
| intensity          | Integer   | Rating of intensity (1-10)            |
| notes              | Text      | Additional feedback notes (optional)  |
| created_at         | DateTime  | Timestamp of creation                 |
| updated_at         | DateTime  | Timestamp of last update              |

### Notification

System notifications for users.

| Column       | Type      | Description                           |
|--------------|-----------|---------------------------------------|
| id           | Integer   | Primary key                           |
| title        | String    | Notification title                    |
| message      | Text      | Notification message content          |
| notification_type | String | Type of notification                |
| recipient_id | Integer   | Foreign key to User (recipient)       |
| sender_id    | Integer   | Foreign key to User (sender)          |
| related_id   | Integer   | ID of related entity (optional)       |
| link         | Text      | URL link (optional)                   |
| is_read      | Boolean   | Whether notification has been read    |
| created_at   | DateTime  | Timestamp of creation                 |

### IndependentTrainingSession

Represents self-directed training sessions by athletes.

| Column        | Type      | Description                           |
|---------------|-----------|---------------------------------------|
| id            | Integer   | Primary key                           |
| athlete_id    | Integer   | Foreign key to User (athlete)         |
| title         | String    | Title of the training session         |
| description   | String    | Description of the session (optional) |
| date          | Date      | Date of the session                   |
| duration      | Integer   | Duration in minutes                   |
| intensity     | Integer   | Intensity rating (1-10) (optional)    |
| notes         | String    | Additional notes (optional)           |
| created_at    | DateTime  | Timestamp of creation                 |
| updated_at    | DateTime  | Timestamp of last update              |

## Relationships

- A **User** (coach) can have many **TrainingSession**s
- A **User** (athlete) can have many **Attendance** records
- A **User** (athlete) can have many **Feedback** records
- A **User** (athlete) can have many **IndependentTrainingSession**s
- A **User** can receive many **Notification**s
- A **User** can send many **Notification**s
- A **TrainingSession** belongs to one **User** (coach)
- A **TrainingSession** can have many **WarmingUp**s
- A **TrainingSession** can have many **MainTraining**s
- A **TrainingSession** can have many **CoolingDown**s
- A **TrainingSession** can have many **Attendance** records
- A **TrainingSession** can have many **Feedback** records
- A **MainTraining** belongs to one **TrainingSession**
- A **MainTraining** can have many **PerformanceRecord**s
- A **PerformanceRecord** belongs to one **MainTraining**
- A **PerformanceRecord** belongs to one **User** (athlete)
- An **Attendance** belongs to one **TrainingSession**
- An **Attendance** belongs to one **User** (athlete)
- A **Feedback** belongs to one **TrainingSession**
- A **Feedback** belongs to one **User** (athlete)
- A **Notification** can be received by one **User**
- A **Notification** can be sent by one **User**
- An **IndependentTrainingSession** belongs to one **User** (athlete) 