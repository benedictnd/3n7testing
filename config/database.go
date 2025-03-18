package config

import (
    "fmt"
    "os"

    "github.com/3and7/training-platform/models"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
)

var DB *gorm.DB

func InitDB() error {
    dbHost := os.Getenv("DB_HOST")
    dbUser := os.Getenv("DB_USER")
    dbPassword := os.Getenv("DB_PASSWORD")
    dbName := os.Getenv("DB_NAME")
    dbPort := os.Getenv("DB_PORT")

    if dbHost == "" {
        dbHost = "localhost"
    }
    if dbPort == "" {
        dbPort = "5432"
    }

    dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable",
        dbHost, dbUser, dbPassword, dbName, dbPort)

    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        return fmt.Errorf("failed to connect to database: %v", err)
    }

    DB = db

    // Auto Migrate the schemas
    err = DB.AutoMigrate(
        &models.User{},
        &models.TrainingSession{},
        &models.WarmingUp{},
        &models.MainTraining{},
        &models.CoolingDown{},
        &models.Feedback{},
        &models.Attendance{},
        &models.PerformanceRecord{},
    )
    if err != nil {
        return fmt.Errorf("failed to migrate database: %v", err)
    }

    return nil
} 