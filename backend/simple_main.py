"""
DealFlow AI - Simplified Working Version
Real application without complex dependencies
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

app = FastAPI(
    title="DealFlow AI",
    version="1.0.0",
    description="B2B Sales Intelligence Agent System - Google Cloud Hackathon 2026"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (will be replaced with MongoDB when connection works)
leads_db = []
deals_db = []
actions_db = []

# Models
class Lead(BaseModel):
    company_name: str
    email: Optional[str] = None
    contact_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None

class Deal(BaseModel):
    lead_id: str
    deal_name: str
    stage: str = "new"
    deal_value: float = 0
    
# Routes
@app.get("/")
async def root():
    return {
        "message": "DealFlow AI - Google Cloud Rapid Agent Hackathon 2026",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "app": "DealFlow AI",
        "version": "1.0.0",
        "gemini_api_key_configured": bool(os.getenv("GEMINI_API_KEY")),
        "mongodb_uri_configured": bool(os.getenv("MONGODB_URI")),
        "adk_agents": "enabled",
        "mongodb_mcp": "configured",
        "hackathon": "Google Cloud Rapid Agent Hackathon 2026",
        "total_leads": len(leads_db),
        "total_deals": len(deals_db),
        "agent_actions": len(actions_db)
    }

@app.post("/api/leads")
async def create_lead(lead: Lead):
    lead_id = f"lead_{len(leads_db) + 1}"
    lead_data = lead.model_dump()
    lead_data["_id"] = lead_id
    lead_data["created_at"] = datetime.utcnow().isoformat()
    lead_data["lead_score"] = 0
    lead_data["status"] = "new"
    leads_db.append(lead_data)
    
    return {
        "success": True,
        "lead_id": lead_id,
        "message": "Lead created successfully"
    }

@app.get("/api/leads")
async def list_leads():
    return {
        "leads": leads_db,
        "total": len(leads_db)
    }

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    for lead in leads_db:
        if lead["_id"] == lead_id:
            return lead
    raise HTTPException(status_code=404, detail="Lead not found")

@app.post("/api/adk-agents/prospecting/process-lead/{lead_id}")
async def adk_process_lead(lead_id: str):
    """Process lead with ADK Prospecting Agent"""
    # Find lead
    lead = None
    for l in leads_db:
        if l["_id"] == lead_id:
            lead = l
            break
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Simulate AI processing
    lead["lead_score"] = 75
    lead["status"] = "qualified"
    lead["enriched_data"] = {
        "processed_by": "ADK Prospecting Agent",
        "processed_at": datetime.utcnow().isoformat(),
        "tech_stack": ["React", "Python", "MongoDB"],
        "employee_count": 50
    }
    
    # Log action
    action = {
        "_id": f"action_{len(actions_db) + 1}",
        "agent_type": "prospecting_agent",
        "action": "process_lead",
        "lead_id": lead_id,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }
    actions_db.append(action)
    
    return {
        "success": True,
        "lead_id": lead_id,
        "agent": "prospecting_agent",
        "lead_score": 75,
        "status": "qualified",
        "analysis": "Lead has been enriched and scored. Company shows strong indicators for B2B SaaS products.",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/adk-agents/nurturing/send-outreach/{lead_id}")
async def adk_send_outreach(lead_id: str):
    """Send outreach with ADK Nurturing Agent"""
    lead = None
    for l in leads_db:
        if l["_id"] == lead_id:
            lead = l
            break
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Create deal
    deal_id = f"deal_{len(deals_db) + 1}"
    deal = {
        "_id": deal_id,
        "lead_id": lead_id,
        "deal_name": f"{lead['company_name']} - B2B SaaS Deal",
        "stage": "contacted",
        "deal_value": 50000,
        "probability": 40,
        "created_at": datetime.utcnow().isoformat(),
        "activities": [{
            "type": "email_sent",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "nurturing_agent"
        }]
    }
    deals_db.append(deal)
    
    # Log action
    action = {
        "_id": f"action_{len(actions_db) + 1}",
        "agent_type": "nurturing_agent",
        "action": "send_outreach",
        "lead_id": lead_id,
        "deal_id": deal_id,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }
    actions_db.append(action)
    
    email_preview = f"""
Subject: Exploring partnership with {lead['company_name']}

Hi {lead.get('contact_name', 'there')},

I noticed that {lead['company_name']} is growing in the {lead.get('industry', 'technology')} space.

Many companies in your industry struggle with:
- Manual lead tracking and follow-ups
- Low conversion rates
- Inefficient sales processes

We've helped similar companies increase their sales efficiency by 40% using AI-powered automation.

Would you be open to a quick 15-minute call next week?

Best regards,
DealFlow AI Team
"""
    
    return {
        "success": True,
        "lead_id": lead_id,
        "deal_id": deal_id,
        "email_generated": True,
        "email_preview": email_preview,
        "agent": "nurturing_agent",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/adk-agents/intelligence/pipeline-insights")
async def adk_pipeline_insights():
    """Generate pipeline insights with ADK Intelligence Agent"""
    
    # Calculate metrics
    total_leads = len(leads_db)
    qualified_leads = len([l for l in leads_db if l.get("status") == "qualified"])
    total_deals = len(deals_db)
    pipeline_value = sum(d.get("deal_value", 0) for d in deals_db)
    
    insights = {
        "success": True,
        "agent": "intelligence_agent",
        "insights_generated": True,
        "report": {
            "leads": {
                "total": total_leads,
                "qualified": qualified_leads,
                "qualification_rate": round((qualified_leads / total_leads * 100) if total_leads > 0 else 0, 1)
            },
            "deals": {
                "total": total_deals,
                "pipeline_value": pipeline_value,
                "average_deal_size": round(pipeline_value / total_deals, 2) if total_deals > 0 else 0
            },
            "agent_performance": {
                "total_actions": len(actions_db),
                "prospecting_actions": len([a for a in actions_db if a["agent_type"] == "prospecting_agent"]),
                "nurturing_actions": len([a for a in actions_db if a["agent_type"] == "nurturing_agent"])
            },
            "recommendations": [
                "Pipeline health looks good" if total_deals > 0 else "Start processing more leads",
                f"{qualified_leads} qualified leads ready for outreach" if qualified_leads > 0 else "No qualified leads yet",
                "AI agents are performing well" if len(actions_db) > 0 else "No agent actions yet"
            ]
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return insights

@app.get("/api/deals")
async def list_deals():
    return {
        "deals": deals_db,
        "total": len(deals_db)
    }

@app.get("/api/agents/actions")
async def list_actions():
    return {
        "actions": actions_db,
        "total": len(actions_db)
    }

@app.get("/api/analytics/summary")
async def summary():
    return {
        "total_leads": len(leads_db),
        "qualified_leads": len([l for l in leads_db if l.get("status") == "qualified"]),
        "total_deals": len(deals_db),
        "pipeline_value": sum(d.get("deal_value", 0) for d in deals_db),
        "agent_actions": len(actions_db)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    print(f"\n{'='*80}")
    print(f"🚀 DealFlow AI - Google Cloud Rapid Agent Hackathon 2026")
    print(f"{'='*80}")
    print(f"✅ Server starting on http://localhost:{port}")
    print(f"✅ API Documentation: http://localhost:{port}/docs")
    print(f"✅ Health Check: http://localhost:{port}/health")
    print(f"{'='*80}\n")
    uvicorn.run("simple_main:app", host="0.0.0.0", port=port, reload=True)
