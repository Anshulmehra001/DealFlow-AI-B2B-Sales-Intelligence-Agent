"""
Nurturing Agent - Automates follow-ups and manages pipeline
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from backend.services.mongodb_service import mongodb_service
from backend.services.email_service import email_service
from backend.services.gemini_service import gemini_service
from backend.models.agent_action import AgentType, ActionType, ActionStatus
from backend.models.deal import DealStage, ActivityType
from backend.config import settings

logger = logging.getLogger(__name__)


class NurturingAgent:
    """Agent responsible for nurturing leads and managing deals"""
    
    def __init__(self):
        self.agent_type = AgentType.NURTURING
        self.name = "Nurturing Agent"
    
    async def send_initial_outreach(self, lead_id: str) -> Dict:
        """Send initial outreach email to a lead"""
        action_id = None
        
        try:
            # Log agent action
            action_id = await mongodb_service.log_agent_action({
                "agent_type": self.agent_type.value,
                "action_type": ActionType.EMAIL_SENT.value,
                "lead_id": lead_id,
                "status": ActionStatus.IN_PROGRESS.value
            })
            
            # Get lead data
            lead = await mongodb_service.get_lead(lead_id)
            if not lead:
                raise ValueError(f"Lead not found: {lead_id}")
            
            if not lead.get("email"):
                raise ValueError("Lead has no email address")
            
            # Generate email content using Gemini
            email_content = await gemini_service.generate_email(
                company_name=lead["company_name"],
                contact_name=lead.get("contact_person", "there"),
                email_type="initial_outreach",
                context={
                    "industry": lead.get("industry"),
                    "company_size": lead.get("company_size")
                }
            )
            
            # Send email
            success = await email_service.send_email(
                to_email=lead["email"],
                subject=email_content["subject"],
                body_html=email_content["body_html"]
            )
            
            if not success:
                raise Exception("Failed to send email")
            
            # Update lead
            await mongodb_service.update_lead(lead_id, {
                "status": "contacted",
                "last_contacted_at": datetime.utcnow()
            })
            
            # Log success
            if action_id:
                await mongodb_service.update_agent_action(action_id, {
                    "status": ActionStatus.SUCCESS.value,
                    "output_data": {
                        "email_sent": True,
                        "subject": email_content["subject"]
                    },
                    "reasoning": "Initial outreach email sent successfully",
                    "completed_at": datetime.utcnow()
                })
            
            logger.info(f"Sent initial outreach to lead {lead_id}")
            
            return {
                "success": True,
                "lead_id": lead_id,
                "email_sent": True
            }
            
        except Exception as e:
            logger.error(f"Failed to send outreach to lead {lead_id}: {e}")
            
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
    
    async def send_follow_up(self, deal_id: str) -> Dict:
        """Send follow-up email for a deal"""
        try:
            # Get deal and lead data
            deal = await mongodb_service.get_deal(deal_id)
            if not deal:
                raise ValueError(f"Deal not found: {deal_id}")
            
            lead = await mongodb_service.get_lead(deal["lead_id"])
            if not lead or not lead.get("email"):
                raise ValueError("Lead not found or has no email")
            
            # Generate follow-up email using Gemini
            email_content = await gemini_service.generate_email(
                company_name=lead["company_name"],
                contact_name=lead.get("contact_person", "there"),
                email_type="follow_up",
                context={
                    "previous_context": "We discussed how our solution could help streamline your sales process"
                }
            )
            
            # Send email
            success = await email_service.send_email(
                to_email=lead["email"],
                subject=email_content["subject"],
                body_html=email_content["body_html"]
            )
            
            if success:
                # Log activity
                await mongodb_service.add_deal_activity(deal_id, {
                    "type": ActivityType.FOLLOW_UP.value,
                    "timestamp": datetime.utcnow(),
                    "description": "Follow-up email sent",
                    "outcome": "pending"
                })
                
                # Update next follow-up date
                await mongodb_service.update_deal(deal_id, {
                    "last_contact_date": datetime.utcnow(),
                    "next_follow_up": datetime.utcnow() + timedelta(days=7)
                })
            
            return {
                "success": success,
                "deal_id": deal_id,
                "email_sent": success
            }
            
        except Exception as e:
            logger.error(f"Failed to send follow-up for deal {deal_id}: {e}")
            return {
                "success": False,
                "deal_id": deal_id,
                "error": str(e)
            }
    
    async def check_follow_ups_needed(self) -> List[Dict]:
        """Check which deals need follow-up"""
        try:
            # Find deals that need follow-up
            now = datetime.utcnow()
            deals = await mongodb_service.db["deals"].find({
                "next_follow_up": {"$lte": now},
                "stage": {"$nin": [DealStage.CLOSED_WON.value, DealStage.CLOSED_LOST.value]}
            }).to_list(length=100)
            
            follow_ups_needed = []
            for deal in deals:
                follow_ups_needed.append({
                    "deal_id": str(deal["_id"]),
                    "deal_name": deal["deal_name"],
                    "days_since_contact": (now - deal.get("last_contact_date", now)).days,
                    "stage": deal["stage"]
                })
            
            logger.info(f"Found {len(follow_ups_needed)} deals needing follow-up")
            return follow_ups_needed
            
        except Exception as e:
            logger.error(f"Failed to check follow-ups: {e}")
            return []
    
    async def auto_follow_up_deals(self) -> Dict:
        """Automatically send follow-ups to deals that need them"""
        results = {
            "checked": 0,
            "sent": 0,
            "failed": 0
        }
        
        follow_ups = await self.check_follow_ups_needed()
        results["checked"] = len(follow_ups)
        
        for follow_up in follow_ups:
            result = await self.send_follow_up(follow_up["deal_id"])
            if result["success"]:
                results["sent"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Auto follow-up completed: {results['sent']} sent, {results['failed']} failed")
        return results
    
    async def move_deal_stage(self, deal_id: str, new_stage: DealStage, reason: str = "") -> Dict:
        """Move a deal to a new stage"""
        try:
            deal = await mongodb_service.get_deal(deal_id)
            if not deal:
                raise ValueError(f"Deal not found: {deal_id}")
            
            old_stage = deal["stage"]
            
            # Update deal stage
            await mongodb_service.update_deal(deal_id, {
                "stage": new_stage.value,
                "probability": self._get_stage_probability(new_stage)
            })
            
            # Log activity
            await mongodb_service.add_deal_activity(deal_id, {
                "type": ActivityType.STAGE_CHANGED.value,
                "timestamp": datetime.utcnow(),
                "description": f"Stage changed from {old_stage} to {new_stage.value}",
                "outcome": reason or "Stage progression"
            })
            
            logger.info(f"Moved deal {deal_id} from {old_stage} to {new_stage.value}")
            
            return {
                "success": True,
                "deal_id": deal_id,
                "old_stage": old_stage,
                "new_stage": new_stage.value
            }
            
        except Exception as e:
            logger.error(f"Failed to move deal stage: {e}")
            return {
                "success": False,
                "deal_id": deal_id,
                "error": str(e)
            }
    
    def _get_stage_probability(self, stage: DealStage) -> int:
        """Get default probability for a stage"""
        stage_probabilities = {
            DealStage.NEW: 10,
            DealStage.CONTACTED: 20,
            DealStage.QUALIFIED: 40,
            DealStage.PROPOSAL: 60,
            DealStage.NEGOTIATION: 80,
            DealStage.CLOSED_WON: 100,
            DealStage.CLOSED_LOST: 0
        }
        return stage_probabilities.get(stage, 0)
    
    async def send_proposal(self, deal_id: str) -> Dict:
        """Send proposal email for a deal"""
        try:
            deal = await mongodb_service.get_deal(deal_id)
            if not deal:
                raise ValueError(f"Deal not found: {deal_id}")
            
            lead = await mongodb_service.get_lead(deal["lead_id"])
            if not lead or not lead.get("email"):
                raise ValueError("Lead not found or has no email")
            
            # Generate proposal email using Gemini
            key_benefits = [
                "40% increase in sales efficiency",
                "Automated lead nurturing",
                "AI-powered insights",
                "24/7 support"
            ]
            
            email_content = await gemini_service.generate_email(
                company_name=lead["company_name"],
                contact_name=lead.get("contact_person", "there"),
                email_type="proposal",
                context={
                    "deal_value": deal["deal_value"],
                    "key_benefits": key_benefits
                }
            )
            
            # Send email
            success = await email_service.send_email(
                to_email=lead["email"],
                subject=email_content["subject"],
                body_html=email_content["body_html"]
            )
            
            if success:
                # Move to proposal stage
                await self.move_deal_stage(deal_id, DealStage.PROPOSAL, "Proposal sent")
                
                # Log activity
                await mongodb_service.add_deal_activity(deal_id, {
                    "type": ActivityType.PROPOSAL_SENT.value,
                    "timestamp": datetime.utcnow(),
                    "description": f"Proposal sent for ${deal['deal_value']:,.0f}",
                    "outcome": "pending"
                })
            
            return {
                "success": success,
                "deal_id": deal_id,
                "proposal_sent": success
            }
            
        except Exception as e:
            logger.error(f"Failed to send proposal for deal {deal_id}: {e}")
            return {
                "success": False,
                "deal_id": deal_id,
                "error": str(e)
            }


# Global nurturing agent instance
nurturing_agent = NurturingAgent()
