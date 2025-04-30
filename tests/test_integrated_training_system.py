import pytest
import datetime
from typing import Dict, List, Optional
from unittest.mock import patch, MagicMock

from models.team import Team, Coach, Athlete, Position
from models.training import TrainingSession, TrainingActivity, Feedback, Attendance
from services.team_service import TeamService
from services.training_service import TrainingService
from services.feedback_service import FeedbackService
from services.attendance_service import AttendanceService


class TestIntegratedTrainingSystem:
    """Test suite for the Integrated Training System using Jaya Jakarta Basketball as mock data"""

    @pytest.fixture
    def mock_team_data(self):
        """Create mock team data for Jaya Jakarta Basketball"""
        coaches = [
            Coach(id="c001", name="William Markus", role="Head Coach", team_id="jaya_jakarta"),
            Coach(id="c002", name="Henry Kusuma Atma", role="Associate Coach", team_id="jaya_jakarta"),
            Coach(id="c003", name="Maya Angelina", role="Associate Coach", team_id="jaya_jakarta"),
            Coach(id="c004", name="Brenda Gunawan", role="Assistant Coach", team_id="jaya_jakarta"),
        ]
        
        athletes = [
            Athlete(id="a001", name="Aryasena Sukma", positions=[Position.POINT_GUARD], team_id="jaya_jakarta"),
            Athlete(id="a002", name="Benjamin Theo", positions=[Position.POINT_GUARD, Position.SHOOTING_GUARD], team_id="jaya_jakarta"),
            Athlete(id="a003", name="Brandon Hartono", positions=[Position.SMALL_FORWARD, Position.POWER_FORWARD], team_id="jaya_jakarta"),
            Athlete(id="a004", name="I Gusti Narendra", positions=[Position.POWER_FORWARD, Position.CENTER], team_id="jaya_jakarta"),
            Athlete(id="a005", name="James Kevin", positions=[Position.SMALL_FORWARD, Position.POWER_FORWARD], team_id="jaya_jakarta"),
            Athlete(id="a006", name="Julian Nathaniel", positions=[Position.POINT_GUARD, Position.POWER_FORWARD], team_id="jaya_jakarta"),
            Athlete(id="a007", name="Leonardo Darwin", positions=[Position.SHOOTING_GUARD, Position.SMALL_FORWARD], team_id="jaya_jakarta"),
            Athlete(id="a008", name="Owen Xaverius", positions=[Position.POINT_GUARD, Position.SHOOTING_GUARD], team_id="jaya_jakarta"),
            Athlete(id="a009", name="Pieter Solomon", positions=[Position.SHOOTING_GUARD], team_id="jaya_jakarta"),
            Athlete(id="a010", name="Satrio Mahatma", positions=[Position.SMALL_FORWARD, Position.POWER_FORWARD], team_id="jaya_jakarta"),
            Athlete(id="a011", name="Theodore Malawi", positions=[Position.CENTER], team_id="jaya_jakarta"),
        ]
        
        team = Team(
            id="jaya_jakarta",
            name="Jaya Jakarta Basketball",
            coaches=coaches,
            athletes=athletes
        )
        
        return team
    
    @pytest.fixture
    def mock_training_sessions(self):
        """Create mock training sessions for January week 1"""
        # Monday Morning (January 1)
        monday_morning = TrainingSession(
            id="ts001",
            team_id="jaya_jakarta",
            date=datetime.date(2024, 1, 1),
            start_time=datetime.time(7, 0),
            end_time=datetime.time(10, 0),
            time_slot="Morning",
            location="Jakarta Training Center",
            activities=[
                TrainingActivity(name="Warming Up", duration_minutes=30, 
                                description="Stretching, Light Jogging, Dynamic warm ups"),
                TrainingActivity(name="Main Training", duration_minutes=120, 
                                description="Shooting drills, 2 vs 3, 3 on 3, 5 on 5, Offense to Defense switch, Free Throw Session"),
                TrainingActivity(name="Cooling Down", duration_minutes=30, 
                                description="Leg hanging, stretching")
            ],
            coach_ids=["c001", "c002", "c004"],  # William, Henry, Bendra
            feedback=Feedback(
                overall_rating=4,
                intensity_rating=4,
                quality_rating=4,
                notes="- No injury recorded\n- Excessive soreness (Brandon Hartono & Leonardo Darwin)\n- Full monitor on Pieter's endurance\n- Add of position Julian Nathaniel (add SF) and Leonardo Darwin (add PF)",
                post_training_summary="everyone inputted from average to good."
            )
        )
        
        # Monday Night (January 1)
        monday_night = TrainingSession(
            id="ts002",
            team_id="jaya_jakarta",
            date=datetime.date(2024, 1, 1),
            start_time=datetime.time(18, 0),
            end_time=datetime.time(21, 0),
            time_slot="Night",
            location="Jakarta Training Center",
            activities=[
                TrainingActivity(name="Warming Up", duration_minutes=30, 
                                description="Stretching, Light Jogging, Dynamic warm ups"),
                TrainingActivity(name="Main Training", duration_minutes=120, 
                                description="Shooting drills, 5 on 5 (reach 7 points, then switch), Offense to Defense switch, Three point session, Positional defense, Free Throw Session"),
                TrainingActivity(name="Cooling Down", duration_minutes=30, 
                                description="Leg hanging, stretching")
            ],
            coach_ids=["c001", "c002", "c003", "c004"],  # William, Henry, Maya, Brenda
            feedback=Feedback(
                overall_rating=4,
                intensity_rating=5,
                quality_rating=4,
                notes="- No injury recorded\n- Excessive soreness (Julian Nathaniel, Pieter Solomon, and Leonardo Darwin)\n- Full monitor on James' ankle (sprained while jumping)\n- Monitor Benjamin's performance (unfocus sometimes)",
                post_training_summary="everyone inputted from average to good except Julian (just his body fitness seems a falling a little from fit after training)"
            )
        )
        
        # Tuesday Morning (January 2)
        tuesday_morning = TrainingSession(
            id="ts003",
            team_id="jaya_jakarta",
            date=datetime.date(2024, 1, 2),
            start_time=datetime.time(7, 0),
            end_time=datetime.time(10, 0),
            time_slot="Morning",
            location="Jakarta Training Center",
            activities=[
                TrainingActivity(name="Warming Up", duration_minutes=30, 
                                description="Stretching, Light Jogging, Dynamic warm ups"),
                TrainingActivity(name="Main Training", duration_minutes=120, 
                                description="Shooting drills, 3 on 3, Free Throw Session"),
                TrainingActivity(name="Cooling Down", duration_minutes=30, 
                                description="Leg hanging, stretching")
            ],
            coach_ids=["c001", "c002", "c004"],  # William, Henry, Bendra
            feedback=Feedback(
                overall_rating=3,
                intensity_rating=3,
                quality_rating=3,
                notes="- No injury recorded\n- Training focuses on physical recovery\n- Athletes' overall endurance are declining a little",
                post_training_summary="everyone inputted average"
            )
        )
        
        # Tuesday Night (January 2)
        tuesday_night = TrainingSession(
            id="ts004",
            team_id="jaya_jakarta",
            date=datetime.date(2024, 1, 2),
            start_time=datetime.time(17, 0),
            end_time=datetime.time(20, 0),
            time_slot="Night",
            location="Jakarta Training Center",
            activities=[
                TrainingActivity(name="Warming Up", duration_minutes=30, 
                                description="Stretching, Light Jogging, Dynamic warm ups"),
                TrainingActivity(name="Main Training", duration_minutes=120, 
                                description="Shooting drills, 2 vs 3, 3 on 3, 5 on 5, Offense to Defense switch, Free Throw Session"),
                TrainingActivity(name="Cooling Down", duration_minutes=30, 
                                description="Leg hanging, stretching")
            ],
            coach_ids=["c001", "c002", "c004"],  # William, Henry, Bendra
            feedback=Feedback(
                overall_rating=4,
                intensity_rating=4,
                quality_rating=5,
                notes="- No injury recorded\n- Everyone is performing well",
                post_training_summary="everyone inputted from good."
            )
        )
        
        # Wednesday Morning (January 3)
        wednesday_morning = TrainingSession(
            id="ts005",
            team_id="jaya_jakarta",
            date=datetime.date(2024, 1, 3),
            start_time=datetime.time(7, 0),
            end_time=datetime.time(10, 0),
            time_slot="Morning",
            location="Jakarta Training Center",
            coach_ids=["c001", "c002", "c003", "c004"],  # All coaches
            feedback=Feedback(
                overall_rating=4,
                intensity_rating=4,
                quality_rating=4,
                notes="",
                post_training_summary=""
            )
        )
        
        # Wednesday Night (January 3)
        wednesday_night = TrainingSession(
            id="ts006",
            team_id="jaya_jakarta",
            date=datetime.date(2024, 1, 3),
            start_time=datetime.time(18, 0),
            end_time=datetime.time(21, 0),
            time_slot="Night",
            location="Jakarta Training Center",
            coach_ids=["c001", "c002", "c003", "c004"],  # All coaches
            feedback=Feedback(
                overall_rating=4,
                intensity_rating=4,
                quality_rating=4,
                notes="",
                post_training_summary=""
            )
        )
        
        # Friday Morning (January 5)
        friday_morning = TrainingSession(
            id="ts007",
            team_id="jaya_jakarta",
            date=datetime.date(2024, 1, 5),
            start_time=datetime.time(7, 0),
            end_time=datetime.time(10, 0),
            time_slot="Morning",
            location="Jakarta Training Center",
            coach_ids=["c001", "c002", "c003", "c004"],  # All coaches
            feedback=Feedback(
                overall_rating=3,
                intensity_rating=4,
                quality_rating=4,
                notes="Body fitness issues reported by some athletes",
                post_training_summary="Some athletes are filling the training sessions as really bad (body fitness) but the training quality is good"
            )
        )
        
        # Friday Night (January 5)
        friday_night = TrainingSession(
            id="ts008",
            team_id="jaya_jakarta",
            date=datetime.date(2024, 1, 5),
            start_time=datetime.time(18, 0),
            end_time=datetime.time(21, 0),
            time_slot="Night",
            location="Jakarta Training Center",
            coach_ids=["c001", "c002", "c003"],  # Brenda cannot attend
            feedback=Feedback(
                overall_rating=4,
                intensity_rating=4,
                quality_rating=4,
                notes="",
                post_training_summary=""
            )
        )
        
        # Saturday Morning (January 6)
        saturday_morning = TrainingSession(
            id="ts009",
            team_id="jaya_jakarta",
            date=datetime.date(2024, 1, 6),
            start_time=datetime.time(7, 0),
            end_time=datetime.time(10, 0),
            time_slot="Morning",
            location="Jakarta Training Center",
            coach_ids=["c001", "c002", "c003", "c004"],  # All coaches
            feedback=Feedback(
                overall_rating=4,
                intensity_rating=4,
                quality_rating=4,
                notes="",
                post_training_summary=""
            )
        )
        
        # Saturday Night (January 6)
        saturday_night = TrainingSession(
            id="ts010",
            team_id="jaya_jakarta",
            date=datetime.date(2024, 1, 6),
            start_time=datetime.time(18, 0),
            end_time=datetime.time(21, 0),
            time_slot="Night",
            location="Jakarta Training Center",
            coach_ids=["c001", "c002", "c003", "c004"],  # All coaches
            feedback=Feedback(
                overall_rating=4,
                intensity_rating=5,
                quality_rating=5,
                notes="",
                post_training_summary=""
            )
        )
        
        return [
            monday_morning, monday_night, 
            tuesday_morning, tuesday_night,
            wednesday_morning, wednesday_night,
            friday_morning, friday_night,
            saturday_morning, saturday_night
        ]
    
    @pytest.fixture
    def mock_attendance_data(self):
        """Create mock attendance data for the training sessions"""
        attendance_data = []
        
        # All athletes present for Monday Morning
        for athlete_id in [f"a{str(i).zfill(3)}" for i in range(1, 12)]:
            attendance_data.append(
                Attendance(
                    session_id="ts001",
                    athlete_id=athlete_id,
                    status="present",
                    notes=""
                )
            )
        
        # All athletes present for Monday Night
        for athlete_id in [f"a{str(i).zfill(3)}" for i in range(1, 12)]:
            attendance_data.append(
                Attendance(
                    session_id="ts002",
                    athlete_id=athlete_id,
                    status="present",
                    notes=""
                )
            )
        
        # All athletes present for Tuesday sessions
        for session_id in ["ts003", "ts004"]:
            for athlete_id in [f"a{str(i).zfill(3)}" for i in range(1, 12)]:
                attendance_data.append(
                    Attendance(
                        session_id=session_id,
                        athlete_id=athlete_id,
                        status="present",
                        notes=""
                    )
                )
        
        # Wednesday morning: Satrio, Owen, and James absent
        absent_athletes = ["a005", "a008", "a010"]  # James, Owen, Satrio
        for athlete_id in [f"a{str(i).zfill(3)}" for i in range(1, 12)]:
            status = "absent" if athlete_id in absent_athletes else "present"
            notes = "Educational purpose" if athlete_id in absent_athletes else ""
            attendance_data.append(
                Attendance(
                    session_id="ts005",
                    athlete_id=athlete_id,
                    status=status,
                    notes=notes
                )
            )
        
        # All athletes present for remaining sessions
        for session_id in ["ts006", "ts007", "ts008", "ts009", "ts010"]:
            for athlete_id in [f"a{str(i).zfill(3)}" for i in range(1, 12)]:
                attendance_data.append(
                    Attendance(
                        session_id=session_id,
                        athlete_id=athlete_id,
                        status="present",
                        notes=""
                    )
                )
        
        return attendance_data
    
    @pytest.fixture
    def mock_services(self, mock_team_data, mock_training_sessions, mock_attendance_data):
        """Create mock services with pre-loaded data"""
        # Create mock services
        team_service = MagicMock(spec=TeamService)
        training_service = MagicMock(spec=TrainingService)
        feedback_service = MagicMock(spec=FeedbackService)
        attendance_service = MagicMock(spec=AttendanceService)
        
        # Configure mock services
        team_service.get_team.return_value = mock_team_data
        team_service.get_coaches.return_value = mock_team_data.coaches
        team_service.get_athletes.return_value = mock_team_data.athletes
        
        training_service.get_training_sessions.return_value = mock_training_sessions
        
        def get_training_session_by_id(session_id):
            return next((session for session in mock_training_sessions if session.id == session_id), None)
        
        training_service.get_training_session.side_effect = get_training_session_by_id
        
        def get_sessions_by_date_range(start_date, end_date):
            return [
                session for session in mock_training_sessions 
                if start_date <= session.date <= end_date
            ]
        
        training_service.get_sessions_by_date_range.side_effect = get_sessions_by_date_range
        
        def get_attendance_by_session(session_id):
            return [a for a in mock_attendance_data if a.session_id == session_id]
        
        attendance_service.get_attendance_by_session.side_effect = get_attendance_by_session
        
        def get_attendance_by_athlete(athlete_id):
            return [a for a in mock_attendance_data if a.athlete_id == athlete_id]
        
        attendance_service.get_attendance_by_athlete.side_effect = get_attendance_by_athlete
        
        def get_feedback_by_session(session_id):
            session = get_training_session_by_id(session_id)
            return session.feedback if session else None
        
        feedback_service.get_feedback_by_session.side_effect = get_feedback_by_session
        
        return {
            "team_service": team_service,
            "training_service": training_service,
            "feedback_service": feedback_service,
            "attendance_service": attendance_service
        }
    
    def test_team_composition(self, mock_services):
        """Test that the team has the correct composition of coaches and athletes"""
        team_service = mock_services["team_service"]
        
        # Test team details
        team = team_service.get_team()
        assert team.name == "Jaya Jakarta Basketball"
        
        # Test coaches count and roles
        coaches = team_service.get_coaches()
        assert len(coaches) == 4
        
        head_coaches = [c for c in coaches if c.role == "Head Coach"]
        assert len(head_coaches) == 1
        assert head_coaches[0].name == "William Markus"
        
        # Test athletes count
        athletes = team_service.get_athletes()
        assert len(athletes) == 11
        
        # Test positions
        point_guards = [a for a in athletes if Position.POINT_GUARD in a.positions]
        assert len(point_guards) == 4
        
        centers = [a for a in athletes if Position.CENTER in a.positions]
        assert len(centers) == 2
        assert "Theodore Malawi" in [c.name for c in centers]
        assert "I Gusti Narendra" in [c.name for c in centers]
    
    def test_training_schedule_january_week1(self, mock_services):
        """Test the training schedule for January Week 1"""
        training_service = mock_services["training_service"]
        
        # Get all training sessions for week 1
        start_date = datetime.date(2024, 1, 1)  # Monday, January 1
        end_date = datetime.date(2024, 1, 7)    # Sunday, January 7
        
        sessions = training_service.get_sessions_by_date_range(start_date, end_date)
        
        # Test total sessions in week 1
        assert len(sessions) == 10
        
        # Test distribution of sessions
        morning_sessions = [s for s in sessions if s.time_slot == "Morning"]
        night_sessions = [s for s in sessions if s.time_slot == "Night"]
        
        assert len(morning_sessions) == 5
        assert len(night_sessions) == 5
        
        # Test specific date
        monday_sessions = [s for s in sessions if s.date == datetime.date(2024, 1, 1)]
        assert len(monday_sessions) == 2
        
        # Test that there are no sessions on Sunday (Jan 7)
        sunday_sessions = [s for s in sessions if s.date == datetime.date(2024, 1, 7)]
        assert len(sunday_sessions) == 0
        
        # Test that there are no sessions on Thursday (Jan 4)
        thursday_sessions = [s for s in sessions if s.date == datetime.date(2024, 1, 4)]
        assert len(thursday_sessions) == 0
    
    def test_coach_attendance(self, mock_services):
        """Test coach attendance for specific sessions"""
        training_service = mock_services["training_service"]
        team_service = mock_services["team_service"]
        
        coaches = team_service.get_coaches()
        coach_dict = {coach.id: coach for coach in coaches}
        
        # Test Monday morning session - William, Henry, Brenda
        monday_morning = training_service.get_training_session("ts001")
        assert len(monday_morning.coach_ids) == 3
        assert "c001" in monday_morning.coach_ids  # William
        assert "c002" in monday_morning.coach_ids  # Henry
        assert "c004" in monday_morning.coach_ids  # Brenda
        assert "c003" not in monday_morning.coach_ids  # Maya not present
        
        # Test Monday night session - All coaches
        monday_night = training_service.get_training_session("ts002")
        assert len(monday_night.coach_ids) == 4
        assert all(coach_id in monday_night.coach_ids for coach_id in ["c001", "c002", "c003", "c004"])
        
        # Test Friday night session - Brenda absent
        friday_night = training_service.get_training_session("ts008")
        assert len(friday_night.coach_ids) == 3
        assert "c001" in friday_night.coach_ids  # William
        assert "c002" in friday_night.coach_ids  # Henry
        assert "c003" in friday_night.coach_ids  # Maya
        assert "c004" not in friday_night.coach_ids  # Brenda not present
        
        # Test Saturday night session - All coaches
        saturday_night = training_service.get_training_session("ts010")
        assert len(saturday_night.coach_ids) == 4
        assert all(coach_id in saturday_night.coach_ids for coach_id in ["c001", "c002", "c003", "c004"])
    
    def test_athlete_attendance(self, mock_services):
        """Test athlete attendance for specific sessions"""
        attendance_service = mock_services["attendance_service"]
        team_service = mock_services["team_service"]
        
        athletes = team_service.get_athletes()
        athlete_dict = {athlete.id: athlete for athlete in athletes}
        
        # Test Monday morning - all athletes present
        monday_morning_attendance = attendance_service.get_attendance_by_session("ts001")
        assert len(monday_morning_attendance) == 11  # All 11 athletes
        assert all(a.status == "present" for a in monday_morning_attendance)
        
        # Test Wednesday morning - 3 athletes absent
        wednesday_morning_attendance = attendance_service.get_attendance_by_session("ts005")
        
        present_athletes = [a for a in wednesday_morning_attendance if a.status == "present"]
        absent_athletes = [a for a in wednesday_morning_attendance if a.status == "absent"]
        
        assert len(present_athletes) == 8
        assert len(absent_athletes) == 3
        
        # Check specific athletes who were absent
        absent_ids = [a.athlete_id for a in absent_athletes]
        assert "a005" in absent_ids  # James
        assert "a008" in absent_ids  # Owen
        assert "a010" in absent_ids  # Satrio
        
        # Check reason for absence
        for attendance in absent_athletes:
            assert attendance.notes == "Educational purpose"
        
        # Test that Satrio was absent only for Wednesday morning
        satrio_attendance = attendance_service.get_attendance_by_athlete("a010")
        assert len(satrio_attendance) == 10  # Should have records for all 10 sessions
        
        satrio_absences = [a for a in satrio_attendance if a.status == "absent"]
        assert len(satrio_absences) == 1
        assert satrio_absences[0].session_id == "ts005"  # Wednesday morning
    
    def test_training_ratings(self, mock_services):
        """Test the ratings and feedback for training sessions"""
        feedback_service = mock_services["feedback_service"]
        
        # Test Monday morning session ratings
        monday_morning_feedback = feedback_service.get_feedback_by_session("ts001")
        assert monday_morning_feedback.overall_rating == 4
        assert monday_morning_feedback.intensity_rating == 4
        assert monday_morning_feedback.quality_rating == 4
        
        # Test Tuesday morning session ratings (recovery focused)
        tuesday_morning_feedback = feedback_service.get_feedback_by_session("ts003")
        assert tuesday_morning_feedback.overall_rating == 3
        assert tuesday_morning_feedback.intensity_rating == 3
        assert tuesday_morning_feedback.quality_rating == 3
        assert "physical recovery" in tuesday_morning_feedback.notes
        
        # Test Friday morning session with body fitness issues
        friday_morning_feedback = feedback_service.get_feedback_by_session("ts007")
        assert "body fitness" in friday_morning_feedback.post_training_summary.lower()
        
        # Test best quality session
        tuesday_night_feedback = feedback_service.get_feedback_by_session("ts004")
        assert tuesday_night_feedback.quality_rating == 5
        assert "performing well" in tuesday_night_feedback.notes
    
    def test_athlete_issues_tracking(self, mock_services):
        """Test tracking of athlete issues like injuries, soreness, etc."""
        feedback_service = mock_services["feedback_service"]
        
        # Monday morning - Brandon & Leonardo excessive soreness, Pieter endurance
        monday_morning_feedback = feedback_service.get_feedback_by_session("ts001")
        assert "Brandon Hartono" in monday_morning_feedback.notes
        assert "Leonardo Darwin" in monday_morning_feedback.notes
        assert "Pieter's endurance" in monday_morning_feedback.notes
        
        # Monday night - James ankle sprain, Benjamin focus issues
        monday_night_feedback = feedback_service.get_feedback_by_session("ts002")
        assert "James' ankle" in monday_night_feedback.notes
        assert "sprained" in monday_night_feedback.notes
        assert "Benjamin's performance" in monday_night_feedback.notes
        assert "unfocus" in monday_night_feedback.notes
    
    def test_position_updates(self, mock_services):
        """Test tracking position updates for athletes"""
        feedback_service = mock_services["feedback_service"]
        
        # Monday morning - Julian added SF, Leonardo added PF
        monday_morning_feedback = feedback_service.get_feedback_by_session("ts001")
        assert "Julian Nathaniel (add SF)" in monday_morning_feedback.notes
        assert "Leonardo Darwin (add PF)" in monday_morning_feedback.notes
    
    def test_training_activity_duration(self, mock_services):
        """Test that training activities have appropriate durations"""
        training_service = mock_services["training_service"]
        
        # Monday morning session - check structure and duration
        monday_morning = training_service.get_training_session("ts001")
        activities = monday_morning.activities
        
        # Check total duration
        total_duration = sum(activity.duration_minutes for activity in activities)
        assert total_duration == 180  # 3 hours = 180 minutes
        
        # Check individual components
        assert len(activities) == 3
        
        warm_up = next((a for a in activities if a.name == "Warming Up"), None)
        main_training = next((a for a in activities if a.name == "Main Training"), None)
        cool_down = next((a for a in activities if a.name == "Cooling Down"), None)
        
        assert warm_up and warm_up.duration_minutes == 30
        assert main_training and main_training.duration_minutes == 120
        assert cool_down and cool_down.duration_minutes == 30
        
        # Check activity content
        assert "Stretching" in warm_up.description
        assert "Shooting drills" in main_training.description
        assert "stretching" in cool_down.description.lower()
    
    def test_generate_weekly_report(self, mock_services):
        """Test generating a weekly training report"""
        team_service = mock_services["team_service"]
        training_service = mock_services["training_service"]
        attendance_service = mock_services["attendance_service"]
        feedback_service = mock_services["feedback_service"]
        
        # Helper method to generate a weekly report
        def generate_weekly_report(start_date, end_date):
            """Generate a weekly report from the services"""
            sessions = training_service.get_sessions_by_date_range(start_date, end_date)
            
            # Gather metrics
            total_sessions = len(sessions)
            total_hours = sum((s.end_time.hour - s.start_time.hour) for s in sessions)
            
            avg_overall_rating = sum(s.feedback.overall_rating for s in sessions) / total_sessions if total_sessions > 0 else 0
            avg_intensity_rating = sum(s.feedback.intensity_rating for s in sessions) / total_sessions if total_sessions > 0 else 0
            avg_quality_rating = sum(s.feedback.quality_rating for s in sessions) / total_sessions if total_sessions > 0 else 0
            
            # Gather attendance data
            attendance_data = []
            for session in sessions:
                attendance = attendance_service.get_attendance_by_session(session.id)
                attendance_data.extend(attendance)
            
            attendance_by_athlete = {}
            for athlete in team_service.get_athletes():
                athlete_attendance = [a for a in attendance_data if a.athlete_id == athlete.id]
                present_count = len([a for a in athlete_attendance if a.status == "present"])
                total_count = len(athlete_attendance)
                attendance_rate = (present_count / total_count) * 100 if total_count > 0 else 0
                
                attendance_by_athlete[athlete.id] = {
                    "name": athlete.name,
                    "present": present_count,
                    "total": total_count,
                    "rate": attendance_rate
                }
            
            # Return the report data
            return {
                "date_range": f"{start_date} to {end_date}",
                "total_sessions": total_sessions,
                "total_hours": total_hours,
                "average_ratings": {
                    "overall": avg_overall_rating,
                    "intensity": avg_intensity_rating,
                    "quality": avg_quality_rating
                },
                "attendance": attendance_by_athlete,
                "issues_noted": [
                    note for session in sessions 
                    if session.feedback and session.feedback.notes
                    for note in session.feedback.notes.split('\n') if note.strip()
                ]
            }
        
        # Generate week 1 report
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 7)
        
        report = generate_weekly_report(start_date, end_date)
        
        # Test the report data
        assert report["total_sessions"] == 10
        assert report["total_hours"] == 30  # 10 sessions x 3 hours
        
        # Check ratings
        assert 3.5 <= report["average_ratings"]["overall"] <= 4.5
        assert 4.0 <= report["average_ratings"]["intensity"] <= 4.5
        assert 4.0 <= report["average_ratings"]["quality"] <= 4.5
        
        # Check attendance rates
        # Athletes who missed Wednesday morning should have ~90% attendance
        for athlete_id in ["a005", "a008", "a010"]:  # James, Owen, Satrio
            assert report["attendance"][athlete_id]["rate"] == 90.0
        
        # Other athletes should have 100% attendance
        for athlete_id in ["a001", "a002", "a003", "a004", "a006", "a007", "a009", "a011"]:
            assert report["attendance"][athlete_id]["rate"] == 100.0
        
        # Check that issues were tracked
        issues = report["issues_noted"]
        assert any("James' ankle" in issue for issue in issues)
        assert any("body fitness" in issue.lower() for issue in issues)
        assert any("Benjamin's performance" in issue for issue in issues)
        
    def test_coach_involvement_stats(self, mock_services):
        """Test calculating coach involvement statistics"""
        training_service = mock_services["training_service"]
        team_service = mock_services["team_service"]
        
        # Get all training sessions for week 1
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 7)
        
        sessions = training_service.get_sessions_by_date_range(start_date, end_date)
        
        # Calculate coach attendance
        coaches = team_service.get_coaches()
        coach_attendance = {}
        
        for coach in coaches:
            attended_sessions = [s for s in sessions if coach.id in s.coach_ids]
            attendance_rate = (len(attended_sessions) / len(sessions)) * 100 if sessions else 0
            
            coach_attendance[coach.id] = {
                "name": coach.name,
                "role": coach.role,
                "sessions_attended": len(attended_sessions),
                "total_sessions": len(sessions),
                "attendance_rate": attendance_rate
            }
        
        # William and Henry should have 100% attendance
        assert coach_attendance["c001"]["attendance_rate"] == 100.0  # William
        assert coach_attendance["c002"]["attendance_rate"] == 100.0  # Henry
        
        # Brenda missed Friday night session
        assert coach_attendance["c004"]["attendance_rate"] == 90.0  # Brenda
        
        # Calculate sessions with all coaches present
        all_coaches_present = [
            s for s in sessions 
            if all(coach.id in s.coach_ids for coach in coaches)
        ]
        
        # Monday night, Wednesday morning/night, Saturday morning/night should have all coaches
        assert len(all_coaches_present) == 5 