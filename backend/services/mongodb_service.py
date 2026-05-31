"""
MongoDB service — all database operations
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
from typing import List, Dict, Optional
from datetime import datetime
import logging

from backend.config import settings, Collections

logger = logging.getLogger(__name__)


class MongoDBService:

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=5000,
            )
            self.db = self.client[settings.MONGODB_DATABASE]
            await self.client.admin.command("ping")
            logger.info(f"MongoDB connected: {settings.MONGODB_DATABASE}")
            await self._create_indexes()
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")

    async def _create_indexes(self):
        try:
            # Leads
            await self.db[Collections.LEADS].create_index([("company_name", ASCENDING)])
            await self.db[Collections.LEADS].create_index([("email", ASCENDING)])
            await self.db[Collections.LEADS].create_index([("lead_score", DESCENDING)])
            await self.db[Collections.LEADS].create_index([("status", ASCENDING)])
            await self.db[Collections.LEADS].create_index([("created_at", DESCENDING)])
            # Deals
            await self.db[Collections.DEALS].create_index([("lead_id", ASCENDING)])
            await self.db[Collections.DEALS].create_index([("stage", ASCENDING)])
            await self.db[Collections.DEALS].create_index([("probability", DESCENDING)])
            await self.db[Collections.DEALS].create_index([("created_at", DESCENDING)])
            await self.db[Collections.DEALS].create_index([("next_follow_up", ASCENDING)])
            # Agent actions
            await self.db[Collections.AGENT_ACTIONS].create_index([("agent_type", ASCENDING)])
            await self.db[Collections.AGENT_ACTIONS].create_index([("lead_id", ASCENDING)])
            await self.db[Collections.AGENT_ACTIONS].create_index([("started_at", DESCENDING)])
            logger.info("Indexes created")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _to_str_id(self, doc: Dict) -> Dict:
        """Convert ObjectId _id to string in-place."""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    # ── Leads ─────────────────────────────────────────────────────────────────

    async def create_lead(self, data: Dict) -> str:
        data.setdefault("created_at", datetime.utcnow())
        data.setdefault("updated_at", datetime.utcnow())
        data.setdefault("lead_score", 0)
        data.setdefault("status", "new")
        result = await self.db[Collections.LEADS].insert_one(data)
        return str(result.inserted_id)

    async def get_lead(self, lead_id: str) -> Optional[Dict]:
        try:
            doc = await self.db[Collections.LEADS].find_one({"_id": ObjectId(lead_id)})
            return self._to_str_id(doc) if doc else None
        except Exception:
            return None

    async def update_lead(self, lead_id: str, data: Dict) -> bool:
        try:
            data["updated_at"] = datetime.utcnow()
            result = await self.db[Collections.LEADS].update_one(
                {"_id": ObjectId(lead_id)}, {"$set": data}
            )
            return result.modified_count > 0
        except Exception:
            return False

    async def list_leads(self, skip: int = 0, limit: int = 100, filters: Dict = None) -> List[Dict]:
        query = filters or {}
        cursor = (
            self.db[Collections.LEADS]
            .find(query)
            .skip(skip)
            .limit(limit)
            .sort("created_at", DESCENDING)
        )
        docs = await cursor.to_list(length=limit)
        return [self._to_str_id(d) for d in docs]

    async def count_leads(self, filters: Dict = None) -> int:
        return await self.db[Collections.LEADS].count_documents(filters or {})

    # ── Deals ─────────────────────────────────────────────────────────────────

    async def create_deal(self, data: Dict) -> str:
        data.setdefault("created_at", datetime.utcnow())
        data.setdefault("updated_at", datetime.utcnow())
        data.setdefault("activities", [])
        data.setdefault("probability", 10)
        result = await self.db[Collections.DEALS].insert_one(data)
        return str(result.inserted_id)

    async def get_deal(self, deal_id: str) -> Optional[Dict]:
        try:
            doc = await self.db[Collections.DEALS].find_one({"_id": ObjectId(deal_id)})
            return self._to_str_id(doc) if doc else None
        except Exception:
            return None

    async def update_deal(self, deal_id: str, data: Dict) -> bool:
        try:
            data["updated_at"] = datetime.utcnow()
            result = await self.db[Collections.DEALS].update_one(
                {"_id": ObjectId(deal_id)}, {"$set": data}
            )
            return result.modified_count > 0
        except Exception:
            return False

    async def list_deals(self, skip: int = 0, limit: int = 100, filters: Dict = None) -> List[Dict]:
        query = filters or {}
        cursor = (
            self.db[Collections.DEALS]
            .find(query)
            .skip(skip)
            .limit(limit)
            .sort("created_at", DESCENDING)
        )
        docs = await cursor.to_list(length=limit)
        return [self._to_str_id(d) for d in docs]

    async def count_deals(self, filters: Dict = None) -> int:
        return await self.db[Collections.DEALS].count_documents(filters or {})

    async def add_deal_activity(self, deal_id: str, activity: Dict) -> bool:
        try:
            result = await self.db[Collections.DEALS].update_one(
                {"_id": ObjectId(deal_id)},
                {
                    "$push": {"activities": activity},
                    "$set": {"updated_at": datetime.utcnow()},
                },
            )
            return result.modified_count > 0
        except Exception:
            return False

    # ── Agent Actions ─────────────────────────────────────────────────────────

    async def log_agent_action(self, data: Dict) -> str:
        data.setdefault("started_at", datetime.utcnow())
        result = await self.db[Collections.AGENT_ACTIONS].insert_one(data)
        return str(result.inserted_id)

    async def update_agent_action(self, action_id: str, data: Dict) -> bool:
        try:
            result = await self.db[Collections.AGENT_ACTIONS].update_one(
                {"_id": ObjectId(action_id)}, {"$set": data}
            )
            return result.modified_count > 0
        except Exception:
            return False

    async def list_agent_actions(self, limit: int = 50) -> List[Dict]:
        cursor = (
            self.db[Collections.AGENT_ACTIONS]
            .find({})
            .sort("started_at", DESCENDING)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._to_str_id(d) for d in docs]

    # ── Analytics ─────────────────────────────────────────────────────────────

    async def get_pipeline_stats(self) -> Dict:
        pipeline = [
            {
                "$group": {
                    "_id": "$stage",
                    "count": {"$sum": 1},
                    "total_value": {"$sum": "$deal_value"},
                    "avg_probability": {"$avg": "$probability"},
                }
            }
        ]
        cursor = self.db[Collections.DEALS].aggregate(pipeline)
        results = await cursor.to_list(length=None)
        return {item["_id"]: {
            "count": item["count"],
            "total_value": item["total_value"],
            "avg_probability": round(item["avg_probability"] or 0, 1),
        } for item in results}

    async def get_lead_score_distribution(self) -> List[Dict]:
        pipeline = [
            {
                "$bucket": {
                    "groupBy": "$lead_score",
                    "boundaries": [0, 25, 50, 75, 101],
                    "default": "other",
                    "output": {"count": {"$sum": 1}},
                }
            }
        ]
        cursor = self.db[Collections.LEADS].aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def get_agent_performance(self) -> List[Dict]:
        pipeline = [
            {
                "$group": {
                    "_id": "$agent_type",
                    "total": {"$sum": 1},
                    "success": {
                        "$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                    },
                    "failed": {
                        "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                    },
                    "avg_duration": {"$avg": "$duration_seconds"},
                }
            }
        ]
        cursor = self.db[Collections.AGENT_ACTIONS].aggregate(pipeline)
        results = await cursor.to_list(length=None)
        for r in results:
            r["success_rate"] = round((r["success"] / r["total"]) * 100, 1) if r["total"] else 0
        return results

    async def get_summary_stats(self) -> Dict:
        """Dashboard summary stats"""
        total_leads = await self.count_leads()
        qualified_leads = await self.count_leads({"status": "qualified"})
        total_deals = await self.count_deals()

        # Total pipeline value
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$deal_value"}}}]
        cursor = self.db[Collections.DEALS].aggregate(pipeline)
        result = await cursor.to_list(length=1)
        pipeline_value = result[0]["total"] if result else 0

        # Won deals value
        pipeline_won = [
            {"$match": {"stage": "closed_won"}},
            {"$group": {"_id": None, "total": {"$sum": "$deal_value"}}},
        ]
        cursor = self.db[Collections.DEALS].aggregate(pipeline_won)
        result = await cursor.to_list(length=1)
        won_value = result[0]["total"] if result else 0

        return {
            "total_leads": total_leads,
            "qualified_leads": qualified_leads,
            "total_deals": total_deals,
            "pipeline_value": pipeline_value,
            "won_value": won_value,
        }


# Global instance
mongodb_service = MongoDBService()
