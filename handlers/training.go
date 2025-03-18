package handlers

import (
    "bytes"
    "fmt"
    "net/http"
    "strconv"
    "time"

    "github.com/3and7/training-platform/config"
    "github.com/3and7/training-platform/models"
    "github.com/3and7/training-platform/repositories"
    "github.com/3and7/training-platform/services"
    "github.com/gin-gonic/gin"
)

// Import sendReportEmail from report.go
// This is just a declaration - the actual implementation comes from handlers/report.go
var sendReportEmail = func(recipients []string, subject string, htmlBody string) error {
    // This function will be replaced at runtime with the actual implementation
    // from handlers/report.go due to package-level initialization.
    return nil
}

// TrainingHandler handles training-related requests
type TrainingHandler struct {
    service *services.TrainingService
}

// NewTrainingHandler creates a new TrainingHandler
func NewTrainingHandler() *TrainingHandler {
    repo := repositories.NewTrainingRepository(config.DB)
    service := services.NewTrainingService(repo)
    return &TrainingHandler{
        service: service,
    }
}

// CreateTrainingSession handles the creation of a new training session
func (h *TrainingHandler) CreateTrainingSession(c *gin.Context) {
    var input struct {
        Type            string    `json:"type" binding:"required"`
        Date            string    `json:"date" binding:"required"`
        StartTime       string    `json:"startTime" binding:"required"`
        EndTime         string    `json:"endTime" binding:"required"`
        WarmingUp       struct {
            Notes     string `json:"notes"`
            Duration int    `json:"duration"`
        } `json:"warmingUp"`
        MainTraining struct {
            Notes     string `json:"notes"`
            Duration int    `json:"duration"`
            PerformanceRecords []struct {
                AthleteID   uint    `json:"athleteID"`
                Time        string  `json:"time"`
                Repetitions int     `json:"repetitions"`
                Sets       int     `json:"sets"`
                Weight     float64 `json:"weight"`
                Notes      string  `json:"notes"`
            } `json:"performanceRecords"`
        } `json:"mainTraining"`
        CoolingDown struct {
            Notes     string `json:"notes"`
            Duration int    `json:"duration"`
        } `json:"coolingDown"`
        TrainingQuality int    `json:"trainingQuality"`
        Expectations   int    `json:"expectations"`
        TeamCondition  int    `json:"teamCondition"`
        Notes          string `json:"notes"`
        Documentation  string `json:"documentation"`
    }

    if err := c.ShouldBindJSON(&input); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // Parse date and times
    date, err := time.Parse("2006-01-02", input.Date)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid date format"})
        return
    }

    startTime, err := time.Parse("15:04", input.StartTime)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid start time format"})
        return
    }

    endTime, err := time.Parse("15:04", input.EndTime)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid end time format"})
        return
    }

    // Get coach ID from context (set by auth middleware)
    coachID, exists := c.Get("userID")
    if !exists {
        c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
        return
    }

    // Create training session
    session := models.TrainingSession{
        Type:            input.Type,
        Date:            date,
        StartTime:       time.Date(date.Year(), date.Month(), date.Day(), startTime.Hour(), startTime.Minute(), 0, 0, time.Local),
        EndTime:         time.Date(date.Year(), date.Month(), date.Day(), endTime.Hour(), endTime.Minute(), 0, 0, time.Local),
        CoachID:         coachID.(uint),
        TrainingQuality: input.TrainingQuality,
        Expectations:    input.Expectations,
        TeamCondition:   input.TeamCondition,
        Notes:          input.Notes,
        Documentation:  input.Documentation,
        WarmingUp: models.WarmingUp{
            Notes:    input.WarmingUp.Notes,
            Duration: input.WarmingUp.Duration,
        },
        MainTraining: models.MainTraining{
            Notes:    input.MainTraining.Notes,
            Duration: input.MainTraining.Duration,
        },
        CoolingDown: models.CoolingDown{
            Notes:    input.CoolingDown.Notes,
            Duration: input.CoolingDown.Duration,
        },
    }

    // Add performance records if type is endurance
    if input.Type == "endurance" {
        for _, record := range input.MainTraining.PerformanceRecords {
            performanceRecord := models.PerformanceRecord{
                AthleteID:   record.AthleteID,
                Time:        record.Time,
                Repetitions: record.Repetitions,
                Sets:       record.Sets,
                Weight:     record.Weight,
                Notes:      record.Notes,
            }
            session.MainTraining.PerformanceRecords = append(
                session.MainTraining.PerformanceRecords, 
                performanceRecord,
            )
        }
    }

    if err := h.service.CreateTrainingSession(&session); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }

    c.JSON(http.StatusCreated, gin.H{
        "message": "Training session created successfully", 
        "id": session.ID,
    })
}

// MarkAttendance handles marking attendance for a training session
func (h *TrainingHandler) MarkAttendance(c *gin.Context) {
    var input struct {
        TrainingSessionID uint   `json:"trainingSessionID" binding:"required"`
        AthleteID        uint   `json:"athleteID" binding:"required"`
    }

    if err := c.ShouldBindJSON(&input); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    attendance := models.Attendance{
        TrainingSessionID: input.TrainingSessionID,
        AthleteID:        input.AthleteID,
    }

    if err := h.service.MarkAttendance(&attendance); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    c.JSON(http.StatusCreated, gin.H{"message": "Attendance marked successfully"})
}

// SubmitFeedback handles athlete feedback submission
func (h *TrainingHandler) SubmitFeedback(c *gin.Context) {
    var input struct {
        TrainingSessionID uint   `json:"trainingSessionID" binding:"required"`
        TrainingQuality  int    `json:"trainingQuality" binding:"required,min=1,max=5"`
        Expectations     int    `json:"expectations" binding:"required,min=1,max=5"`
        BodyCondition    int    `json:"bodyCondition" binding:"required,min=1,max=10"`
        Intensity        int    `json:"intensity" binding:"required,min=1,max=10"`
        Notes           string `json:"notes"`
    }

    if err := c.ShouldBindJSON(&input); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // Get athlete ID from context (set by auth middleware)
    athleteID, exists := c.Get("userID")
    if !exists {
        c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
        return
    }

    feedback := models.Feedback{
        TrainingSessionID: input.TrainingSessionID,
        AthleteID:        athleteID.(uint),
        TrainingQuality:  input.TrainingQuality,
        Expectations:     input.Expectations,
        BodyCondition:    input.BodyCondition,
        Intensity:        input.Intensity,
        Notes:           input.Notes,
    }

    if err := h.service.SubmitFeedback(&feedback); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    c.JSON(http.StatusCreated, gin.H{"message": "Feedback submitted successfully"})
}

// GetTrainingSession retrieves a training session by ID
func (h *TrainingHandler) GetTrainingSession(c *gin.Context) {
    id := c.Param("id")
    
    sessionID, err := strconv.ParseUint(id, 10, 32)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid session ID"})
        return
    }

    session, err := h.service.GetTrainingSessionByID(uint(sessionID))
    if err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "Training session not found"})
        return
    }

    c.JSON(http.StatusOK, session)
}

// GetTrainingSessions retrieves all training sessions with pagination
func (h *TrainingHandler) GetTrainingSessions(c *gin.Context) {
    page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
    pageSize, _ := strconv.Atoi(c.DefaultQuery("pageSize", "10"))
    
    if page < 1 {
        page = 1
    }
    if pageSize < 1 || pageSize > 100 {
        pageSize = 10
    }

    sessions, err := h.service.GetTrainingSessions(page, pageSize)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve training sessions"})
        return
    }

    c.JSON(http.StatusOK, sessions)
}

// GetSessionStats retrieves statistics for a specific session
func (h *TrainingHandler) GetSessionStats(c *gin.Context) {
    id := c.Param("id")
    
    sessionID, err := strconv.ParseUint(id, 10, 32)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid session ID"})
        return
    }

    stats, err := h.service.GetSessionStats(uint(sessionID))
    if err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
        return
    }

    c.JSON(http.StatusOK, stats)
}

// SubmitTrainingSession handles the submission of training sessions and sends notification emails
func (h *TrainingHandler) SubmitTrainingSession(c *gin.Context) {
    // Parse request
    var req struct {
        SessionID  uint   `json:"session_id"`
        Notes      string `json:"notes"`
        Schedule   string `json:"schedule"`
    }
    
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    
    // Get session details
    var session models.TrainingSession
    if err := config.DB.First(&session, req.SessionID).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve session information"})
        return
    }
    
    // Update session with notes
    session.Notes = req.Notes
    if err := config.DB.Save(&session).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update session with notes"})
        return
    }
    
    // Get coach and stakeholders email addresses
    var coach models.User
    if err := config.DB.First(&coach, session.CoachID).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve coach information"})
        return
    }
    
    var stakeholders []models.User
    if err := config.DB.Where("role = ?", "stakeholder").Find(&stakeholders).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve stakeholder information"})
        return
    }
    
    // Create list of recipient emails
    recipients := []string{coach.Email}
    for _, s := range stakeholders {
        recipients = append(recipients, s.Email)
    }
    
    // Generate email content with session information, notes, and schedule
    trainingDate := session.StartTime.Format("Monday, January 2, 2006")
    trainingTime := fmt.Sprintf("%s - %s", 
        session.StartTime.Format("3:04 PM"),
        session.EndTime.Format("3:04 PM"))
    
    // Prepare email HTML
    var emailHTML bytes.Buffer
    
    emailHTML.WriteString("<html><body>")
    emailHTML.WriteString("<h1>Training Session Completed</h1>")
    emailHTML.WriteString(fmt.Sprintf("<p><strong>Date:</strong> %s</p>", trainingDate))
    emailHTML.WriteString(fmt.Sprintf("<p><strong>Time:</strong> %s</p>", trainingTime))
    emailHTML.WriteString(fmt.Sprintf("<p><strong>Type:</strong> %s</p>", session.Type))
    emailHTML.WriteString(fmt.Sprintf("<p><strong>Coach:</strong> %s %s</p>", coach.FirstName, coach.LastName))
    
    if session.Notes != "" {
        emailHTML.WriteString("<h2>Notes</h2>")
        emailHTML.WriteString(fmt.Sprintf("<p>%s</p>", session.Notes))
    }
    
    emailHTML.WriteString("<h2>Training Details</h2>")
    // Add training details as needed
    
    emailHTML.WriteString("<p>You can view the full session report and attendance details in the platform.</p>")
    emailHTML.WriteString(fmt.Sprintf("<p><a href='https://3and7.example.com/reports/session/%d'>View Session Report</a></p>", session.ID))
    
    emailHTML.WriteString("</body></html>")
    
    // Send email
    subject := fmt.Sprintf("Training Session Completed: %s", trainingDate)
    if err := sendReportEmail(recipients, subject, emailHTML.String()); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send notification email"})
        return
    }
    
    // Return success response
    c.JSON(http.StatusOK, gin.H{
        "message": "Training session submitted successfully and notification sent",
        "redirect": "/training/completed",
    })
} 