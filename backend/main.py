"""
DealFlow AI - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import csv
import io
from typing import Optional
from bson import ObjectId

from backend.config import settings
from backend.services.mongodb_service import mongodb_service
from backend.agents.prospecting_agent import prospecting_agent
from backend.agents.nurturing_agent import nurturing_agent
from backend.agents.intelligence_agent import intelligence_agent
from backend.models.lead import LeadCreate, LeadUpdate
from backend.models.deal import DealCreate, DealUpdate

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def serialize(obj):
    """Recursively convert MongoDB documents to JSON-serializable dicts."""
    if isinstance(obj, list):
        return [serialize(i) for i in obj]
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DealFlow AI...")
    await mongodb_service.connect()
    logger.info("DealFlow AI started — MongoDB connected")
    yield
    await mongodb_service.disconnect()
    logger.info("DealFlow AI shut down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="B2B Sales Intelligence Agent — Google Gemini + MongoDB",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "gemini_enabled": settings.gemini_enabled,
        "email_enabled": settings.email_enabled,
    }


# ─── Leads ───────────────────────────────────────────────────────────────────

@app.post("/api/leads")
async def create_lead(lead: LeadCreate, background_tasks: BackgroundTasks):
    try:
        lead_dict = lead.model_dump(exclude_none=True)
        lead_id = await mongodb_service.create_lead(lead_dict)
        background_tasks.add_task(prospecting_agent.process_lead, lead_id)
        return {"success": True, "lead_id": lead_id}
    except Exception as e:
        logger.error(f"create_lead error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads")
async def list_leads(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    try:
        filters = {}
        if status:
            filters["status"] = status
        leads = await mongodb_service.list_leads(skip=skip, limit=limit, filters=filters)
        total = await mongodb_service.count_leads(filters=filters)
        return {"leads": serialize(leads), "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        logger.error(f"list_leads error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    try:
        lead = await mongodb_service.get_lead(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return serialize(lead)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, lead_update: LeadUpdate):
    try:
        update_dict = lead_update.model_dump(exclude_none=True)
        success = await mongodb_service.update_lead(lead_id, update_dict)
        if not success:
            raise HTTPException(status_code=404, detail="Lead not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/leads/bulk-import")
async def bulk_import_leads(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    try:
        contents = await file.read()
        csv_data = io.StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(csv_data)

        lead_ids = []
        for row in reader:
            lead_data = {k: v.strip() for k, v in row.items() if v and v.strip()}
            if lead_data.get("company_name"):
                lead_id = await mongodb_service.create_lead(lead_data)
                lead_ids.append(lead_id)

        if background_tasks and lead_ids:
            background_tasks.add_task(prospecting_agent.bulk_process_leads, lead_ids)

        return {"success": True, "imported_count": len(lead_ids), "lead_ids": lead_ids}
    except Exception as e:
        logger.error(f"bulk_import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Deals ───────────────────────────────────────────────────────────────────

@app.post("/api/deals")
async def create_deal(deal: DealCreate):
    try:
        deal_dict = deal.model_dump(exclude_none=True)
        deal_id = await mongodb_service.create_deal(deal_dict)
        return {"success": True, "deal_id": deal_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/deals")
async def list_deals(skip: int = 0, limit: int = 100, stage: Optional[str] = None):
    try:
        filters = {}
        if stage:
            filters["stage"] = stage
        deals = await mongodb_service.list_deals(skip=skip, limit=limit, filters=filters)
        total = await mongodb_service.count_deals(filters=filters)
        return {"deals": serialize(deals), "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/deals/{deal_id}")
async def get_deal(deal_id: str):
    try:
        deal = await mongodb_service.get_deal(deal_id)
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        return serialize(deal)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/deals/{deal_id}")
async def update_deal(deal_id: str, deal_update: DealUpdate):
    try:
        update_dict = deal_update.model_dump(exclude_none=True)
        success = await mongodb_service.update_deal(deal_id, update_dict)
        if not success:
            raise HTTPException(status_code=404, detail="Deal not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Agent Endpoints ─────────────────────────────────────────────────────────

@app.post("/api/agents/prospecting/process-lead/{lead_id}")
async def process_lead(lead_id: str):
    try:
        result = await prospecting_agent.process_lead(lead_id)
        return serialize(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/prospecting/top-leads")
async def get_top_leads(limit: int = 10):
    try:
        leads = await prospecting_agent.get_top_leads(limit=limit)
        return {"leads": serialize(leads)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/nurturing/send-outreach/{lead_id}")
async def send_outreach(lead_id: str):
    try:
        result = await nurturing_agent.send_initial_outreach(lead_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/nurturing/follow-up/{deal_id}")
async def send_follow_up(deal_id: str):
    try:
        result = await nurturing_agent.send_follow_up(deal_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/nurturing/check-follow-ups")
async def check_follow_ups():
    try:
        follow_ups = await nurturing_agent.check_follow_ups_needed()
        return {"follow_ups": serialize(follow_ups)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/nurturing/auto-follow-up")
async def auto_follow_up():
    try:
        result = await nurturing_agent.auto_follow_up_deals()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/intelligence/predict/{deal_id}")
async def predict_deal(deal_id: str):
    try:
        result = await intelligence_agent.predict_deal_outcome(deal_id)
        return serialize(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/intelligence/at-risk-deals")
async def at_risk_deals():
    try:
        deals = await intelligence_agent.identify_at_risk_deals()
        return {"at_risk_deals": serialize(deals)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/intelligence/pipeline-insights")
async def pipeline_insights():
    try:
        insights = await intelligence_agent.generate_pipeline_insights()
        return serialize(insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/performance")
async def agent_performance():
    try:
        report = await intelligence_agent.get_agent_performance_report()
        return serialize(report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Analytics ───────────────────────────────────────────────────────────────

@app.get("/api/analytics/pipeline-stats")
async def pipeline_stats():
    try:
        stats = await mongodb_service.get_pipeline_stats()
        return serialize(stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/lead-score-distribution")
async def lead_score_distribution():
    try:
        dist = await mongodb_service.get_lead_score_distribution()
        return {"distribution": serialize(dist)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/summary")
async def summary_stats():
    try:
        stats = await mongodb_service.get_summary_stats()
        return serialize(stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/actions")
async def list_agent_actions(limit: int = 50):
    try:
        actions = await mongodb_service.list_agent_actions(limit=limit)
        return {"actions": serialize(actions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=settings.DEBUG)
