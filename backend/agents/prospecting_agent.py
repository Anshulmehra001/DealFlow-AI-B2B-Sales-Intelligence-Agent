"""
Prospecting Agent - Enriches leads and scores opportunities
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

from backend.services.mongodb_service import mongodb_service
from backend.services.enrichment_service import enrichment_service
from backend.services.gemini_service import gemini_service
from backend.models.agent_action import AgentType, ActionType, ActionStatus
from backend.config import settings

logger = logging.getLogger(__name__)


class ProspectingAgent:
    """Agent responsible for lead prospecting and enrichment"""
    
    def __init__(self):
        self.agent_type = AgentType.PROSPECTING
        self.name = "Prospecting Agent"
    
    async def process_lead(self, lead_id: str) -> Dict:
        """Process and enrich a single lead"""
        action_id = None
        
        try:
            # Log agent action start
            action_id = await mongodb_service.log_agent_action({
                "agent_type": self.agent_type.value,
                "action_type": ActionType.LEAD_ENRICHMENT.value,
                "lead_id": lead_id,
                "status": ActionStatus.IN_PROGRESS.value,
                "input_data": {"lead_id": lead_id}
            })
            
            # Get lead data
            lead = await mongodb_service.get_lead(lead_id)
            if not lead:
                raise ValueError(f"Lead not found: {lead_id}")
            
            # Enrich lead data
            enriched_data = await enrichment_service.enrich_lead(
                company_name=lead["company_name"],
                website=lead.get("website")
            )
            
            # Score the lead
            lead_score = await self._score_lead(lead, enriched_data)
            
            # Get AI insights
            ai_insights = await gemini_service.analyze_lead({
                **lead,
                "enriched_data": enriched_data
            })
            
            # Update lead in database
            await mongodb_service.update_lead(lead_id, {
                "enriched_data": enriched_data,
                "lead_score": lead_score,
                "status": "qualified" if lead_score >= settings.LEAD_SCORE_THRESHOLD else "unqualified",
                "notes": lead.get("notes", []) + [f"AI Insight: {ai_insights.get('insights', 'N/A')}"]
            })
            
            # Log success
            if action_id:
                await mongodb_service.update_agent_action(action_id, {
                    "status": ActionStatus.SUCCESS.value,
                    "output_data": {
                        "enriched_data": enriched_data,
                        "lead_score": lead_score
                    },
                    "reasoning": f"Lead enriched and scored: {lead_score}/100",
                    "completed_at": datetime.utcnow()
                })
            
            logger.info(f"Successfully processed lead {lead_id} with score {lead_score}")
            
            return {
                "success": True,
                "lead_id": lead_id,
                "lead_score": lead_score,
                "enriched_data": enriched_data
            }
            
        except Exception as e:
            logger.error(f"Failed to process lead {lead_id}: {e}")
            
            if action_id:
                await mongodb_service.update_agent_action(action_id, {
                    "status": ActionStatus.FAILED.value,
                    "error_message": str(e),
                    "completed_at": datetime.utcnow()
                })
            
            return {
                "success": False,
                "lead_id": lead_id,
                "error": str(e)
            }
    
    async def _score_lead(self, lead: Dict, enriched_data: Dict) -> int:
        """Score a lead based on various factors"""
        score = 0
        
        # Base score for having contact information
        if lead.get("email"):
            score += 20
        if lead.get("phone"):
            score += 10
        if lead.get("linkedin_url"):
            score += 10
        
        # Score based on company size
        company_size = lead.get("company_size")
        size_scores = {
            "1-10": 10,
            "11-50": 20,
            "51-200": 30,
            "201-1000": 25,
            "1000+": 15
        }
        score += size_scores.get(company_size, 0)
        
        # Score based on industry (prioritize SaaS and tech)
        industry = lead.get("industry")
        industry_scores = {
            "saas": 20,
            "fintech": 18,
            "healthcare": 15,
            "ecommerce": 15,
            "manufacturing": 12,
            "retail": 10,
            "education": 10,
            "real_estate": 8,
            "other": 5
        }
        score += industry_scores.get(industry, 0)
        
        # Score based on tech stack (modern tech = higher score)
        tech_stack = enriched_data.get("tech_stack", [])
        modern_tech = ["React", "Vue.js", "Angular", "Node.js", "MongoDB", "PostgreSQL", "Next.js"]
        tech_score = sum(5 for tech in tech_stack if tech in modern_tech)
        score += min(tech_score, 20)  # Cap at 20
        
        # Score based on social media presence
        social_media = enriched_data.get("social_media", {})
        score += len(social_media) * 2  # 2 points per platform
        
        # Ensure score is between 0 and 100
        return min(max(score, 0), 100)
    
    async def bulk_process_leads(self, lead_ids: List[str]) -> Dict:
        """Process multiple leads"""
        results = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "high_score_leads": []
        }
        
        for lead_id in lead_ids:
            result = await self.process_lead(lead_id)
            results["processed"] += 1
            
            if result["success"]:
                results["successful"] += 1
                if result["lead_score"] >= settings.LEAD_SCORE_THRESHOLD:
                    results["high_score_leads"].append({
                        "lead_id": lead_id,
                        "score": result["lead_score"]
                    })
            else:
                results["failed"] += 1
        
        logger.info(f"Bulk processed {results['processed']} leads: "
                   f"{results['successful']} successful, {results['failed']} failed")
        
        return results
    
    async def find_similar_leads(self, lead_id: str, limit: int = 5) -> List[Dict]:
        """Find similar leads using vector search"""
        try:
            lead = await mongodb_service.get_lead(lead_id)
            if not lead or not lead.get("embedding"):
                return []
            
            # Perform vector search
            similar_leads = await mongodb_service.vector_search(
                query_embedding=lead["embedding"],
                limit=limit + 1  # +1 to exclude the query lead itself
            )
            
            # Filter out the query lead
            return [l for l in similar_leads if str(l.get("_id")) != lead_id][:limit]
            
        except Exception as e:
            logger.error(f"Failed to find similar leads: {e}")
            return []
    
    async def get_top_leads(self, limit: int = 10) -> List[Dict]:
        """Get top scored leads"""
        try:
            leads = await mongodb_service.list_leads(
                limit=limit,
                filters={"lead_score": {"$gte": settings.LEAD_SCORE_THRESHOLD}}
            )
            return sorted(leads, key=lambda x: x.get("lead_score", 0), reverse=True)
        except Exception as e:
            logger.error(f"Failed to get top leads: {e}")
            return []


# Global prospecting agent instance
prospecting_agent = ProspectingAgent()
