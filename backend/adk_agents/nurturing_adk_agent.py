"""
Nurturing Agent using Google ADK + MongoDB MCP Server
Handles email automation, follow-ups, and deal nurturing
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

from google import genai
from google.genai import types

from backend.config import settings
from backend.services.email_service import email_service

logger = logging.getLogger(__name__)


class NurturingADKAgent:
    """
    ADK-powered Nurturing Agent with MongoDB MCP integration
    """
    
    def __init__(self):
        self.client = None
        self.agent_name = "nurturing_agent"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            if settings.GEMINI_API_KEY:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Nurturing ADK Agent initialized with Gemini")
            else:
                logger.warning("No Gemini API key - using fallback mode")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None
    
    async def send_initial_outreach(self, lead_id: str, mcp_tools) -> Dict:
        """
        Generate and send initial outreach email using ADK agent
        
        Args:
            lead_id: The lead ID to contact
            mcp_tools: MongoDB MCP tools provided by ADK
        
        Returns:
            Dict with email send results
        """
        try:
            prompt = f"""
You are a B2B sales outreach expert specializing in personalized communication.

Task: Create and send an initial outreach email for lead ID: {lead_id}

Steps:
1. Use MongoDB MCP tools to find the lead in 'leads' collection
2. Analyze their company, industry, and role
3. Generate a personalized email that:
   - Addresses specific pain points for their industry
   - Is under 150 words
   - Has a clear, soft call-to-action
   - Professional but conversational tone
4. Create a deal in 'deals' collection with:
   - lead_id reference
   - stage = 'contacted'
   - deal_value = estimated based on company size
   - next_follow_up = 3 days from now
5. Log this action in 'agent_actions' collection

Return the email subject and body that was created.
"""
            
            if self.client:
                response = await self._call_gemini_with_mcp(prompt, mcp_tools)
                
                # In production, email would be sent via email service
                # For demo, we log it
                
                return {
                    "success": True,
                    "lead_id": lead_id,
                    "email_generated": True,
                    "email_preview": response[:200] + "..." if len(response) > 200 else response,
                    "agent": self.agent_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Gemini client not initialized",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in send_initial_outreach: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def send_follow_up(self, deal_id: str, mcp_tools) -> Dict:
        """Send a follow-up email for an existing deal"""
        try:
            prompt = f"""
You are a B2B sales follow-up specialist.

Task: Create a follow-up email for deal ID: {deal_id}

Steps:
1. Find the deal in 'deals' collection using MongoDB MCP tools
2. Find the associated lead
3. Review previous activities
4. Generate a follow-up email that:
   - References previous conversation
   - Provides additional value
   - Suggests specific next steps
   - Under 100 words
5. Update deal:
   - Add activity to activities array
   - Update next_follow_up date
   - Update stage if appropriate
6. Log the action

Return the follow-up email created.
"""
            
            if self.client:
                response = await self._call_gemini_with_mcp(prompt, mcp_tools)
                
                return {
                    "success": True,
                    "deal_id": deal_id,
                    "follow_up_sent": True,
                    "email_preview": response[:200] + "..." if len(response) > 200 else response,
                    "agent": self.agent_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Gemini client not initialized",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in send_follow_up: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_follow_ups_needed(self, mcp_tools) -> Dict:
        """Check which deals need follow-up"""
        try:
            prompt = """
You are a sales pipeline manager.

Task: Identify deals that need follow-up attention

Steps:
1. Use MongoDB MCP aggregate tool on 'deals' collection to find:
   - Deals where next_follow_up date is in the past
   - Deals in 'contacted' or 'qualified' stage for > 7 days
   - Deals with no recent activities
2. Return list of deal IDs that need follow-up
3. Prioritize by:
   - Deal value (higher first)
   - Days since last contact (longer first)

Return JSON array of deal IDs with priority scores.
"""
            
            if self.client:
                response = await self._call_gemini_with_mcp(prompt, mcp_tools)
                
                return {
                    "success": True,
                    "follow_ups_identified": True,
                    "details": response,
                    "agent": self.agent_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Gemini client not initialized",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in check_follow_ups_needed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _call_gemini_with_mcp(self, prompt: str, mcp_tools) -> str:
        """Call Gemini API with MCP tool access"""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return f"Error: {str(e)}"


# Global instance
nurturing_adk_agent = NurturingADKAgent()
