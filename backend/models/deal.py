"""
Deal data model
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class DealStage(str, Enum):
    """Deal pipeline stages"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ActivityType(str, Enum):
    """Activity types"""
    EMAIL_SENT = "email_sent"
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"
    CALL_MADE = "call_made"
    MEETING_SCHEDULED = "meeting_scheduled"
    MEETING_COMPLETED = "meeting_completed"
    PROPOSAL_SENT = "proposal_sent"
    FOLLOW_UP = "follow_up"
    NOTE_ADDED = "note_added"
    STAGE_CHANGED = "stage_changed"


class Activity(BaseModel):
    """Activity log entry"""
    type: ActivityType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    description: str
    outcome: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)


class Deal(BaseModel):
    """Deal model for time-series tracking"""
    id: Optional[str] = Field(None, alias="_id")
    lead_id: str = Field(..., description="Reference to Lead")
    
    # Deal Information
    deal_name: str = Field(..., min_length=1, max_length=200)
    deal_value: float = Field(..., ge=0)
    currency: str = Field(default="USD")
    
    # Pipeline
    stage: DealStage = Field(default=DealStage.NEW)
    probability: int = Field(default=0, ge=0, le=100, description="Close probability %")
    
    # Dates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_contact_date: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    
    # Activities (Time-series data)
    activities: List[Activity] = Field(default_factory=list)
    
    # Notes and Context
    notes: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    decision_makers: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    
    # Assignment
    assigned_to: Optional[str] = None
    
    # AI Predictions
    predicted_close_date: Optional[datetime] = None
    predicted_value: Optional[float] = None
    risk_score: int = Field(default=0, ge=0, le=100)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "lead_id": "507f1f77bcf86cd799439011",
                "deal_name": "Acme Corp - Enterprise Plan",
                "deal_value": 50000.0,
                "currency": "USD",
                "stage": "proposal",
                "probability": 75,
                "expected_close_date": "2026-06-30T00:00:00Z",
                "pain_points": ["Manual data entry", "Lack of automation"],
                "decision_makers": ["John Doe - CTO", "Jane Smith - CFO"]
            }
        }


class DealCreate(BaseModel):
    """Schema for creating a new deal"""
    lead_id: str
    deal_name: str = Field(..., min_length=1, max_length=200)
    deal_value: float = Field(..., ge=0)
    currency: str = Field(default="USD")
    stage: DealStage = Field(default=DealStage.NEW)
    expected_close_date: Optional[datetime] = None
    pain_points: List[str] = Field(default_factory=list)
    decision_makers: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class DealUpdate(BaseModel):
    """Schema for updating a deal"""
    deal_name: Optional[str] = None
    deal_value: Optional[float] = Field(None, ge=0)
    stage: Optional[DealStage] = None
    probability: Optional[int] = Field(None, ge=0, le=100)
    next_follow_up: Optional[datetime] = None
    expected_close_date: Optional[datetime] = None
    pain_points: Optional[List[str]] = None
    decision_makers: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    notes: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    assigned_to: Optional[str] = None


class DealActivity(BaseModel):
    """Schema for adding an activity to a deal"""
    deal_id: str
    type: ActivityType
    description: str
    outcome: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)
