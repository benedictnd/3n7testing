package services

import (
	"errors"
	"time"

	"github.com/3and7/training-platform/models"
	"github.com/3and7/training-platform/repositories"
)

// TrainingService defines business operations for training
type TrainingService struct {
	repo repositories.TrainingRepository
}

// NewTrainingService creates a new instance of TrainingService
func NewTrainingService(repo repositories.TrainingRepository) *TrainingService {
	return &TrainingService{
		repo: repo,
	}
}

// CreateTrainingSession validates and creates a new training session
func (s *TrainingService) CreateTrainingSession(session *models.TrainingSession) error {
	// Validate session data
	if session.Type != "core" && session.Type != "endurance" {
		return errors.New("invalid training type: must be 'core' or 'endurance'")
	}

	if session.StartTime.After(session.EndTime) {
		return errors.New("start time cannot be after end time")
	}

	// Create session
	return s.repo.CreateTrainingSession(session)
}

// GetTrainingSessionByID retrieves a training session by ID
func (s *TrainingService) GetTrainingSessionByID(id uint) (*models.TrainingSession, error) {
	return s.repo.GetTrainingSessionByID(id)
}

// GetTrainingSessions retrieves paginated training sessions
func (s *TrainingService) GetTrainingSessions(page, pageSize int) ([]models.TrainingSession, error) {
	offset := (page - 1) * pageSize
	return s.repo.GetTrainingSessions(pageSize, offset)
}

// GetTrainingSessionsByCoach retrieves paginated training sessions for a coach
func (s *TrainingService) GetTrainingSessionsByCoach(coachID uint, page, pageSize int) ([]models.TrainingSession, error) {
	offset := (page - 1) * pageSize
	return s.repo.GetTrainingSessionsByCoach(coachID, pageSize, offset)
}

// GetTrainingSessionsByDate retrieves all training sessions for a specific date
func (s *TrainingService) GetTrainingSessionsByDate(date time.Time) ([]models.TrainingSession, error) {
	return s.repo.GetTrainingSessionsByDate(date)
}

// MarkAttendance validates and marks attendance for a training session
func (s *TrainingService) MarkAttendance(attendance *models.Attendance) error {
	// Get session to verify it has ended
	session, err := s.repo.GetTrainingSessionByID(attendance.TrainingSessionID)
	if err != nil {
		return err
	}

	// Validate attendance time (can only be marked after session ends)
	if time.Now().Before(session.EndTime) {
		return errors.New("attendance can only be marked after session ends")
	}

	// Check if athlete is already marked as attended
	attendances, err := s.repo.GetAttendanceBySession(attendance.TrainingSessionID)
	if err != nil {
		return err
	}

	for _, a := range attendances {
		if a.AthleteID == attendance.AthleteID {
			return errors.New("athlete already marked as attended")
		}
	}

	// Mark attendance
	attendance.CheckInTime = time.Now()
	return s.repo.MarkAttendance(attendance)
}

// SubmitFeedback validates and submits feedback for a training session
func (s *TrainingService) SubmitFeedback(feedback *models.Feedback) error {
	// Get session to verify it has ended
	session, err := s.repo.GetTrainingSessionByID(feedback.TrainingSessionID)
	if err != nil {
		return err
	}

	// Validate submission time (can only be submitted after session ends)
	if time.Now().Before(session.EndTime) {
		return errors.New("feedback can only be submitted after session ends")
	}

	// Validate ratings
	if feedback.TrainingQuality < 1 || feedback.TrainingQuality > 5 {
		return errors.New("training quality rating must be between 1 and 5")
	}

	if feedback.Expectations < 1 || feedback.Expectations > 5 {
		return errors.New("expectations rating must be between 1 and 5")
	}

	if feedback.BodyCondition < 1 || feedback.BodyCondition > 10 {
		return errors.New("body condition rating must be between 1 and 10")
	}

	if feedback.Intensity < 1 || feedback.Intensity > 10 {
		return errors.New("intensity rating must be between 1 and 10")
	}

	// Check if athlete attended the session
	attendances, err := s.repo.GetAttendanceBySession(feedback.TrainingSessionID)
	if err != nil {
		return err
	}

	attended := false
	for _, a := range attendances {
		if a.AthleteID == feedback.AthleteID {
			attended = true
			break
		}
	}

	if !attended {
		return errors.New("athlete did not attend this session")
	}

	// Check if athlete already submitted feedback
	feedbacks, err := s.repo.GetFeedbackBySession(feedback.TrainingSessionID)
	if err != nil {
		return err
	}

	for _, f := range feedbacks {
		if f.AthleteID == feedback.AthleteID {
			return errors.New("athlete already submitted feedback")
		}
	}

	// Submit feedback
	return s.repo.SubmitFeedback(feedback)
}

// GetSessionStats calculates statistics for a training session
func (s *TrainingService) GetSessionStats(sessionID uint) (map[string]interface{}, error) {
	session, err := s.repo.GetTrainingSessionByID(sessionID)
	if err != nil {
		return nil, err
	}

	feedbacks, err := s.repo.GetFeedbackBySession(sessionID)
	if err != nil {
		return nil, err
	}

	// Calculate average ratings
	var avgTrainingQuality, avgExpectations, avgBodyCondition, avgIntensity float64
	fbCount := len(feedbacks)

	if fbCount > 0 {
		for _, fb := range feedbacks {
			avgTrainingQuality += float64(fb.TrainingQuality)
			avgExpectations += float64(fb.Expectations)
			avgBodyCondition += float64(fb.BodyCondition)
			avgIntensity += float64(fb.Intensity)
		}

		avgTrainingQuality /= float64(fbCount)
		avgExpectations /= float64(fbCount)
		avgBodyCondition /= float64(fbCount)
		avgIntensity /= float64(fbCount)
	}

	// Calculate total duration
	totalDuration := session.WarmingUp.Duration + 
		session.MainTraining.Duration + 
		session.CoolingDown.Duration

	return map[string]interface{}{
		"session_id":         session.ID,
		"type":               session.Type,
		"date":               session.Date,
		"attendees_count":    len(session.Attendances),
		"feedback_count":     fbCount,
		"total_duration":     totalDuration,
		"avg_training_quality": avgTrainingQuality,
		"avg_expectations":   avgExpectations,
		"avg_body_condition": avgBodyCondition,
		"avg_intensity":      avgIntensity,
	}, nil
} 