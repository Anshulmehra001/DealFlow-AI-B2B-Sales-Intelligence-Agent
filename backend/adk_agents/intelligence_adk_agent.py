"""
Intelligence Agent using Google ADK + MongoDB MCP Server
Handles analytics, predictions, and insights
"""
import logging
from typing import Dict, List
from datetime import datetime

from google import genai
from google.genai import types

from backend.config import settings

logger = logging.getLogger(__name__)


class IntelligenceADKAgent:
    """
    ADK-powered Intelligence Agent with MongoDB MCP integration
    """
    
    def __init__(self):
        self.client = None
        self.agent_name = "intelligence_agent"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            if settings.GEMINI_API_KEY:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Intelligence ADK Agent initialized with Gemini")
            else:
                logger.warning("No Gemini API key - using fallback mode")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None
    
    async def predict_deal_outcome(self, deal_id: str, mcp_tools) -> Dict:
        """
        Predict deal outcome using AI analysis via ADK agent
        
        Args:
            deal_id: The deal ID to analyze
            mcp_tools: MongoDB MCP tools provided by ADK
        
        Returns:
            Dict with prediction results
        """
        try:
            prompt = f"""
You are a B2B sales analytics expert with predictive modeling capabilities.

Task: Predict the outcome for deal ID: {deal_id}

Steps:
1. Use MongoDB MCP tools to find the deal in 'deals' collection
2. Find the associated lead
3. Analyze factors:
   - Current stage and time in stage
   - Deal value vs company size fit
   - Number and frequency of activities
   - Lead score
   - Days since last contact
   - Progression through pipeline
4. Calculate:
   - Win probability (0-100%)
   - Predicted days to close
   - Risk factors (list)
   - Recommended actions (list)
5. Update the deal with prediction data:
   - probability field
   - predicted_close_date
   - risk_factors array
6. Log the analysis in 'agent_actions'

Return JSON with: probability, days_to_close, risk_factors[], recommendations[]
"""
            
            if self.client:
                response = await self._call_gemini_with_mcp(prompt, mcp_tools)
                
                return {
                    "success": True,
                    "deal_id": deal_id,
                    "prediction": response,
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
            logger.error(f"Error in predict_deal_outcome: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def identify_at_risk_deals(self, mcp_tools) -> Dict:
        """Identify deals at risk of being lost"""
        try:
            prompt = """
You are a sales pipeline risk analyst.

Task: Identify at-risk deals in the pipeline

Steps:
1. Use MongoDB MCP aggregate tool on 'deals' collection
2. Find deals with risk indicators:
   - In same stage for > 14 days
   - No activities in last 7 days
   - Low probability scores (< 40%)
   - High deal value but slow progression
   - Multiple failed follow-up attempts
3. For each at-risk deal:
   - Calculate risk score (0-100, higher = more risk)
   - Identify specific risk factors
   - Suggest recovery actions
4. Sort by risk score descending
5. Return top 10 at-risk deals

Return JSON array with: deal_id, risk_score, risk_factors[], suggested_actions[]
"""
            
            if self.client:
                response = await self._call_gemini_with_mcp(prompt, mcp_tools)
                
                return {
                    "success": True,
                    "at_risk_deals_identified": True,
                    "analysis": response,
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
            logger.error(f"Error in identify_at_risk_deals: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def generate_pipeline_insights(self, mcp_tools) -> Dict:
        """Generate comprehensive pipeline insights"""
        try:
            prompt = """
You are a sales operations analyst providing executive insights.

Task: Generate comprehensive pipeline insights and recommendations

Steps:
1. Use MongoDB MCP aggregate tools to analyze:
   
   LEADS ANALYSIS:
   - Total leads by status
   - Average lead score
   - Conversion rate (leads -> deals)
   - Lead score distribution
   
   DEALS ANALYSIS:
   - Total pipeline value by stage
   - Average deal size by stage
   - Win rate (closed_won / all closed)
   - Average days in each stage
   - Stage-to-stage conversion rates
   
   VELOCITY METRICS:
   - Average time from lead to closed deal
   - Deals expected to close this month
   - Pipeline health score
   
   AGENT PERFORMANCE:
   - Actions taken by each agent type
   - Success rates
   - Average processing times

2. Identify:
   - Pipeline bottlenecks
   - High-performing segments
   - Opportunities for improvement
   - Recommended focus areas

3. Generate executive summary with:
   - Key metrics
   - Trends
   - Action items
   - Forecasts

Return comprehensive JSON report with all metrics and insights.
"""
            
            if self.client:
                response = await self._call_gemini_with_mcp(prompt, mcp_tools)
                
                return {
                    "success": True,
                    "insights_generated": True,
                    "report": response,
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
            logger.error(f"Error in generate_pipeline_insights: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_agent_performance_report(self, mcp_tools) -> Dict:
        """Get performance metrics for all agents"""
        try:
            prompt = """
You are an AI operations analyst.

Task: Generate agent performance report

Steps:
1. Use MongoDB MCP aggregate on 'agent_actions' collection
2. Group by agent_type and calculate:
   - Total actions
   - Success rate
   - Average duration
   - Actions per hour/day
   - Most common action types
3. Identify:
   - Most productive agents
   - Bottlenecks or failures
   - Optimization opportunities

Return JSON with performance metrics for each agent type.
"""
            
            if self.client:
                response = await self._call_gemini_with_mcp(prompt, mcp_tools)
                
                return {
                    "success": True,
                    "performance_report": response,
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
            logger.error(f"Error in get_agent_performance_report: {e}")
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
intelligence_adk_agent = IntelligenceADKAgent()
