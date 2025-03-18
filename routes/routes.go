package routes

import (
    "github.com/3and7/training-platform/handlers"
    "github.com/3and7/training-platform/middlewares"
    "github.com/gin-gonic/gin"
)

func SetupRoutes(router *gin.Engine) {
    // Static routes
    router.Static("/static", "./static")
    router.StaticFile("/favicon.ico", "./static/favicon.ico")
    router.LoadHTMLGlob("templates/*")

    // Authentication routes
    authHandler := handlers.NewAuthHandler()
    auth := router.Group("/api/auth")
    {
        auth.POST("/login", authHandler.Login)
        auth.POST("/register", authHandler.Register)
        auth.GET("/profile", middlewares.AuthMiddleware(), authHandler.GetUserProfile)
    }

    // Training session routes
    trainingHandler := handlers.NewTrainingHandler()
    
    // Public training routes
    training := router.Group("/api/training")
    {
        training.GET("/sessions", trainingHandler.GetTrainingSessions)
        training.GET("/sessions/:id", trainingHandler.GetTrainingSession)
    }

    // Protected training routes
    protectedTraining := router.Group("/api/training")
    protectedTraining.Use(middlewares.AuthMiddleware())
    {
        // Coach-only routes
        coachRoutes := protectedTraining.Group("")
        coachRoutes.Use(middlewares.RoleMiddleware("coach"))
        {
            coachRoutes.POST("/sessions", trainingHandler.CreateTrainingSession)
            coachRoutes.POST("/attendance", trainingHandler.MarkAttendance)
            coachRoutes.POST("/submit", trainingHandler.SubmitTrainingSession)
        }

        // Athlete-only routes
        athleteRoutes := protectedTraining.Group("")
        athleteRoutes.Use(middlewares.RoleMiddleware("athlete"))
        {
            athleteRoutes.POST("/feedback", trainingHandler.SubmitFeedback)
        }

        // Coach and stakeholder routes
        reportRoutes := protectedTraining.Group("")
        reportRoutes.Use(middlewares.RoleMiddleware("coach", "stakeholder"))
        {
            reportRoutes.GET("/sessions/:id/stats", trainingHandler.GetSessionStats)
        }
        
        // History routes for all authenticated users
        protectedTraining.GET("/history", handlers.GetTrainingHistory)
    }
    
    // Report routes
    reports := router.Group("/api/reports")
    reports.Use(middlewares.AuthMiddleware())
    {
        reports.GET("/session/:id", handlers.GenerateSessionReport)
        reports.GET("/monthly", handlers.GenerateMonthlyReport)
    }

    // HTML routes
    router.GET("/", func(c *gin.Context) {
        c.Redirect(302, "/training")
    })
    
    router.GET("/training", func(c *gin.Context) {
        c.HTML(200, "integrated-training.html", gin.H{})
    })
    
    router.GET("/feedback", func(c *gin.Context) {
        c.HTML(200, "athlete-feedback.html", gin.H{})
    })
    
    router.GET("/history", func(c *gin.Context) {
        c.HTML(200, "training-history.html", gin.H{})
    })
    
    router.GET("/training/completed", func(c *gin.Context) {
        c.HTML(200, "post_training_completion.html", gin.H{})
    })
    
    router.GET("/reports/session/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.Redirect(302, "/api/reports/session/"+id)
    })
    
    router.GET("/reports/monthly", func(c *gin.Context) {
        period := c.DefaultQuery("period", "month")
        c.Redirect(302, "/api/reports/monthly?period="+period)
    })
    
    router.GET("/reports/calendar", func(c *gin.Context) {
        c.HTML(200, "training_report_calendar.html", gin.H{})
    })

    // TODO: Add user management routes
    // TODO: Add reporting routes
} 