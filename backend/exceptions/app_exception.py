from fastapi import HTTPException

class AppException(HTTPException):
    """
    Custom application exception class that extends FastAPI's HTTPException.
    Use this for application-specific exceptions with standardized formatting.
    """
    
    def __init__(self, status_code: int, detail: str):
        """
        Initialize the exception with a status code and detail message.
        
        Args:
            status_code: HTTP status code to return
            detail: Error message details
        """
        super().__init__(
            status_code=status_code,
            detail=detail
        ) 