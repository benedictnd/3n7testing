package models

import (
    "time"

    "gorm.io/gorm"
)

type User struct {
    gorm.Model
    Email        string `gorm:"unique;not null"`
    Password     string `gorm:"not null"`
    Name         string `gorm:"not null"`
    Role         string `gorm:"not null"` // athlete, coach, stakeholder, support
    TrainingSessions []TrainingSession
    Attendances      []Attendance
    Feedbacks        []Feedback
}

type TrainingSession struct {
    gorm.Model
    Type            string    `gorm:"not null"` // core or endurance
    Date            time.Time `gorm:"not null"`
    StartTime       time.Time `gorm:"not null"`
    EndTime         time.Time `gorm:"not null"`
    CoachID         uint      `gorm:"not null"`
    Coach           User      `gorm:"foreignKey:CoachID"`
    WarmingUp       WarmingUp
    MainTraining    MainTraining
    CoolingDown     CoolingDown
    Attendances     []Attendance
    Feedbacks       []Feedback
    TrainingQuality int       // 1-5 rating
    Expectations    int       // 1-5 rating
    TeamCondition   int       // 1-5 rating
    Notes           string
    Documentation   string    // File path or URL
}

type WarmingUp struct {
    gorm.Model
    TrainingSessionID uint `gorm:"not null"`
    Notes            string
    Duration        int    // in minutes
}

type MainTraining struct {
    gorm.Model
    TrainingSessionID  uint `gorm:"not null"`
    Notes             string
    Duration         int    // in minutes
    PerformanceRecords []PerformanceRecord
}

type CoolingDown struct {
    gorm.Model
    TrainingSessionID uint `gorm:"not null"`
    Notes            string
    Duration        int    // in minutes
}

type PerformanceRecord struct {
    gorm.Model
    MainTrainingID uint   `gorm:"not null"`
    AthleteID      uint   `gorm:"not null"`
    Athlete        User   `gorm:"foreignKey:AthleteID"`
    Time           string // Duration or time achieved
    Repetitions    int
    Sets           int
    Weight         float64 // in kg
    Notes          string
}

type Attendance struct {
    gorm.Model
    TrainingSessionID uint      `gorm:"not null"`
    AthleteID        uint      `gorm:"not null"`
    Athlete          User      `gorm:"foreignKey:AthleteID"`
    CheckInTime      time.Time `gorm:"not null"`
}

type Feedback struct {
    gorm.Model
    TrainingSessionID uint   `gorm:"not null"`
    AthleteID        uint   `gorm:"not null"`
    Athlete          User   `gorm:"foreignKey:AthleteID"`
    TrainingQuality  int    // 1-5 rating
    Expectations     int    // 1-5 rating
    BodyCondition    int    // 1-10 rating
    Intensity        int    // 1-10 rating
    Notes           string
} 