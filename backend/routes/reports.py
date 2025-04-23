from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from io import BytesIO
from datetime import datetime, date, timedelta
from dependencies.auth import get_current_user, get_optional_user
from dependencies.database import get_db, get_db_session
from models.report import (
    ReportFormat, 
    TrainingReportResponse, 
    AttendanceReportResponse, 
    FeedbackReportResponse,
    ReportExportRequest,
    MonthlyReportResponse
)
from services.report_service import ReportService
from repositories.independent_training_repository import IndependentTrainingRepository
from exceptions.app_exception import AppException
from models.db_models import User, TrainingSession, Feedback, Attendance
import logging
import json
import os
from typing import Dict, List, Union, Any

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)

# Helper function to get user role from User object
def get_user_role(current_user: User = Depends(get_current_user)):
    return current_user.role if hasattr(current_user, "role") else "unknown"

# Helper function to check if user has a specific role
def has_role(role: str, current_user: User = Depends(get_current_user)):
    return current_user.role == role if hasattr(current_user, "role") else False

@router.get("/training", response_model=TrainingReportResponse)
def get_training_report(
    start_date: str = Query(..., description="Start date in format YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in format YYYY-MM-DD"),
    format: Optional[ReportFormat] = Query(
        ReportFormat.JSON, 
        description="Format of the report (json, pdf, ppt)"
    ),
    db_session: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    user_role: str = Depends(get_user_role),
):
    """
    Generate a training report for the specified date range.
    
    The report includes:
    - Summary of training sessions
    - List of sessions with details
    - Attendance stats for each session
    - Feedback summary for each session
    
    Returns:
    - JSON data by default
    - PDF or PowerPoint if format is specified
    """
    try:
        # Parse dates
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD."
        )
    
    report_service = ReportService(db_session)
    
    if format == ReportFormat.JSON:
        # Return JSON report
        report = report_service.generate_training_report(
            start_date=start_date_obj,
            end_date=end_date_obj,
            user_id=current_user["id"],
            user_role=user_role
        )
        return report
    
    elif format == ReportFormat.PDF:
        # Return PDF report
        pdf_data = report_service.generate_training_report_pdf(
            start_date=start_date_obj,
            end_date=end_date_obj,
            user_id=current_user["id"],
            user_role=user_role
        )
        
        response = Response(
            content=pdf_data,
            media_type="application/pdf"
        )
        
        response.headers["Content-Disposition"] = (
            f"attachment; filename=training_report_{start_date}_{end_date}.pdf"
        )
        
        return response
    
    elif format == ReportFormat.PPT:
        # Return PowerPoint report
        ppt_data = report_service.generate_training_report_ppt(
            start_date=start_date_obj,
            end_date=end_date_obj,
            user_id=current_user["id"],
            user_role=user_role
        )
        
        response = Response(
            content=ppt_data,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
        response.headers["Content-Disposition"] = (
            f"attachment; filename=training_report_{start_date}_{end_date}.pptx"
        )
        
        return response


@router.get("/attendance", response_model=AttendanceReportResponse)
def get_attendance_report(
    start_date: str = Query(..., description="Start date in format YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in format YYYY-MM-DD"),
    athlete_id: Optional[str] = Query(None, description="Get attendance for a specific athlete"),
    format: Optional[ReportFormat] = Query(
        ReportFormat.JSON, 
        description="Format of the report (json, pdf, ppt)"
    ),
    db_session: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    user_role: str = Depends(get_user_role),
):
    """
    Generate an attendance report for the specified date range.
    
    The report includes:
    - Overall attendance statistics
    - For a team: attendance rate for each athlete
    - For an individual: sessions attended/missed with details
    
    Returns:
    - JSON data by default
    - PDF or PowerPoint if format is specified
    """
    try:
        # Parse dates
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD."
        )
    
    # Set athlete_id for athletes viewing their own attendance
    if user_role == "athlete" and not athlete_id:
        athlete_id = current_user["id"]
    
    # For coaches and admins, if no athlete_id is specified, return team attendance
    # For stakeholders, require athlete_id or raise error
    if user_role == "stakeholder" and not athlete_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stakeholders must specify an athlete_id"
        )
    
    report_service = ReportService(db_session)
    
    if format == ReportFormat.JSON:
        # Return JSON report
        report = report_service.generate_attendance_report(
            start_date=start_date_obj,
            end_date=end_date_obj,
            athlete_id=athlete_id
        )
        return report
    
    elif format == ReportFormat.PDF:
        # Return PDF report
        pdf_data = report_service.generate_attendance_report_pdf(
            start_date=start_date_obj,
            end_date=end_date_obj,
            athlete_id=athlete_id
        )
        
        response = Response(
            content=pdf_data,
            media_type="application/pdf"
        )
        
        filename = f"attendance_report_{start_date}_{end_date}"
        if athlete_id:
            filename += f"_{athlete_id}"
        filename += ".pdf"
        
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        
        return response
    
    elif format == ReportFormat.PPT:
        # Return PowerPoint report
        ppt_data = report_service.generate_attendance_report_ppt(
            start_date=start_date_obj,
            end_date=end_date_obj,
            athlete_id=athlete_id
        )
        
        response = Response(
            content=ppt_data,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
        filename = f"attendance_report_{start_date}_{end_date}"
        if athlete_id:
            filename += f"_{athlete_id}"
        filename += ".pptx"
        
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        
        return response


@router.get("/feedback", response_model=FeedbackReportResponse)
def get_feedback_report(
    start_date: str = Query(..., description="Start date in format YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in format YYYY-MM-DD"),
    session_id: Optional[str] = Query(None, description="Get feedback for a specific session"),
    format: Optional[ReportFormat] = Query(
        ReportFormat.JSON, 
        description="Format of the report (json, pdf, ppt)"
    ),
    db_session: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    user_role: str = Depends(get_user_role),
):
    """
    Generate a feedback report for the specified date range.
    
    The report includes:
    - Overall feedback statistics
    - For a date range: feedback summary for each session
    - For a specific session: detailed feedback from each athlete
    
    Returns:
    - JSON data by default
    - PDF or PowerPoint if format is specified
    """
    try:
        # Parse dates
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD."
        )
    
    # Check permissions based on user role
    # Athletes can only see aggregate feedback
    # Coaches can see detailed feedback
    # Admins can see all feedback
    if user_role == "athlete" and session_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Athletes can only view aggregate feedback"
        )
    
    report_service = ReportService(db_session)
    
    if format == ReportFormat.JSON:
        # Return JSON report
        report = report_service.generate_feedback_report(
            start_date=start_date_obj,
            end_date=end_date_obj,
            session_id=session_id
        )
        return report
    
    elif format == ReportFormat.PDF:
        # Return PDF report
        pdf_data = report_service.generate_feedback_report_pdf(
            start_date=start_date_obj,
            end_date=end_date_obj,
            session_id=session_id
        )
        
        response = Response(
            content=pdf_data,
            media_type="application/pdf"
        )
        
        filename = f"feedback_report_{start_date}_{end_date}"
        if session_id:
            filename += f"_session_{session_id}"
        filename += ".pdf"
        
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        
        return response
    
    elif format == ReportFormat.PPT:
        # Return PowerPoint report
        ppt_data = report_service.generate_feedback_report_ppt(
            start_date=start_date_obj,
            end_date=end_date_obj,
            session_id=session_id
        )
        
        response = Response(
            content=ppt_data,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
        filename = f"feedback_report_{start_date}_{end_date}"
        if session_id:
            filename += f"_session_{session_id}"
        filename += ".pptx"
        
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        
        return response


@router.post("/export")
def export_report(
    report_request: ReportExportRequest,
    db_session: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    user_role: str = Depends(get_user_role),
):
    """
    Export a custom report as PDF or PowerPoint.
    
    Accepts:
    - Custom report data
    - Title for the report
    - Format (PDF or PPT)
    
    Returns:
    - PDF or PowerPoint file
    """
    report_service = ReportService(db_session)
    
    if report_request.format == ReportFormat.PDF:
        # Export as PDF
        pdf_data = report_service.export_custom_report_pdf(
            report_data=report_request.data,
            title=report_request.title
        )
        
        response = Response(
            content=pdf_data,
            media_type="application/pdf"
        )
        
        # Create safe filename from title
        safe_title = "".join(c if c.isalnum() else "_" for c in report_request.title)
        filename = f"report_{safe_title}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        
        return response
    
    elif report_request.format == ReportFormat.PPT:
        # Export as PowerPoint
        ppt_data = report_service.export_custom_report_ppt(
            report_data=report_request.data,
            title=report_request.title
        )
        
        response = Response(
            content=ppt_data,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
        # Create safe filename from title
        safe_title = "".join(c if c.isalnum() else "_" for c in report_request.title)
        filename = f"report_{safe_title}_{datetime.now().strftime('%Y%m%d')}.pptx"
        
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        
        return response
    
    else:
        # Invalid format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be PDF or PPT for exports"
        )


@router.get("/monthly", response_model=MonthlyReportResponse)
def get_monthly_report(
    start_date: str = Query(..., description="Start date in format YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in format YYYY-MM-DD"),
    format: Optional[ReportFormat] = Query(
        ReportFormat.JSON, 
        description="Format of the report (json, pdf, ppt)"
    ),
    db_session: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    user_role: str = Depends(get_user_role),
):
    """
    Generate a monthly report including both training sessions and independent training
    
    This combines data from both training sessions and independent training sessions
    to provide a comprehensive monthly view for coaches and athletes.
    """
    try:
        # Parse dates
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Initialize report service
        report_service = ReportService(db_session)
        
        # Get standard training report data
        training_report = report_service.generate_training_report(start, end, current_user['id'], user_role)
        
        # Fetch independent training data
        independent_repo = IndependentTrainingRepository(db_session)
        independent_training = independent_repo.get_independent_training_sessions(
            start_date=start,
            end_date=end,
            user_id=current_user['id'] if user_role == 'athlete' else None,
            coach_id=current_user['id'] if user_role == 'coach' else None
        )
        
        # Process independent training data
        independent_training_data = []
        training_type_counts = {}
        
        for session in independent_training.get('sessions', []):
            # Add to type counts
            if session.type not in training_type_counts:
                training_type_counts[session.type] = 0
            training_type_counts[session.type] += 1
            
            # Add to list of sessions
            independent_training_data.append({
                "id": session.id,
                "date": session.date.strftime('%Y-%m-%d'),
                "type": session.type,
                "start_time": session.start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                "end_time": session.end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                "location": session.location,
                "intensity": session.intensity,
                "body_condition": session.body_condition
            })
        
        # Combine into monthly report
        monthly_report = {
            "title": f"Monthly Training Report: {start.strftime('%B %Y')}",
            "generated_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "date_range": f"{start_date} to {end_date}",
            "summary": {
                **training_report.summary,
                "independent_training_count": len(independent_training_data),
                "independent_training_types": training_type_counts
            },
            "data": training_report.data,
            "independent_training": independent_training_data
        }
        
        # Return JSON or generate PDF/PPT
        if format == ReportFormat.JSON:
            return monthly_report
        elif format == ReportFormat.PDF:
            pdf_bytes = report_service.generate_monthly_report_pdf(start, end, current_user['id'], user_role)
            return StreamingResponse(
                BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=monthly_report_{start_date}_to_{end_date}.pdf"}
            )
        elif format == ReportFormat.PPT:
            ppt_bytes = report_service.generate_monthly_report_ppt(start, end, current_user['id'], user_role)
            return StreamingResponse(
                BytesIO(ppt_bytes),
                media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                headers={"Content-Disposition": f"attachment; filename=monthly_report_{start_date}_to_{end_date}.pptx"}
            )
    except Exception as e:
        logger.error(f"Error generating monthly report: {str(e)}")
        raise AppException(status_code=500, detail=f"Failed to generate monthly report: {str(e)}")


@router.get("/overview")
def get_overview_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Get overview report with statistics
    """
    # Count total training sessions
    total_sessions = db.query(TrainingSession).count()
    
    # Count total users
    total_users = db.query(User).count()
    
    # Count total feedbacks
    total_feedbacks = db.query(Feedback).count()
    
    # Count total attendances
    total_attendances = db.query(Attendance).count()
    
    # Calculate average training quality
    avg_quality = db.query(TrainingSession).with_entities(
        db.func.avg(TrainingSession.training_quality)
    ).scalar() or 0
    
    # Return report data
    return {
        "total_sessions": total_sessions,
        "total_users": total_users,
        "total_feedbacks": total_feedbacks,
        "total_attendances": total_attendances,
        "average_training_quality": round(float(avg_quality), 2)
    } 