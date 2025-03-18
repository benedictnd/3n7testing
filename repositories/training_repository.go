package repositories

import (
	"time"

	"github.com/3and7/training-platform/models"
	"gorm.io/gorm"
)

// TrainingRepository defines the interface for training data operations
type TrainingRepository interface {
	CreateTrainingSession(session *models.TrainingSession) error
	GetTrainingSessionByID(id uint) (*models.TrainingSession, error)
	GetTrainingSessions(limit, offset int) ([]models.TrainingSession, error)
	GetTrainingSessionsByCoach(coachID uint, limit, offset int) ([]models.TrainingSession, error)
	GetTrainingSessionsByDate(date time.Time) ([]models.TrainingSession, error)
	MarkAttendance(attendance *models.Attendance) error
	SubmitFeedback(feedback *models.Feedback) error
	GetAttendanceBySession(sessionID uint) ([]models.Attendance, error)
	GetFeedbackBySession(sessionID uint) ([]models.Feedback, error)
}

// GormTrainingRepository implements TrainingRepository with GORM
type GormTrainingRepository struct {
	db *gorm.DB
}

// NewTrainingRepository creates a new instance of GormTrainingRepository
func NewTrainingRepository(db *gorm.DB) TrainingRepository {
	return &GormTrainingRepository{
		db: db,
	}
}

// CreateTrainingSession creates a new training session
func (r *GormTrainingRepository) CreateTrainingSession(session *models.TrainingSession) error {
	tx := r.db.Begin()

	if err := tx.Create(session).Error; err != nil {
		tx.Rollback()
		return err
	}

	if err := tx.Create(&session.WarmingUp).Error; err != nil {
		tx.Rollback()
		return err
	}

	if err := tx.Create(&session.MainTraining).Error; err != nil {
		tx.Rollback()
		return err
	}

	// Create performance records if any
	for i := range session.MainTraining.PerformanceRecords {
		session.MainTraining.PerformanceRecords[i].MainTrainingID = session.MainTraining.ID
		if err := tx.Create(&session.MainTraining.PerformanceRecords[i]).Error; err != nil {
			tx.Rollback()
			return err
		}
	}

	if err := tx.Create(&session.CoolingDown).Error; err != nil {
		tx.Rollback()
		return err
	}

	return tx.Commit().Error
}

// GetTrainingSessionByID retrieves a training session by its ID
func (r *GormTrainingRepository) GetTrainingSessionByID(id uint) (*models.TrainingSession, error) {
	var session models.TrainingSession
	if err := r.db.Preload("WarmingUp").
		Preload("MainTraining").
		Preload("MainTraining.PerformanceRecords").
		Preload("CoolingDown").
		Preload("Attendances").
		Preload("Attendances.Athlete").
		Preload("Feedbacks").
		Preload("Feedbacks.Athlete").
		Preload("Coach").
		First(&session, id).Error; err != nil {
		return nil, err
	}
	return &session, nil
}

// GetTrainingSessions retrieves all training sessions with pagination
func (r *GormTrainingRepository) GetTrainingSessions(limit, offset int) ([]models.TrainingSession, error) {
	var sessions []models.TrainingSession
	if err := r.db.Preload("WarmingUp").
		Preload("MainTraining").
		Preload("Coach").
		Limit(limit).
		Offset(offset).
		Find(&sessions).Error; err != nil {
		return nil, err
	}
	return sessions, nil
}

// GetTrainingSessionsByCoach retrieves all training sessions for a coach
func (r *GormTrainingRepository) GetTrainingSessionsByCoach(coachID uint, limit, offset int) ([]models.TrainingSession, error) {
	var sessions []models.TrainingSession
	if err := r.db.Preload("WarmingUp").
		Preload("MainTraining").
		Where("coach_id = ?", coachID).
		Limit(limit).
		Offset(offset).
		Find(&sessions).Error; err != nil {
		return nil, err
	}
	return sessions, nil
}

// GetTrainingSessionsByDate retrieves all training sessions for a specific date
func (r *GormTrainingRepository) GetTrainingSessionsByDate(date time.Time) ([]models.TrainingSession, error) {
	var sessions []models.TrainingSession
	if err := r.db.Preload("WarmingUp").
		Preload("MainTraining").
		Preload("Coach").
		Where("date = ?", date.Format("2006-01-02")).
		Find(&sessions).Error; err != nil {
		return nil, err
	}
	return sessions, nil
}

// MarkAttendance records attendance for a training session
func (r *GormTrainingRepository) MarkAttendance(attendance *models.Attendance) error {
	return r.db.Create(attendance).Error
}

// SubmitFeedback records feedback for a training session
func (r *GormTrainingRepository) SubmitFeedback(feedback *models.Feedback) error {
	return r.db.Create(feedback).Error
}

// GetAttendanceBySession retrieves attendance records for a specific session
func (r *GormTrainingRepository) GetAttendanceBySession(sessionID uint) ([]models.Attendance, error) {
	var attendances []models.Attendance
	if err := r.db.Preload("Athlete").
		Where("training_session_id = ?", sessionID).
		Find(&attendances).Error; err != nil {
		return nil, err
	}
	return attendances, nil
}

// GetFeedbackBySession retrieves feedback records for a specific session
func (r *GormTrainingRepository) GetFeedbackBySession(sessionID uint) ([]models.Feedback, error) {
	var feedbacks []models.Feedback
	if err := r.db.Preload("Athlete").
		Where("training_session_id = ?", sessionID).
		Find(&feedbacks).Error; err != nil {
		return nil, err
	}
	return feedbacks, nil
} 