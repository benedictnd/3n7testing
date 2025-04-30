from typing import List, Optional
from pydantic import BaseModel

class CoachAssignment(BaseModel):
    """Model for coach assignments to training sessions"""
    coach_id: str
    name: str
    role: Optional[str] = None  # "Head Coach", "Assistant", etc.
    
    class Config:
        from_attributes = True
