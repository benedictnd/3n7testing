package handlers

import (
    "bytes"
    "fmt"
    "html/template"
    "net/http"
    "net/smtp"
    "os"
    "strconv"
    "strings"
    "time"

    "github.com/3and7/training-platform/config"
    "github.com/3and7/training-platform/models"
    "github.com/gin-gonic/gin"
)

type TrainingReport struct {
    Session        models.TrainingSession
    WarmingUp      models.WarmingUp
    MainTraining   models.MainTraining
    CoolingDown    models.CoolingDown
    Attendees      []models.User
    Feedbacks      []models.Feedback
    AverageRatings struct {
        TrainingQuality float64
        Expectations   float64
        BodyCondition  float64
        Intensity     float64
    }
}

// GenerateSessionReport generates a detailed report for a specific training session
func GenerateSessionReport(c *gin.Context) {
    sessionID := c.Param("id")

    var session models.TrainingSession
    if err := config.DB.Preload("WarmingUp").
        Preload("MainTraining").
        Preload("MainTraining.PerformanceRecords").
        Preload("CoolingDown").
        Preload("Attendances").
        Preload("Attendances.Athlete").
        Preload("Feedbacks").
        First(&session, sessionID).Error; err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "Training session not found"})
        return
    }

    // Calculate average ratings
    var avgRatings struct {
        TrainingQuality float64
        Expectations   float64
        BodyCondition  float64
        Intensity     float64
    }

    if len(session.Feedbacks) > 0 {
        for _, feedback := range session.Feedbacks {
            avgRatings.TrainingQuality += float64(feedback.TrainingQuality)
            avgRatings.Expectations += float64(feedback.Expectations)
            avgRatings.BodyCondition += float64(feedback.BodyCondition)
            avgRatings.Intensity += float64(feedback.Intensity)
        }
        count := float64(len(session.Feedbacks))
        avgRatings.TrainingQuality /= count
        avgRatings.Expectations /= count
        avgRatings.BodyCondition /= count
        avgRatings.Intensity /= count
    }

    // Get list of attendees
    var attendees []models.User
    for _, attendance := range session.Attendances {
        attendees = append(attendees, attendance.Athlete)
    }

    report := TrainingReport{
        Session:        session,
        WarmingUp:      session.WarmingUp,
        MainTraining:   session.MainTraining,
        CoolingDown:    session.CoolingDown,
        Attendees:      attendees,
        Feedbacks:      session.Feedbacks,
        AverageRatings: avgRatings,
    }

    // Generate HTML report
    var reportHTML bytes.Buffer
    tmpl := template.Must(template.ParseFiles("templates/session_report.html"))
    if err := tmpl.Execute(&reportHTML, report); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate report"})
        return
    }

    // Send email with report
    sendParam := c.DefaultQuery("send", "false")
    sendEmail, _ := strconv.ParseBool(sendParam)

    if sendEmail {
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

        // Send email with report
        if err := sendReportEmail(recipients, "Training Session Report", reportHTML.String()); err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send email report"})
            return
        }

        c.JSON(http.StatusOK, gin.H{"message": "Report sent successfully to coach and stakeholders"})
        return
    }

    c.HTML(http.StatusOK, "session_report.html", report)
}

// GenerateMonthlyReport generates a monthly summary of all training sessions
func GenerateMonthlyReport(c *gin.Context) {
    year := c.Query("year")
    month := c.Query("month")

    if year == "" || month == "" {
        now := time.Now()
        year = fmt.Sprintf("%d", now.Year())
        month = fmt.Sprintf("%02d", now.Month())
    }

    startDate := fmt.Sprintf("%s-%s-01", year, month)
    start, err := time.Parse("2006-01-02", startDate)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid date format"})
        return
    }

    endDate := start.AddDate(0, 1, 0)

    var sessions []models.TrainingSession
    if err := config.DB.Preload("WarmingUp").
        Preload("MainTraining").
        Preload("MainTraining.PerformanceRecords").
        Preload("CoolingDown").
        Preload("Attendances").
        Preload("Feedbacks").
        Where("date >= ? AND date < ?", start, endDate).
        Find(&sessions).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve sessions"})
        return
    }

    // Calculate monthly statistics
    stats := struct {
        TotalSessions     int
        CoreSessions      int
        EnduranceSessions int
        TotalAttendees    int
        AverageRatings    struct {
            TrainingQuality float64
            Expectations   float64
            BodyCondition  float64
            Intensity     float64
        }
    }{}

    stats.TotalSessions = len(sessions)

    var totalFeedbacks int
    for _, session := range sessions {
        if session.Type == "core" {
            stats.CoreSessions++
        } else {
            stats.EnduranceSessions++
        }

        stats.TotalAttendees += len(session.Attendances)

        for _, feedback := range session.Feedbacks {
            stats.AverageRatings.TrainingQuality += float64(feedback.TrainingQuality)
            stats.AverageRatings.Expectations += float64(feedback.Expectations)
            stats.AverageRatings.BodyCondition += float64(feedback.BodyCondition)
            stats.AverageRatings.Intensity += float64(feedback.Intensity)
            totalFeedbacks++
        }
    }

    if totalFeedbacks > 0 {
        count := float64(totalFeedbacks)
        stats.AverageRatings.TrainingQuality /= count
        stats.AverageRatings.Expectations /= count
        stats.AverageRatings.BodyCondition /= count
        stats.AverageRatings.Intensity /= count
    }

    // Generate HTML report
    var reportHTML bytes.Buffer
    tmpl := template.Must(template.ParseFiles("templates/monthly_report.html"))
    if err := tmpl.Execute(&reportHTML, gin.H{
        "Year":     year,
        "Month":    month,
        "Sessions": sessions,
        "Stats":    stats,
    }); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate report"})
        return
    }

    // Send email with report
    sendParam := c.DefaultQuery("send", "false")
    sendEmail, _ := strconv.ParseBool(sendParam)

    if sendEmail {
        // Get coach and stakeholders email addresses
        var coaches []models.User
        if err := config.DB.Where("role = ?", "coach").Find(&coaches).Error; err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve coach information"})
            return
        }

        var stakeholders []models.User
        if err := config.DB.Where("role = ?", "stakeholder").Find(&stakeholders).Error; err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve stakeholder information"})
            return
        }

        // Create list of recipient emails
        recipients := []string{}
        for _, c := range coaches {
            recipients = append(recipients, c.Email)
        }
        for _, s := range stakeholders {
            recipients = append(recipients, s.Email)
        }

        // Send email with report
        if err := sendReportEmail(recipients, fmt.Sprintf("Monthly Training Report - %s %s", month, year), reportHTML.String()); err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send email report"})
            return
        }

        c.JSON(http.StatusOK, gin.H{"message": "Monthly report sent successfully to coaches and stakeholders"})
        return
    }

    c.HTML(http.StatusOK, "monthly_report.html", gin.H{
        "Year":     year,
        "Month":    month,
        "Sessions": sessions,
        "Stats":    stats,
    })
}

// GetTrainingHistory retrieves training history data for chart and calendar visualization
func GetTrainingHistory(c *gin.Context) {
    period := c.DefaultQuery("period", "month")
    userID, _ := c.Get("userID")
    
    var startDate, endDate time.Time
    now := time.Now()
    
    // Calculate date range based on period
    switch period {
    case "week":
        // Get current week (Sunday to Saturday)
        weekday := now.Weekday()
        startDate = now.AddDate(0, 0, -int(weekday))
        endDate = startDate.AddDate(0, 0, 7)
    case "month":
        // Get current month
        startDate = time.Date(now.Year(), now.Month(), 1, 0, 0, 0, 0, time.Local)
        endDate = startDate.AddDate(0, 1, 0)
    case "6weeks":
        // Get last 6 weeks
        startDate = now.AddDate(0, 0, -42) // 6 weeks * 7 days
        endDate = now
    case "quarter":
        // Get current quarter
        quarter := (int(now.Month()) - 1) / 3
        startDate = time.Date(now.Year(), time.Month(quarter*3+1), 1, 0, 0, 0, 0, time.Local)
        endDate = startDate.AddDate(0, 3, 0)
    case "custom":
        // Parse custom date range
        start := c.Query("start")
        end := c.Query("end")
        
        if start != "" && end != "" {
            startDate, _ = time.Parse("2006-01-02", start)
            endDate, _ = time.Parse("2006-01-02", end)
            endDate = endDate.AddDate(0, 0, 1) // Include the end date
        } else {
            // Default to current month if custom range is invalid
            startDate = time.Date(now.Year(), now.Month(), 1, 0, 0, 0, 0, time.Local)
            endDate = startDate.AddDate(0, 1, 0)
        }
    }
    
    // Get all training sessions in the date range
    var sessions []models.TrainingSession
    if err := config.DB.Preload("WarmingUp").
        Preload("MainTraining").
        Preload("Coach").
        Preload("Attendances").
        Where("date >= ? AND date < ?", startDate.Format("2006-01-02"), endDate.Format("2006-01-02")).
        Find(&sessions).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve training sessions"})
        return
    }
    
    // Calculate statistics
    totalSessions := len(sessions)
    var userAttendance int
    var totalDuration int
    
    // Count sessions by time of day
    var morningSessions, afternoonSessions, nightSessions int
    var userMorningSessions, userAfternoonSessions, userNightSessions int
    
    // Weekly data for chart
    weeklyData := make(map[string]map[string]int)
    
    // Calendar data
    calendarData := make(map[string]map[string]bool)
    
    for _, session := range sessions {
        // Calculate total duration
        duration := session.WarmingUp.Duration + session.MainTraining.Duration + session.CoolingDown.Duration
        totalDuration += duration
        
        // Categorize by time of day
        hour := session.StartTime.Hour()
        timeCategory := "morning"
        if hour >= 12 && hour < 17 {
            timeCategory = "afternoon"
            afternoonSessions++
        } else if hour >= 17 {
            timeCategory = "night"
            nightSessions++
        } else {
            morningSessions++
        }
        
        // Check user attendance
        userAttended := false
        for _, attendance := range session.Attendances {
            if attendance.AthleteID == userID {
                userAttended = true
                // Count user attendance by time of day
                if timeCategory == "morning" {
                    userMorningSessions++
                } else if timeCategory == "afternoon" {
                    userAfternoonSessions++
                } else {
                    userNightSessions++
                }
                break
            }
        }
        
        if userAttended {
            userAttendance++
        }
        
        // Add to weekly data
        weekNum := getWeekNumber(session.Date)
        weekKey := fmt.Sprintf("Week %d", weekNum)
        
        if _, exists := weeklyData[weekKey]; !exists {
            weeklyData[weekKey] = map[string]int{
                "morning": 0,
                "afternoon": 0,
                "night": 0,
            }
        }
        weeklyData[weekKey][timeCategory]++
        
        // Add to calendar data
        dateKey := session.Date.Format("2006-01-02")
        if _, exists := calendarData[dateKey]; !exists {
            calendarData[dateKey] = map[string]bool{
                "morning": false,
                "afternoon": false,
                "night": false,
            }
        }
        calendarData[dateKey][timeCategory] = true
    }
    
    // Prepare chart data
    var chartLabels []string
    var morningData, afternoonData, nightData []int
    
    // Sort weeks and create chart data
    // This is a simplified version - in a real implementation, you would ensure all weeks are represented
    for i := 1; i <= 6; i++ {
        weekKey := fmt.Sprintf("Week %d", i)
        chartLabels = append(chartLabels, weekKey)
        
        if data, exists := weeklyData[weekKey]; exists {
            morningData = append(morningData, data["morning"])
            afternoonData = append(afternoonData, data["afternoon"])
            nightData = append(nightData, data["night"])
        } else {
            morningData = append(morningData, 0)
            afternoonData = append(afternoonData, 0)
            nightData = append(nightData, 0)
        }
    }
    
    // Average duration per session
    avgDuration := 0
    if totalSessions > 0 {
        avgDuration = totalDuration / totalSessions
    }
    
    // Prepare response data
    response := gin.H{
        "stats": gin.H{
            "totalSessions": totalSessions,
            "userAttendance": userAttendance,
            "attendancePercentage": calculatePercentage(userAttendance, totalSessions),
            "avgDuration": avgDuration,
        },
        "team": gin.H{
            "totalSessions": totalSessions,
            "morningSessions": morningSessions,
            "afternoonSessions": afternoonSessions,
            "nightSessions": nightSessions,
        },
        "user": gin.H{
            "attendedSessions": userAttendance,
            "morningSessions": userMorningSessions,
            "afternoonSessions": userAfternoonSessions,
            "nightSessions": userNightSessions,
        },
        "chart": gin.H{
            "labels": chartLabels,
            "datasets": gin.H{
                "morning": morningData,
                "afternoon": afternoonData,
                "night": nightData,
            },
        },
        "calendar": calendarData,
        "dateRange": gin.H{
            "start": startDate.Format("2006-01-02"),
            "end": endDate.AddDate(0, 0, -1).Format("2006-01-02"), // Subtract 1 day since endDate is exclusive
        },
    }
    
    c.JSON(http.StatusOK, response)
}

// sendReportEmail sends an email with the provided report HTML
func sendReportEmail(recipients []string, subject string, htmlBody string) error {
    // Get email configuration from environment variables
    smtpHost := os.Getenv("SMTP_HOST")
    smtpPort := os.Getenv("SMTP_PORT")
    smtpUser := os.Getenv("SMTP_USER")
    smtpPass := os.Getenv("SMTP_PASS")
    senderEmail := os.Getenv("SENDER_EMAIL")
    
    if smtpHost == "" || smtpPort == "" || smtpUser == "" || smtpPass == "" || senderEmail == "" {
        return fmt.Errorf("email configuration not complete")
    }
    
    // Set up email headers
    headers := make(map[string]string)
    headers["From"] = senderEmail
    headers["To"] = strings.Join(recipients, ", ")
    headers["Subject"] = subject
    headers["MIME-Version"] = "1.0"
    headers["Content-Type"] = "text/html; charset=utf-8"
    
    // Compose email message
    message := ""
    for k, v := range headers {
        message += fmt.Sprintf("%s: %s\r\n", k, v)
    }
    message += "\r\n" + htmlBody
    
    // Connect to SMTP server
    auth := smtp.PlainAuth("", smtpUser, smtpPass, smtpHost)
    addr := fmt.Sprintf("%s:%s", smtpHost, smtpPort)
    
    return smtp.SendMail(addr, auth, senderEmail, recipients, []byte(message))
}

// getWeekNumber returns the week number (1-53) for a given date
func getWeekNumber(date time.Time) int {
    _, week := date.ISOWeek()
    return week
}

// calculatePercentage calculates the percentage of part out of total
func calculatePercentage(part, total int) int {
    if total == 0 {
        return 0
    }
    return int(float64(part) / float64(total) * 100)
} 