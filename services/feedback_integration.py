from typing import Dict, List, Any, Optional, Callable, Union
import json
import asyncio
import logging
import datetime
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass


# Set up logging
logger = logging.getLogger(__name__)


class DataSourceType(str, Enum):
    """Types of data sources for performance tracking"""
    WEARABLE = "wearable"
    CAMERA = "camera"
    MANUAL = "manual"
    SENSOR = "sensor"
    API = "api"


class MetricType(str, Enum):
    """Types of metrics that can be tracked"""
    HEART_RATE = "heart_rate"
    DISTANCE = "distance"
    SPEED = "speed"
    ACCELERATION = "acceleration"
    POWER = "power"
    FORM = "form"
    TECHNIQUE = "technique"
    FATIGUE = "fatigue"
    POSITION = "position"
    CUSTOM = "custom"


@dataclass
class MetricThreshold:
    """Threshold configuration for metric alerts"""
    metric_type: MetricType
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    target_value: Optional[float] = None
    target_range: Optional[tuple] = None
    
    def is_exceeded(self, value: float) -> bool:
        """
        Check if a value exceeds the threshold
        
        Args:
            value: The metric value to check
            
        Returns:
            True if threshold is exceeded, False otherwise
        """
        if self.min_value is not None and value < self.min_value:
            return True
            
        if self.max_value is not None and value > self.max_value:
            return True
            
        if self.target_range is not None:
            min_range, max_range = self.target_range
            if value < min_range or value > max_range:
                return True
                
        return False


class MetricReading:
    """A single reading from a data source"""
    
    def __init__(
        self,
        metric_type: MetricType,
        value: Union[float, str, Dict, List],
        timestamp: Optional[datetime.datetime] = None,
        athlete_id: Optional[str] = None,
        source_id: Optional[str] = None,
        source_type: Optional[DataSourceType] = None,
        confidence: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a metric reading
        
        Args:
            metric_type: Type of metric
            value: Measured value
            timestamp: Time of measurement
            athlete_id: ID of athlete
            source_id: ID of data source
            source_type: Type of data source
            confidence: Confidence level (0-1)
            context: Additional context
        """
        self.metric_type = metric_type
        self.value = value
        self.timestamp = timestamp or datetime.datetime.now()
        self.athlete_id = athlete_id
        self.source_id = source_id
        self.source_type = source_type
        self.confidence = confidence
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary representation
        """
        return {
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "athlete_id": self.athlete_id,
            "source_id": self.source_id,
            "source_type": self.source_type.value if self.source_type else None,
            "confidence": self.confidence,
            "context": self.context
        }


class DataSourceAdapter(ABC):
    """Abstract base class for data source adapters"""
    
    def __init__(
        self,
        source_id: str,
        source_name: str,
        source_type: DataSourceType,
        supported_metrics: List[MetricType]
    ):
        """
        Initialize a data source adapter
        
        Args:
            source_id: Unique ID for the data source
            source_name: Human-readable name
            source_type: Type of data source
            supported_metrics: List of supported metrics
        """
        self.source_id = source_id
        self.source_name = source_name
        self.source_type = source_type
        self.supported_metrics = supported_metrics
        self.connected = False
        self.callbacks: List[Callable[[MetricReading], None]] = []
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the data source
        
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the data source
        
        Returns:
            Success status
        """
        pass
    
    def register_callback(self, callback: Callable[[MetricReading], None]) -> None:
        """
        Register a callback for new readings
        
        Args:
            callback: Function to call with new readings
        """
        self.callbacks.append(callback)
    
    def notify_callbacks(self, reading: MetricReading) -> None:
        """
        Notify all callbacks of a new reading
        
        Args:
            reading: The new metric reading
        """
        for callback in self.callbacks:
            try:
                callback(reading)
            except Exception as e:
                logger.error(f"Error in callback for {self.source_id}: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary representation
        """
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_type": self.source_type.value,
            "supported_metrics": [m.value for m in self.supported_metrics],
            "connected": self.connected
        }


class WebSocketAdapter(DataSourceAdapter):
    """Adapter for WebSocket-based data sources"""
    
    def __init__(
        self,
        source_id: str,
        source_name: str,
        source_type: DataSourceType,
        supported_metrics: List[MetricType],
        websocket_url: str,
        auth_token: Optional[str] = None,
        reconnect_interval: int = 5
    ):
        """
        Initialize a WebSocket adapter
        
        Args:
            source_id: Unique ID for the data source
            source_name: Human-readable name
            source_type: Type of data source
            supported_metrics: List of supported metrics
            websocket_url: URL for WebSocket connection
            auth_token: Authentication token
            reconnect_interval: Reconnection interval in seconds
        """
        super().__init__(source_id, source_name, source_type, supported_metrics)
        self.websocket_url = websocket_url
        self.auth_token = auth_token
        self.reconnect_interval = reconnect_interval
        self.ws = None
        self.running = False
        self.task = None
    
    async def connect(self) -> bool:
        """
        Connect to the WebSocket data source
        
        Returns:
            Success status
        """
        try:
            # Note: In a real implementation, you would use a proper WebSocket library
            # such as websockets or aiohttp
            logger.info(f"Connecting to WebSocket at {self.websocket_url}")
            
            # Simulate connection
            await asyncio.sleep(0.5)
            self.connected = True
            self.running = True
            
            # Start background task to simulate receiving data
            self.task = asyncio.create_task(self._receive_data())
            
            logger.info(f"Connected to {self.source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to {self.source_name}: {str(e)}")
            self.connected = False
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the WebSocket data source
        
        Returns:
            Success status
        """
        try:
            logger.info(f"Disconnecting from {self.source_name}")
            self.running = False
            
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
                self.task = None
            
            # Simulate disconnection
            await asyncio.sleep(0.5)
            self.connected = False
            
            logger.info(f"Disconnected from {self.source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from {self.source_name}: {str(e)}")
            return False
    
    async def _receive_data(self) -> None:
        """Background task to receive and process data"""
        while self.running:
            try:
                # In a real implementation, this would be a proper WebSocket receive
                # Simulating data reception
                await asyncio.sleep(1)
                
                # Process the received data (simulated)
                for metric in self.supported_metrics:
                    # Generate sample data based on metric type
                    if metric == MetricType.HEART_RATE:
                        value = 120 + (asyncio.get_event_loop().time() % 20)
                    elif metric == MetricType.SPEED:
                        value = 5 + (asyncio.get_event_loop().time() % 5)
                    elif metric == MetricType.DISTANCE:
                        value = asyncio.get_event_loop().time() * 2 % 100
                    else:
                        value = asyncio.get_event_loop().time() % 10
                    
                    # Create a reading
                    reading = MetricReading(
                        metric_type=metric,
                        value=value,
                        source_id=self.source_id,
                        source_type=self.source_type,
                        confidence=0.95,
                        context={"simulated": True}
                    )
                    
                    # Notify callbacks
                    self.notify_callbacks(reading)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error receiving data from {self.source_name}: {str(e)}")
                await asyncio.sleep(self.reconnect_interval)


class HTTPAPIAdapter(DataSourceAdapter):
    """Adapter for HTTP API-based data sources"""
    
    def __init__(
        self,
        source_id: str,
        source_name: str,
        source_type: DataSourceType,
        supported_metrics: List[MetricType],
        api_base_url: str,
        poll_interval: int = 60,
        auth_token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize an HTTP API adapter
        
        Args:
            source_id: Unique ID for the data source
            source_name: Human-readable name
            source_type: Type of data source
            supported_metrics: List of supported metrics
            api_base_url: Base URL for API
            poll_interval: Polling interval in seconds
            auth_token: Authentication token
            headers: Additional HTTP headers
        """
        super().__init__(source_id, source_name, source_type, supported_metrics)
        self.api_base_url = api_base_url
        self.poll_interval = poll_interval
        self.auth_token = auth_token
        self.headers = headers or {}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        self.running = False
        self.task = None
    
    async def connect(self) -> bool:
        """
        Connect to the HTTP API data source
        
        Returns:
            Success status
        """
        try:
            logger.info(f"Connecting to API at {self.api_base_url}")
            
            # Validate connection with a test request
            # In a real implementation, this would be an actual HTTP request
            await asyncio.sleep(0.5)
            
            self.connected = True
            self.running = True
            
            # Start background task to poll for data
            self.task = asyncio.create_task(self._poll_data())
            
            logger.info(f"Connected to {self.source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to {self.source_name}: {str(e)}")
            self.connected = False
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the HTTP API data source
        
        Returns:
            Success status
        """
        try:
            logger.info(f"Disconnecting from {self.source_name}")
            self.running = False
            
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
                self.task = None
            
            self.connected = False
            
            logger.info(f"Disconnected from {self.source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from {self.source_name}: {str(e)}")
            return False
    
    async def _poll_data(self) -> None:
        """Background task to poll for data"""
        while self.running:
            try:
                # In a real implementation, this would be actual HTTP requests
                # to the API endpoints for each metric
                await asyncio.sleep(self.poll_interval)
                
                # Simulate API responses for each metric
                for metric in self.supported_metrics:
                    # Simulate data based on metric type
                    if metric == MetricType.HEART_RATE:
                        value = 120 + (asyncio.get_event_loop().time() % 20)
                    elif metric == MetricType.SPEED:
                        value = 5 + (asyncio.get_event_loop().time() % 5)
                    elif metric == MetricType.DISTANCE:
                        value = asyncio.get_event_loop().time() * 2 % 100
                    else:
                        value = asyncio.get_event_loop().time() % 10
                    
                    # Create readings
                    # In a real implementation, this would parse actual API responses
                    reading = MetricReading(
                        metric_type=metric,
                        value=value,
                        source_id=self.source_id,
                        source_type=self.source_type,
                        confidence=0.9,
                        context={"simulated": True, "api_poll": True}
                    )
                    
                    # Notify callbacks
                    self.notify_callbacks(reading)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error polling data from {self.source_name}: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying


class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class FeedbackAlert:
    """A feedback alert generated from metric data"""
    
    def __init__(
        self,
        alert_id: str,
        level: AlertLevel,
        message: str,
        metric_reading: MetricReading,
        threshold: Optional[MetricThreshold] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        timestamp: Optional[datetime.datetime] = None
    ):
        """
        Initialize a feedback alert
        
        Args:
            alert_id: Unique alert ID
            level: Alert severity level
            message: Alert message
            metric_reading: Related metric reading
            threshold: Related threshold if applicable
            actions: Suggested actions
            timestamp: Alert timestamp
        """
        self.alert_id = alert_id
        self.level = level
        self.message = message
        self.metric_reading = metric_reading
        self.threshold = threshold
        self.actions = actions or []
        self.timestamp = timestamp or datetime.datetime.now()
        self.acknowledged = False
        self.acknowledged_by = None
        self.acknowledged_at = None
    
    def acknowledge(self, user_id: str) -> None:
        """
        Acknowledge the alert
        
        Args:
            user_id: ID of acknowledging user
        """
        self.acknowledged = True
        self.acknowledged_by = user_id
        self.acknowledged_at = datetime.datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary representation
        """
        return {
            "alert_id": self.alert_id,
            "level": self.level.value,
            "message": self.message,
            "metric_reading": self.metric_reading.to_dict(),
            "threshold": self.threshold.__dict__ if self.threshold else None,
            "actions": self.actions,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }


class FeedbackManager:
    """
    Manager for real-time feedback from performance tracking systems
    """
    
    def __init__(self):
        """Initialize the feedback manager"""
        self.data_sources: Dict[str, DataSourceAdapter] = {}
        self.thresholds: Dict[str, List[MetricThreshold]] = {}
        self.alerts: List[FeedbackAlert] = []
        self.alert_callbacks: List[Callable[[FeedbackAlert], None]] = []
        self.readings_buffer: Dict[str, List[MetricReading]] = {}
        self.max_buffer_size = 1000
    
    def register_data_source(self, source: DataSourceAdapter) -> None:
        """
        Register a data source
        
        Args:
            source: Data source adapter
        """
        if source.source_id in self.data_sources:
            raise ValueError(f"Data source with ID {source.source_id} already registered")
        
        self.data_sources[source.source_id] = source
        source.register_callback(self._handle_metric_reading)
        self.readings_buffer[source.source_id] = []
    
    def unregister_data_source(self, source_id: str) -> bool:
        """
        Unregister a data source
        
        Args:
            source_id: ID of data source to unregister
            
        Returns:
            Success status
        """
        if source_id not in self.data_sources:
            return False
        
        del self.data_sources[source_id]
        return True
    
    async def connect_all_sources(self) -> Dict[str, bool]:
        """
        Connect to all registered data sources
        
        Returns:
            Dictionary of connection results
        """
        results = {}
        for source_id, source in self.data_sources.items():
            results[source_id] = await source.connect()
        return results
    
    async def disconnect_all_sources(self) -> Dict[str, bool]:
        """
        Disconnect from all data sources
        
        Returns:
            Dictionary of disconnection results
        """
        results = {}
        for source_id, source in self.data_sources.items():
            results[source_id] = await source.disconnect()
        return results
    
    def set_thresholds(self, athlete_id: str, thresholds: List[MetricThreshold]) -> None:
        """
        Set metric thresholds for an athlete
        
        Args:
            athlete_id: Athlete ID
            thresholds: List of threshold configurations
        """
        self.thresholds[athlete_id] = thresholds
    
    def register_alert_callback(self, callback: Callable[[FeedbackAlert], None]) -> None:
        """
        Register a callback for alerts
        
        Args:
            callback: Function to call with new alerts
        """
        self.alert_callbacks.append(callback)
    
    def _handle_metric_reading(self, reading: MetricReading) -> None:
        """
        Handle a new metric reading
        
        Args:
            reading: The new metric reading
        """
        # Buffer the reading
        if reading.source_id in self.readings_buffer:
            buffer = self.readings_buffer[reading.source_id]
            buffer.append(reading)
            
            # Trim buffer if it gets too large
            if len(buffer) > self.max_buffer_size:
                buffer = buffer[-self.max_buffer_size:]
                self.readings_buffer[reading.source_id] = buffer
        
        # Check thresholds for the athlete
        if reading.athlete_id and reading.athlete_id in self.thresholds:
            athlete_thresholds = self.thresholds[reading.athlete_id]
            
            for threshold in athlete_thresholds:
                if threshold.metric_type == reading.metric_type:
                    # Check if value exceeds threshold
                    if isinstance(reading.value, (int, float)) and threshold.is_exceeded(reading.value):
                        # Create an alert
                        alert = self._create_alert(reading, threshold)
                        
                        # Store alert
                        self.alerts.append(alert)
                        
                        # Notify callbacks
                        for callback in self.alert_callbacks:
                            try:
                                callback(alert)
                            except Exception as e:
                                logger.error(f"Error in alert callback: {str(e)}")
    
    def _create_alert(
        self,
        reading: MetricReading,
        threshold: MetricThreshold
    ) -> FeedbackAlert:
        """
        Create an alert from a threshold violation
        
        Args:
            reading: The metric reading
            threshold: The threshold that was exceeded
            
        Returns:
            Feedback alert
        """
        # Determine alert level based on how much the threshold was exceeded
        level = AlertLevel.WARNING
        
        value = reading.value
        if not isinstance(value, (int, float)):
            level = AlertLevel.INFO
            message = f"Unusual reading for {reading.metric_type.value}"
        else:
            # Calculate severity based on threshold
            if threshold.max_value and value > threshold.max_value:
                excess = (value - threshold.max_value) / threshold.max_value
                if excess > 0.2:
                    level = AlertLevel.CRITICAL
                message = f"{reading.metric_type.value.replace('_', ' ').title()} is too high: {value}"
            elif threshold.min_value and value < threshold.min_value:
                deficit = (threshold.min_value - value) / threshold.min_value
                if deficit > 0.2:
                    level = AlertLevel.CRITICAL
                message = f"{reading.metric_type.value.replace('_', ' ').title()} is too low: {value}"
            elif threshold.target_range:
                min_range, max_range = threshold.target_range
                if value < min_range:
                    message = f"{reading.metric_type.value.replace('_', ' ').title()} below target range: {value}"
                elif value > max_range:
                    message = f"{reading.metric_type.value.replace('_', ' ').title()} above target range: {value}"
                else:
                    message = f"{reading.metric_type.value.replace('_', ' ').title()} outside target"
            else:
                message = f"Abnormal {reading.metric_type.value.replace('_', ' ').title()}: {value}"
        
        # Generate actions based on metric type and severity
        actions = []
        
        if reading.metric_type == MetricType.HEART_RATE:
            if level == AlertLevel.CRITICAL:
                actions.append({
                    "type": "stop",
                    "message": "Stop activity immediately and rest"
                })
            elif level == AlertLevel.WARNING:
                actions.append({
                    "type": "reduce",
                    "message": "Reduce intensity and monitor"
                })
        elif reading.metric_type == MetricType.FATIGUE:
            actions.append({
                "type": "monitor",
                "message": "Monitor athlete for signs of fatigue"
            })
        
        # Create unique ID for alert
        alert_id = f"{reading.metric_type.value}_{level.value}_{datetime.datetime.now().timestamp()}"
        
        return FeedbackAlert(
            alert_id=alert_id,
            level=level,
            message=message,
            metric_reading=reading,
            threshold=threshold,
            actions=actions
        )
    
    def get_recent_readings(
        self,
        source_id: Optional[str] = None,
        athlete_id: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent readings from the buffer
        
        Args:
            source_id: Filter by source ID
            athlete_id: Filter by athlete ID
            metric_type: Filter by metric type
            limit: Maximum number of readings
            
        Returns:
            List of readings as dictionaries
        """
        all_readings = []
        
        # Collect readings from specified source or all sources
        sources = [source_id] if source_id else self.readings_buffer.keys()
        for sid in sources:
            if sid in self.readings_buffer:
                all_readings.extend(self.readings_buffer[sid])
        
        # Filter by athlete ID if specified
        if athlete_id:
            all_readings = [r for r in all_readings if r.athlete_id == athlete_id]
        
        # Filter by metric type if specified
        if metric_type:
            all_readings = [r for r in all_readings if r.metric_type == metric_type]
        
        # Sort by timestamp (most recent first)
        all_readings.sort(key=lambda r: r.timestamp, reverse=True)
        
        # Limit results
        all_readings = all_readings[:limit]
        
        # Convert to dictionaries
        return [r.to_dict() for r in all_readings]
    
    def get_active_alerts(
        self,
        athlete_id: Optional[str] = None,
        level: Optional[AlertLevel] = None,
        acknowledged: Optional[bool] = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get active (unacknowledged) alerts
        
        Args:
            athlete_id: Filter by athlete ID
            level: Filter by alert level
            acknowledged: Include acknowledged alerts
            limit: Maximum number of alerts
            
        Returns:
            List of alerts as dictionaries
        """
        filtered_alerts = self.alerts
        
        # Filter by acknowledgement status
        if not acknowledged:
            filtered_alerts = [a for a in filtered_alerts if not a.acknowledged]
        
        # Filter by athlete ID if specified
        if athlete_id:
            filtered_alerts = [
                a for a in filtered_alerts 
                if a.metric_reading.athlete_id == athlete_id
            ]
        
        # Filter by level if specified
        if level:
            filtered_alerts = [a for a in filtered_alerts if a.level == level]
        
        # Sort by timestamp (most recent first)
        filtered_alerts.sort(key=lambda a: a.timestamp, reverse=True)
        
        # Limit results
        filtered_alerts = filtered_alerts[:limit]
        
        # Convert to dictionaries
        return [a.to_dict() for a in filtered_alerts]
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: ID of alert to acknowledge
            user_id: ID of acknowledging user
            
        Returns:
            Success status
        """
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledge(user_id)
                return True
        
        return False 