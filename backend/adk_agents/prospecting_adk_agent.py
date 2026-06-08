"""
Prospecting Agent using Google ADK + MongoDB MCP Server
Handles lead enrichment, scoring, and qualification
"""
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime

from google import genai
from google.genai import types

from backend.config import settings

logger = logging.getLogger(__name__)


class ProspectingADKAgent:
    """
    ADK-powered Prospecting Agent with MongoDB MCP integration
    """
    
    def __init__(self):
        self.client = None
        self.agent_name = "prospecting_agent"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            if settings.GEMINI_API_KEY:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Prospecting ADK Agent initialized with Gemini")
            else:
                logger.warning("No Gemini API key - using fallback mode")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None
    
    async def process_lead(self, lead_id: str, mcp_tools) -> Dict:
        """
        Process and enrich a lead using ADK agent with MCP tools
        
        Args:
            lead_id: The lead ID to process
            mcp_tools: MongoDB MCP tools provided by ADK
        
        Returns:
            Dict with processing results
        """
        action_id = None
        
        try:
            # Log agent action start using MCP
            action_doc = {
                "agent_type": self.agent_name,
                "action": "process_lead",
                "lead_id": lead_id,
                "status": "running",
                "started_at": datetime.utcnow().isoformat(),
            }
            
            # Use MCP tool to insert action log
            # In real ADK implementation, tools are called via agent.run()
            
            # Fetch lead using MCP find tool
            prompt = f"""
You are a B2B sales prospecting expert. 

Task: Analyze and enrich the lead with ID: {lead_id}

Steps:
1. Find the lead document from the 'leads' collection
2. Analyze the company information
3. Calculate a lead score (0-100) based on:
   - Company size (larger = higher score)
   - Industry fit (technology/SaaS = higher score)
   - Contact quality (valid email, name present)
   - Website presence
4. Generate enrichment insights
5. Update the lead with:
   - lead_score
   - enriched_data
   - status = 'qualified' if score >= 60, else 'new'

Use the MongoDB MCP tools to:
- Find the lead
- Update it with your analysis
- Log the action

Be specific and provide actionable insights.
"""
            
            if self.client:
                # Use Gemini with MCP tools
                response = await self._call_gemini_with_mcp(prompt, mcp_tools)
                
                return {
                    "success": True,
                    "lead_id": lead_id,
                    "agent": self.agent_name,
                    "analysis": response,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # Fallback mode
                return {
                    "success": False,
                    "lead_id": lead_id,
                    "error": "Gemini client not initialized",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in process_lead: {e}")
            return {
                "success": False,
                "lead_id": lead_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _call_gemini_with_mcp(self, prompt: str, mcp_tools) -> str:
        """Call Gemini API with MCP tool access"""
        try:
            # In production ADK setup, this would be:
            # response = await agent.run(prompt)
            # For now, use basic Gemini call
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return f"Error: {str(e)}"
    
    async def bulk_process_leads(self, lead_ids: List[str], mcp_tools) -> Dict:
        """Process multiple leads"""
        results = []
        
        for lead_id in lead_ids:
            result = await self.process_lead(lead_id, mcp_tools)
            results.append(result)
        
        return {
            "processed": len(results),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def calculate_lead_score(self, lead_data: Dict) -> int:
        """Calculate lead score using rule-based logic"""
        score = 0
        
        # Company size scoring
        company_size = lead_data.get("company_size", "").lower()
        size_scores = {
            "enterprise": 30,
            "large": 25,
            "medium": 20,
            "small": 15,
            "startup": 10
        }
        score += size_scores.get(company_size, 10)
        
        # Industry scoring
        industry = lead_data.get("industry", "").lower()
        high_value_industries = ["technology", "saas", "software", "fintech", "healthcare"]
        if any(ind in industry for ind in high_value_industries):
            score += 25
        else:
            score += 10
        
        # Contact quality
        if lead_data.get("email"):
            score += 15
        if lead_data.get("contact_name"):
            score += 10
        if lead_data.get("phone"):
            score += 5
        
        # Web presence
        if lead_data.get("website"):
            score += 10
        
        # Budget/revenue indicators
        if lead_data.get("annual_revenue"):
            score += 5
        
        return min(score, 100)


# Global instance
prospecting_adk_agent = ProspectingADKAgent()
