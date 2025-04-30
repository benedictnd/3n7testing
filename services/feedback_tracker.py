from typing import Dict, List, Any, Optional, Tuple
import datetime
import math
import statistics
from enum import Enum

from models.drill import DrillResult, SuccessMetric


class FeedbackType(str, Enum):
    """Types of feedback that can be provided during training"""
    TECHNICAL = "technical"
    TACTICAL = "tactical"
    PHYSICAL = "physical"
    MENTAL = "mental"
    GENERAL = "general"


class PerformanceAlert(str, Enum):
    """Performance alert levels"""
    CRITICAL = "critical"  # Major issue requiring immediate attention
    WARNING = "warning"    # Potential issue to monitor
    POSITIVE = "positive"  # Exceptional performance
    INFO = "info"          # General information


class DrillPerformanceTracker:
    """
    Tracks real-time performance of athletes during drills and provides feedback
    """
    
    def __init__(self, drill_id: str, athlete_ids: List[str], baseline_data: Optional[Dict[str, Any]] = None):
        """
        Initialize tracker for a specific drill
        
        Args:
            drill_id: The ID of the drill being tracked
            athlete_ids: List of athlete IDs participating in the drill
            baseline_data: Optional baseline performance data for comparison
        """
        self.drill_id = drill_id
        self.athlete_ids = athlete_ids
        self.baseline_data = baseline_data or {}
        self.start_time = datetime.datetime.now()
        self.end_time = None
        
        # Initialize tracking structures
        self.metrics: Dict[str, Dict[str, List[float]]] = {
            athlete_id: {} for athlete_id in athlete_ids
        }
        
        # Feedback storage
        self.feedback: Dict[str, List[Dict[str, Any]]] = {
            athlete_id: [] for athlete_id in athlete_ids
        }
        
        # Alert history
        self.alerts: Dict[str, List[Dict[str, Any]]] = {
            athlete_id: [] for athlete_id in athlete_ids
        }
    
    def record_metric(self, athlete_id: str, metric_name: str, value: float) -> None:
        """
        Record a performance metric for an athlete
        
        Args:
            athlete_id: Athlete ID
            metric_name: Name of the metric being recorded
            value: The metric value
        """
        if athlete_id not in self.athlete_ids:
            raise ValueError(f"Athlete {athlete_id} is not part of this drill")
            
        # Initialize metric list if this is the first recording
        if metric_name not in self.metrics[athlete_id]:
            self.metrics[athlete_id][metric_name] = []
            
        self.metrics[athlete_id][metric_name].append(value)
        
        # Analyze the latest data point
        self._analyze_latest_metric(athlete_id, metric_name, value)
    
    def _analyze_latest_metric(self, athlete_id: str, metric_name: str, value: float) -> None:
        """
        Analyze the latest metric recording and generate alerts if needed
        
        Args:
            athlete_id: Athlete ID
            metric_name: Name of the metric
            value: The latest value
        """
        # Check if we have baseline data for comparison
        baseline = self.baseline_data.get(athlete_id, {}).get(metric_name)
        
        # Only analyze if we have sufficient data points
        metric_history = self.metrics[athlete_id][metric_name]
        if len(metric_history) < 3:
            return
            
        # Calculate recent trend
        recent_values = metric_history[-3:]
        trend = self._calculate_trend(recent_values)
        
        # Determine if this metric requires attention
        alert = self._check_for_alerts(athlete_id, metric_name, value, trend, baseline)
        if alert:
            self.alerts[athlete_id].append(alert)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calculate the trend from a series of values
        
        Args:
            values: List of recent values
            
        Returns:
            Trend coefficient (positive = improving, negative = declining)
        """
        if len(values) < 2:
            return 0.0
            
        # Simple linear regression slope calculation
        n = len(values)
        x = list(range(1, n + 1))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
            
        return numerator / denominator
    
    def _check_for_alerts(
        self, 
        athlete_id: str, 
        metric_name: str, 
        current_value: float, 
        trend: float, 
        baseline: Optional[float]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if current metrics should trigger alerts
        
        Args:
            athlete_id: Athlete ID
            metric_name: Metric name
            current_value: Current value
            trend: Calculated trend
            baseline: Baseline value (if available)
            
        Returns:
            Alert data if an alert should be raised, None otherwise
        """
        # Examples of alert conditions (these would be customized)
        
        # Check against baseline if available
        if baseline is not None:
            deviation = (current_value - baseline) / baseline
            
            # Critical decline from baseline
            if deviation < -0.25:
                return {
                    "timestamp": datetime.datetime.now(),
                    "athlete_id": athlete_id,
                    "metric": metric_name,
                    "value": current_value,
                    "baseline": baseline,
                    "deviation": deviation,
                    "level": PerformanceAlert.CRITICAL,
                    "message": f"Critical decline in {metric_name}: {current_value:.2f} vs baseline {baseline:.2f} ({deviation:.1%})"
                }
            
            # Significant improvement
            if deviation > 0.20:
                return {
                    "timestamp": datetime.datetime.now(),
                    "athlete_id": athlete_id,
                    "metric": metric_name,
                    "value": current_value,
                    "baseline": baseline,
                    "deviation": deviation,
                    "level": PerformanceAlert.POSITIVE,
                    "message": f"Excellent performance in {metric_name}: {current_value:.2f} vs baseline {baseline:.2f} ({deviation:.1%})"
                }
        
        # Check for concerning trends regardless of baseline
        metric_history = self.metrics[athlete_id][metric_name]
        if len(metric_history) >= 5:
            # Consistent negative trend
            if trend < -0.1 and all(metric_history[-i] <= metric_history[-(i+1)] for i in range(1, 5)):
                return {
                    "timestamp": datetime.datetime.now(),
                    "athlete_id": athlete_id,
                    "metric": metric_name,
                    "value": current_value,
                    "trend": trend,
                    "level": PerformanceAlert.WARNING,
                    "message": f"Declining trend in {metric_name} over last 5 attempts"
                }
        
        return None
    
    def add_feedback(
        self, 
        athlete_id: str, 
        feedback_text: str, 
        feedback_type: FeedbackType = FeedbackType.GENERAL,
        coach_id: Optional[str] = None
    ) -> None:
        """
        Add coaching feedback for an athlete
        
        Args:
            athlete_id: Athlete ID
            feedback_text: The feedback text
            feedback_type: Type of feedback
            coach_id: ID of the coach providing feedback (optional)
        """
        if athlete_id not in self.athlete_ids:
            raise ValueError(f"Athlete {athlete_id} is not part of this drill")
            
        self.feedback[athlete_id].append({
            "timestamp": datetime.datetime.now(),
            "text": feedback_text,
            "type": feedback_type,
            "coach_id": coach_id
        })
    
    def complete_drill(self) -> Dict[str, DrillResult]:
        """
        Complete the drill and generate result summaries
        
        Returns:
            Dictionary of athlete IDs to their DrillResult objects
        """
        self.end_time = datetime.datetime.now()
        duration = (self.end_time - self.start_time).total_seconds() / 60  # Duration in minutes
        
        results = {}
        for athlete_id in self.athlete_ids:
            # Calculate summary statistics for each metric
            metrics_summary = {}
            for metric_name, values in self.metrics[athlete_id].items():
                if not values:
                    continue
                    
                metrics_summary[metric_name] = {
                    "count": len(values),
                    "average": statistics.mean(values) if values else None,
                    "max": max(values) if values else None,
                    "min": min(values) if values else None
                }
                
                # Add standard deviation if we have enough data points
                if len(values) >= 2:
                    metrics_summary[metric_name]["std_dev"] = statistics.stdev(values)
            
            # Collect all feedback
            all_feedback = self.feedback[athlete_id]
            
            # Generate success metrics based on our tracking
            success_metrics = []
            for metric_name, stats in metrics_summary.items():
                if stats["count"] > 0:
                    success_metrics.append(
                        SuccessMetric(
                            name=metric_name,
                            value=stats["average"],
                            context={
                                "count": stats["count"],
                                "min": stats["min"],
                                "max": stats["max"]
                            }
                        )
                    )
            
            # Create the drill result
            results[athlete_id] = DrillResult(
                drill_id=self.drill_id,
                athlete_id=athlete_id,
                completed_at=self.end_time,
                duration_minutes=duration,
                success_metrics=success_metrics,
                feedback=[item["text"] for item in all_feedback],
                performance_data={
                    "metrics": metrics_summary,
                    "alerts": self.alerts[athlete_id],
                    "feedback": all_feedback
                }
            )
        
        return results


class TeamPerformanceTracker:
    """
    Tracks overall team performance across multiple drills
    """
    
    def __init__(self, team_id: str, session_id: str):
        """
        Initialize team performance tracker
        
        Args:
            team_id: Team ID
            session_id: Training session ID
        """
        self.team_id = team_id
        self.session_id = session_id
        self.drill_trackers: Dict[str, DrillPerformanceTracker] = {}
        self.session_start = datetime.datetime.now()
        self.session_end = None
    
    def start_drill(
        self, 
        drill_id: str, 
        athlete_ids: List[str], 
        baseline_data: Optional[Dict[str, Any]] = None
    ) -> DrillPerformanceTracker:
        """
        Start tracking a new drill
        
        Args:
            drill_id: The ID of the drill being tracked
            athlete_ids: List of athlete IDs participating in the drill
            baseline_data: Optional baseline performance data for comparison
            
        Returns:
            The drill tracker instance
        """
        tracker = DrillPerformanceTracker(drill_id, athlete_ids, baseline_data)
        self.drill_trackers[drill_id] = tracker
        return tracker
    
    def get_drill_tracker(self, drill_id: str) -> DrillPerformanceTracker:
        """
        Get tracker for a specific drill
        
        Args:
            drill_id: Drill ID
            
        Returns:
            The drill tracker instance
        """
        if drill_id not in self.drill_trackers:
            raise ValueError(f"No tracker exists for drill {drill_id}")
        return self.drill_trackers[drill_id]
    
    def complete_session(self) -> Dict[str, Any]:
        """
        Complete the session and generate overall summary
        
        Returns:
            Session summary data
        """
        self.session_end = datetime.datetime.now()
        duration = (self.session_end - self.session_start).total_seconds() / 60  # Duration in minutes
        
        # Complete any drills that haven't been completed yet
        completed_drills: Dict[str, Dict[str, DrillResult]] = {}
        for drill_id, tracker in self.drill_trackers.items():
            if not tracker.end_time:
                results = tracker.complete_drill()
                completed_drills[drill_id] = results
            else:
                # If the drill was already completed, just grab its results
                results = {
                    athlete_id: None
                    for athlete_id in tracker.athlete_ids
                }
                for athlete_id in tracker.athlete_ids:
                    # We need to access the actual DrillResult objects here
                    # This would require a bit more structure in the real implementation
                    pass
                completed_drills[drill_id] = results
        
        # Compile athlete session summaries
        athlete_summaries = self._compile_athlete_summaries(completed_drills)
        
        # Overall session summary
        session_summary = {
            "team_id": self.team_id,
            "session_id": self.session_id,
            "start_time": self.session_start,
            "end_time": self.session_end,
            "duration_minutes": duration,
            "drill_count": len(self.drill_trackers),
            "athlete_summaries": athlete_summaries,
            "drill_results": completed_drills,
        }
        
        return session_summary
    
    def _compile_athlete_summaries(
        self, 
        completed_drills: Dict[str, Dict[str, DrillResult]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compile summary statistics for each athlete across all drills
        
        Args:
            completed_drills: Dictionary of drill_id to athlete results
            
        Returns:
            Dictionary of athlete summaries
        """
        # First, collect all athlete IDs
        all_athletes = set()
        for drill_results in completed_drills.values():
            all_athletes.update(drill_results.keys())
        
        # Initialize summaries
        summaries = {athlete_id: {
            "drills_completed": 0,
            "total_duration": 0,
            "feedback_count": 0,
            "alert_counts": {
                PerformanceAlert.CRITICAL: 0,
                PerformanceAlert.WARNING: 0,
                PerformanceAlert.POSITIVE: 0,
                PerformanceAlert.INFO: 0
            },
            "metrics": {}
        } for athlete_id in all_athletes}
        
        # Compile data from each drill
        for drill_id, drill_results in completed_drills.items():
            for athlete_id, result in drill_results.items():
                if not result:
                    continue
                    
                # Update basic counters
                summaries[athlete_id]["drills_completed"] += 1
                summaries[athlete_id]["total_duration"] += result.duration_minutes
                summaries[athlete_id]["feedback_count"] += len(result.feedback)
                
                # Update alert counts
                for alert in result.performance_data.get("alerts", []):
                    level = alert.get("level", PerformanceAlert.INFO)
                    summaries[athlete_id]["alert_counts"][level] += 1
                
                # Aggregate metrics across drills
                for metric in result.success_metrics:
                    metric_name = metric.name
                    if metric_name not in summaries[athlete_id]["metrics"]:
                        summaries[athlete_id]["metrics"][metric_name] = {
                            "values": [],
                            "drills": []
                        }
                    
                    summaries[athlete_id]["metrics"][metric_name]["values"].append(metric.value)
                    summaries[athlete_id]["metrics"][metric_name]["drills"].append(drill_id)
        
        # Calculate averages for metrics
        for athlete_id, summary in summaries.items():
            for metric_name, metric_data in summary["metrics"].items():
                if metric_data["values"]:
                    metric_data["average"] = statistics.mean(metric_data["values"])
                    if len(metric_data["values"]) >= 2:
                        metric_data["std_dev"] = statistics.stdev(metric_data["values"])
        
        return summaries 