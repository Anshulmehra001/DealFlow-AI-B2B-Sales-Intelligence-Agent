"""
Intelligence Agent - Analyzes data and predicts outcomes
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from statistics import mean

from backend.services.mongodb_service import mongodb_service
from backend.services.gemini_service import gemini_service
from backend.models.agent_action import AgentType, ActionType, ActionStatus
from backend.models.deal import DealStage
from backend.config import settings

logger = logging.getLogger(__name__)


class IntelligenceAgent:
    """Agent responsible for analytics and predictions"""
    
    def __init__(self):
        self.agent_type = AgentType.INTELLIGENCE
        self.name = "Intelligence Agent"
    
    async def predict_deal_outcome(self, deal_id: str) -> Dict:
        """Predict deal close probability and date"""
        action_id = None
        
        try:
            # Log agent action
            action_id = await mongodb_service.log_agent_action({
                "agent_type": self.agent_type.value,
                "action_type": ActionType.DEAL_PREDICTION.value,
                "deal_id": deal_id,
                "status": ActionStatus.IN_PROGRESS.value
            })
            
            # Get deal data
            deal = await mongodb_service.get_deal(deal_id)
            if not deal:
                raise ValueError(f"Deal not found: {deal_id}")
            
            # Calculate prediction using both rule-based and AI
            prediction = await self._calculate_prediction(deal)
            
            # Get AI prediction for enhanced accuracy
            ai_prediction = await gemini_service.predict_deal_outcome({
                **deal,
                "days_in_stage": (datetime.utcnow() - deal["created_at"]).days,
                "days_since_contact": (datetime.utcnow() - deal.get("last_contact_date", datetime.utcnow())).days if deal.get("last_contact_date") else None
            })
            
            # Combine predictions (weighted average)
            final_probability = int((prediction["close_probability"] * 0.6) + (ai_prediction.get("probability", prediction["close_probability"]) * 0.4))
            
            prediction["close_probability"] = final_probability
            prediction["ai_insights"] = ai_prediction
            
            # Update deal with prediction
            await mongodb_service.update_deal(deal_id, {
                "predicted_close_date": prediction["predicted_close_date"],
                "predicted_value": prediction["predicted_value"],
                "risk_score": prediction["risk_score"]
            })
            
            # Log success
            if action_id:
                await mongodb_service.update_agent_action(action_id, {
                    "status": ActionStatus.SUCCESS.value,
                    "output_data": prediction,
                    "reasoning": prediction["reasoning"],
                    "completed_at": datetime.utcnow()
                })
            
            logger.info(f"Predicted outcome for deal {deal_id}: {prediction['close_probability']}%")
            
            return {
                "success": True,
                "deal_id": deal_id,
                **prediction
            }
            
        except Exception as e:
            logger.error(f"Failed to predict deal outcome: {e}")
            
            if action_id:
                await mongodb_service.update_agent_action(action_id, {
                    "status": ActionStatus.FAILED.value,
                    "error_message": str(e),
                    "completed_at": datetime.utcnow()
                })
            
            return {
                "success": False,
                "deal_id": deal_id,
                "error": str(e)
            }
    
    async def _calculate_prediction(self, deal: Dict) -> Dict:
        """Calculate deal prediction based on various factors"""
        # Base probability from stage
        stage_probabilities = {
            "new": 10,
            "contacted": 20,
            "qualified": 40,
            "proposal": 60,
            "negotiation": 80,
            "closed_won": 100,
            "closed_lost": 0
        }
        
        base_probability = stage_probabilities.get(deal["stage"], 0)
        
        # Adjust based on activity
        activity_count = len(deal.get("activities", []))
        activity_bonus = min(activity_count * 2, 20)  # Max 20% bonus
        
        # Adjust based on time in stage
        days_in_stage = (datetime.utcnow() - deal["created_at"]).days
        if days_in_stage > 30:
            time_penalty = -10  # Stale deal
        elif days_in_stage > 14:
            time_penalty = -5
        else:
            time_penalty = 0
        
        # Adjust based on last contact
        if deal.get("last_contact_date"):
            days_since_contact = (datetime.utcnow() - deal["last_contact_date"]).days
            if days_since_contact > 14:
                contact_penalty = -15
            elif days_since_contact > 7:
                contact_penalty = -5
            else:
                contact_penalty = 0
        else:
            contact_penalty = -10
        
        # Calculate final probability
        close_probability = base_probability + activity_bonus + time_penalty + contact_penalty
        close_probability = max(0, min(100, close_probability))  # Clamp to 0-100
        
        # Calculate risk score (inverse of probability)
        risk_score = 100 - close_probability
        
        # Predict close date
        stage_durations = {
            "new": 7,
            "contacted": 14,
            "qualified": 21,
            "proposal": 14,
            "negotiation": 21
        }
        
        days_to_close = stage_durations.get(deal["stage"], 30)
        predicted_close_date = datetime.utcnow() + timedelta(days=days_to_close)
        
        # Predicted value (could be adjusted based on negotiation stage)
        predicted_value = deal["deal_value"]
        if deal["stage"] == "negotiation":
            predicted_value *= 0.9  # Assume 10% discount in negotiation
        
        reasoning = f"Probability: {close_probability}% based on stage ({base_probability}%), " \
                   f"activity (+{activity_bonus}%), time penalty ({time_penalty}%), " \
                   f"contact penalty ({contact_penalty}%)"
        
        return {
            "close_probability": close_probability,
            "risk_score": risk_score,
            "predicted_close_date": predicted_close_date,
            "predicted_value": predicted_value,
            "reasoning": reasoning
        }
    
    async def identify_at_risk_deals(self) -> List[Dict]:
        """Identify deals that are at risk"""
        try:
            # Get all active deals
            deals = await mongodb_service.db["deals"].find({
                "stage": {"$nin": ["closed_won", "closed_lost"]}
            }).to_list(length=1000)
            
            at_risk_deals = []
            
            for deal in deals:
                # Check if deal needs attention
                risk_factors = []
                
                # No recent contact
                if deal.get("last_contact_date"):
                    days_since_contact = (datetime.utcnow() - deal["last_contact_date"]).days
                    if days_since_contact > 14:
                        risk_factors.append(f"No contact in {days_since_contact} days")
                
                # Stale deal
                days_in_stage = (datetime.utcnow() - deal["created_at"]).days
                if days_in_stage > 30:
                    risk_factors.append(f"In stage for {days_in_stage} days")
                
                # Low activity
                activity_count = len(deal.get("activities", []))
                if activity_count < 3:
                    risk_factors.append(f"Only {activity_count} activities")
                
                # Missed follow-up
                if deal.get("next_follow_up") and deal["next_follow_up"] < datetime.utcnow():
                    risk_factors.append("Missed follow-up")
                
                if risk_factors:
                    at_risk_deals.append({
                        "deal_id": str(deal["_id"]),
                        "deal_name": deal["deal_name"],
                        "deal_value": deal["deal_value"],
                        "stage": deal["stage"],
                        "risk_factors": risk_factors,
                        "risk_score": len(risk_factors) * 25  # Simple scoring
                    })
            
            # Sort by risk score
            at_risk_deals.sort(key=lambda x: x["risk_score"], reverse=True)
            
            logger.info(f"Identified {len(at_risk_deals)} at-risk deals")
            return at_risk_deals
            
        except Exception as e:
            logger.error(f"Failed to identify at-risk deals: {e}")
            return []
    
    async def generate_pipeline_insights(self) -> Dict:
        """Generate insights about the sales pipeline"""
        try:
            # Get pipeline stats
            pipeline_stats = await mongodb_service.get_pipeline_stats()
            
            # Calculate metrics
            total_deals = sum(stage["count"] for stage in pipeline_stats.values())
            total_value = sum(stage["total_value"] for stage in pipeline_stats.values())
            
            # Get weighted average probability
            weighted_prob = sum(
                stage["count"] * stage["avg_probability"]
                for stage in pipeline_stats.values()
            ) / total_deals if total_deals > 0 else 0
            
            # Identify bottlenecks
            bottlenecks = []
            for stage, stats in pipeline_stats.items():
                if stats["count"] > total_deals * 0.3:  # More than 30% in one stage
                    bottlenecks.append({
                        "stage": stage,
                        "count": stats["count"],
                        "percentage": (stats["count"] / total_deals * 100) if total_deals > 0 else 0
                    })
            
            # Get conversion rates
            conversion_rates = await self._calculate_conversion_rates()
            
            insights = {
                "total_deals": total_deals,
                "total_pipeline_value": total_value,
                "weighted_probability": weighted_prob,
                "expected_revenue": total_value * (weighted_prob / 100),
                "pipeline_by_stage": pipeline_stats,
                "bottlenecks": bottlenecks,
                "conversion_rates": conversion_rates,
                "generated_at": datetime.utcnow()
            }
            
            logger.info(f"Generated pipeline insights: {total_deals} deals, ${total_value:,.0f} value")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate pipeline insights: {e}")
            return {}
    
    async def _calculate_conversion_rates(self) -> Dict:
        """Calculate conversion rates between stages"""
        try:
            # This is a simplified version
            # In production, you'd track historical stage transitions
            
            all_deals = await mongodb_service.db["deals"].find({}).to_list(length=10000)
            
            stage_counts = {}
            for deal in all_deals:
                stage = deal["stage"]
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            # Calculate simple conversion rates
            stages = ["new", "contacted", "qualified", "proposal", "negotiation", "closed_won"]
            conversion_rates = {}
            
            for i in range(len(stages) - 1):
                current_stage = stages[i]
                next_stage = stages[i + 1]
                
                current_count = stage_counts.get(current_stage, 0)
                next_count = stage_counts.get(next_stage, 0)
                
                if current_count > 0:
                    rate = (next_count / current_count) * 100
                else:
                    rate = 0
                
                conversion_rates[f"{current_stage}_to_{next_stage}"] = round(rate, 2)
            
            return conversion_rates
            
        except Exception as e:
            logger.error(f"Failed to calculate conversion rates: {e}")
            return {}
    
    async def get_agent_performance_report(self) -> Dict:
        """Get performance report for all agents"""
        try:
            performance = await mongodb_service.get_agent_performance()
            
            report = {
                "agents": performance,
                "total_actions": sum(agent["total_actions"] for agent in performance),
                "overall_success_rate": mean([agent["success_rate"] for agent in performance]) if performance else 0,
                "generated_at": datetime.utcnow()
            }
            
            logger.info(f"Generated agent performance report: {report['total_actions']} total actions")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {}


# Global intelligence agent instance
intelligence_agent = IntelligenceAgent()
