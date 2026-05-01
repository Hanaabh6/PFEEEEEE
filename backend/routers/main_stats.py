from fastapi import APIRouter, HTTPException, Request
from typing import Any

from ..base import things_collection, notifications_collection, user_history_collection

stats_router = APIRouter(tags=["stats"])


def _require_authenticated_user(request: Request):
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "").strip() if auth.startswith("Bearer ") else auth.strip()
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifie")
    return token


def _normalize_status(value: str) -> str:
    v = str(value or "").lower().strip()
    if v in ("active", "actif", "disponible"):
        return "active"
    if v in ("inactive", "inactif", "indisponible", "hors service", "hors-service", "hors ligne", "hors-ligne", "broken", "out of order", "hs"):
        return "inactive"
    if v in ("en_utilisation", "en utilisation", "borrowed", "emprunte"):
        return "en_utilisation"
    if v in ("panne", "en panne", "maintenance", "signale"):
        return "panne"
    return "autre"


@stats_router.get("/admin/stats/overview")
def get_overview_stats(request: Request):
    _require_authenticated_user(request)
    try:
        total = things_collection.count_documents({})
        active = things_collection.count_documents({
            "$or": [
                {"status": {"$in": ["active", "Active", "disponible", "Disponible"]}},
                {"availability": {"$in": ["active", "Active", "disponible", "Disponible"]}}
            ]
        })
        inactive = things_collection.count_documents({
            "$or": [
                {"status": {"$in": ["inactive", "Inactive", "indisponible", "hors service", "hors-service"]}},
                {"availability": {"$in": ["inactive", "Inactive", "indisponible", "hors service", "hors-service"]}}
            ]
        })
        
        # Objets en panne / maintenance
        broken = things_collection.count_documents({
            "$or": [
                {"maintenance_state": {"$exists": True, "$ne": ""}},
                {"status": {"$in": ["panne", "en panne", "maintenance"]}},
                {"availability": {"$in": ["panne", "en panne", "maintenance"]}}
            ]
        })
        
        # Objets actuellement empruntés
        borrowed = things_collection.count_documents({
            "$or": [
                {"current_borrow": {"$exists": True, "$ne": None}},
                {"status": "en_utilisation"},
                {"availability": "en_utilisation"}
            ]
        })
        
        # Signalements non lus / en attente
        notif_unread = notifications_collection.count_documents({
            "notif_type": "warning",
            "$or": [
                {"is_read": False},
                {"is_read": {"$exists": False}}
            ]
        })
        # Also include 'signalement' actions recorded in user_history_collection
        history_reports = user_history_collection.count_documents({
            "action": {"$regex": "signal|SIGNALEMENT", "$options": "i"}
        })
        pending_reports = notif_unread + history_reports
        
        # Total vues
        views_pipeline = [
            {"$group": {"_id": None, "total_views": {"$sum": "$view_count"}}}
        ]
        views_result = list(things_collection.aggregate(views_pipeline))
        total_views = views_result[0]["total_views"] if views_result else 0
        
        # Salles uniques
        rooms = things_collection.distinct("location.room")
        room_count = len([r for r in rooms if r])
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "broken": broken,
            "borrowed": borrowed,
            "pending_reports": pending_reports,
            "total_views": total_views,
            "rooms": room_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur stats overview: {e}")


@stats_router.get("/admin/stats/by-type")
def get_stats_by_type(request: Request):
    _require_authenticated_user(request)
    try:
        pipeline = [
            {"$match": {"type": {"$exists": True, "$ne": ""}}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        results = list(things_collection.aggregate(pipeline))
        return [{"type": r["_id"], "count": r["count"]} for r in results if r["_id"]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur stats by-type: {e}")


@stats_router.get("/admin/stats/by-status")
def get_stats_by_status(request: Request):
    _require_authenticated_user(request)
    try:
        items = list(things_collection.find({}, {"status": 1, "availability": 1, "maintenance_state": 1}))
        status_counts = {"active": 0, "inactive": 0, "en_utilisation": 0, "panne": 0, "autre": 0}
        
        for item in items:
            raw_status = item.get("status") or item.get("availability") or ""
            if item.get("maintenance_state"):
                status_counts["panne"] += 1
            else:
                normalized = _normalize_status(raw_status)
                status_counts[normalized] += 1
        
        return [{"status": k, "count": v} for k, v in status_counts.items() if v > 0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur stats by-status: {e}")


@stats_router.get("/admin/stats/top-viewed")
def get_top_viewed(request: Request, limit: int = 10):
    _require_authenticated_user(request)
    try:
        results = list(
            things_collection.find(
                {"view_count": {"$exists": True, "$gt": 0}}
            ).sort("view_count", -1).limit(limit)
        )
        return [
            {
                "id": str(r.get("id", "")),
                "name": r.get("name", "Sans nom"),
                "type": r.get("type", "Inconnu"),
                "view_count": r.get("view_count", 0)
            }
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur stats top-viewed: {e}")


@stats_router.get("/admin/stats/top-reported")
def get_top_reported(request: Request, limit: int = 10):
    _require_authenticated_user(request)
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        # Option 1: Query user_history_collection for signalements
        signalements_pipeline = [
            {"$match": {"action": "SIGNALEMENT_OBJET"}},
            {"$group": {
                "_id": "$thing_id",
                "thing_name": {"$first": "$thing_name"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        signalements_results = list(user_history_collection.aggregate(signalements_pipeline))
        
        # Option 2: Query things_collection for objects in maintenance/panne
        things_pipeline = [
            {"$match": {
                "$or": [
                    {"maintenance_state": {"$exists": True, "$ne": ""}},
                    {"maintenance_state": {"$exists": True, "$ne": None}},
                    {"status": {"$in": ["panne", "en panne", "maintenance", "broken", "hors service", "hs"]}},
                    {"availability": {"$in": ["panne", "en panne", "maintenance", "broken", "hors service", "hs"]}}
                ]
            }},
            {"$group": {
                "_id": "$id",
                "thing_name": {"$first": "$name"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        things_results = list(things_collection.aggregate(things_pipeline))
        
        logger.info(f"DEBUG top-reported: Signalements={len(signalements_results)}, Things maintenance={len(things_results)}")
        
        # Combine both sources - prefer signalements if available
        all_results = signalements_results + things_results
        
        # Deduplicate by thing_id, keeping signalement data over things data
        seen = {}
        for r in all_results:
            tid = r.get("_id") or r.get("thing_id")
            if tid and tid not in seen:
                seen[tid] = {
                    "thing_id": tid,
                    "thing_name": r.get("thing_name") or "Objet",
                    "count": r.get("count", 1)
                }
        
        combined = list(seen.values())[:limit]
        logger.info(f"DEBUG top-reported: Combined result count={len(combined)}")
        
        return combined
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur stats top-reported: {e}")


@stats_router.get("/admin/stats/borrow-stats")
def get_borrow_stats(request: Request):
    _require_authenticated_user(request)
    try:
        # Emprunts en cours
        current_borrows = things_collection.count_documents({
            "current_borrow": {"$exists": True, "$ne": None}
        })
        
        # Total emprunts historiques (depuis l'historique utilisateur)
        borrow_history = user_history_collection.count_documents({
            "action": {"$regex": "emprunt|borrow|take", "$options": "i"}
        })
        
        # Objets retournés (on compte les actions de retour)
        returned_count = user_history_collection.count_documents({
            "action": {"$regex": "retour|return|release", "$options": "i"}
        })
        
        return {
            "current": current_borrows,
            "total_history": borrow_history,
            "returned": returned_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur stats borrow: {e}")


@stats_router.get("/admin/stats/recent-activity")
def get_recent_activity(request: Request, limit: int = 20):
    _require_authenticated_user(request)
    try:
        results = list(
            user_history_collection.find()
            .sort("created_at", -1)
            .limit(limit)
        )
        return [
            {
                "id": str(r.get("_id", "")),
                "action": r.get("action", ""),
                "detail": r.get("detail", ""),
                "status": r.get("status", ""),
                "email": r.get("email", ""),
                "created_at": str(r.get("created_at", ""))
            }
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur stats recent-activity: {e}")


@stats_router.get("/admin/stats/notifications-count")
def get_admin_notifications_count(request: Request):
    _require_authenticated_user(request)
    try:
        unread = notifications_collection.count_documents({
            "notif_type": "warning",
            "$or": [
                {"is_read": False},
                {"is_read": {"$exists": False}}
            ]
        })
        return {"unread": unread}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur notifications count: {e}")