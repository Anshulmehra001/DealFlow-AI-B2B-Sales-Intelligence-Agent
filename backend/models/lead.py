"""
Lead data model
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Industry(str, Enum):
    """Industry categories"""
    SAAS = "saas"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    ECOMMERCE = "ecommerce"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    EDUCATION = "education"
    REAL_ESTATE = "real_estate"
    OTHER = "other"


class CompanySize(str, Enum):
    """Company size categories"""
    STARTUP = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "201-1000"
    ENTERPRISE = "1000+"


class LeadStatus(str, Enum):
    """Lead status"""
    NEW = "new"
    ENRICHING = "enriching"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    CONVERTED = "converted"


class EnrichedData(BaseModel):
    """Enriched lead data from web scraping"""
    tech_stack: List[str] = Field(default_factory=list)
    funding_stage: Optional[str] = None
    recent_news: List[str] = Field(default_factory=list)
    social_media: Dict[str, str] = Field(default_factory=dict)
    employee_count_estimate: Optional[int] = None
    annual_revenue_estimate: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)


class Lead(BaseModel):
    """Lead model"""
    id: Optional[str] = Field(None, alias="_id")
    company_name: str = Field(..., min_length=1, max_length=200)
    website: Optional[str] = None
    industry: Optional[Industry] = None
    company_size: Optional[CompanySize] = None
    
    # Contact Information
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    # Lead Details
    source: str = Field(default="manual")
    lead_score: int = Field(default=0, ge=0, le=100)
    status: LeadStatus = Field(default=LeadStatus.NEW)
    
    # Enriched Data
    enriched_data: Optional[EnrichedData] = None
    
    # Vector Embedding for Semantic Search
    embedding: Optional[List[float]] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_contacted_at: Optional[datetime] = None
    
    # Notes and Tags
    notes: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # Assignment
    assigned_to: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "company_name": "Acme Corp",
                "website": "https://acmecorp.com",
                "industry": "saas",
                "company_size": "51-200",
                "contact_person": "John Doe",
                "email": "john@acmecorp.com",
                "phone": "+1-555-0123",
                "source": "csv_import",
                "lead_score": 85,
                "status": "qualified",
                "tags": ["high-priority", "enterprise"]
            }
        }


class LeadCreate(BaseModel):
    """Schema for creating a new lead"""
    company_name: str = Field(..., min_length=1, max_length=200)
    website: Optional[str] = None
    industry: Optional[Industry] = None
    company_size: Optional[CompanySize] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    source: str = Field(default="manual")
    tags: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class LeadUpdate(BaseModel):
    """Schema for updating a lead"""
    company_name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[Industry] = None
    company_size: Optional[CompanySize] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    lead_score: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[LeadStatus] = None
    tags: Optional[List[str]] = None
    notes: Optional[List[str]] = None
    assigned_to: Optional[str] = None


class LeadBulkImport(BaseModel):
    """Schema for bulk importing leads"""
    leads: List[LeadCreate]
    source: str = Field(default="csv_import")
    auto_enrich: bool = Field(default=True)
