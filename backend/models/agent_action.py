"""
Agent Action data model for logging agent activities
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Types of agents"""
    PROSPECTING = "prospecting"
    NURTURING = "nurturing"
    INTELLIGENCE = "intelligence"


class ActionType(str, Enum):
    """Types of actions agents can perform"""
    LEAD_ENRICHMENT = "lead_enrichment"
    LEAD_SCORING = "lead_scoring"
    EMAIL_SENT = "email_sent"
    DEAL_PREDICTION = "deal_prediction"
    RISK_ASSESSMENT = "risk_assessment"
    FOLLOW_UP_SCHEDULED = "follow_up_scheduled"
    INSIGHT_GENERATED = "insight_generated"
    WEB_SCRAPING = "web_scraping"
    DATA_ANALYSIS = "data_analysis"


class ActionStatus(str, Enum):
    """Status of agent action"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentAction(BaseModel):
    """Agent action log model"""
    id: Optional[str] = Field(None, alias="_id")
    
    # Agent Information
    agent_type: AgentType
    action_type: ActionType
    
    # Related Entities
    lead_id: Optional[str] = None
    deal_id: Optional[str] = None
    
    # Action Details
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    reasoning: Optional[str] = None
    
    # Status
    status: ActionStatus = Field(default=ActionStatus.PENDING)
    error_message: Optional[str] = None
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "agent_type": "prospecting",
                "action_type": "lead_enrichment",
                "lead_id": "507f1f77bcf86cd799439011",
                "input_data": {
                    "company_name": "Acme Corp",
                    "website": "https://acmecorp.com"
                },
                "output_data": {
                    "tech_stack": ["React", "Node.js", "MongoDB"],
                    "employee_count": 150,
                    "funding_stage": "Series B"
                },
                "reasoning": "Scraped company website and LinkedIn profile",
                "status": "success",
                "duration_seconds": 3.5
            }
        }


class AgentActionCreate(BaseModel):
    """Schema for creating an agent action log"""
    agent_type: AgentType
    action_type: ActionType
    lead_id: Optional[str] = None
    deal_id: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentActionUpdate(BaseModel):
    """Schema for updating an agent action"""
    output_data: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    status: Optional[ActionStatus] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class AgentMetrics(BaseModel):
    """Agent performance metrics"""
    agent_type: AgentType
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    average_duration_seconds: float = 0.0
    success_rate: float = 0.0
    last_action_at: Optional[datetime] = None
