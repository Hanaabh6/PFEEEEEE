from datetime import datetime, timedelta, timezone
import sys

from bson import ObjectId
from fastapi import APIRouter, Body, HTTPException, Query, Request
from pydantic import BaseModel, Field

from ..base import notifications_collection, user_history_collection, things_collection
from .main_auth import _get_user_from_token, extract_bearer_token, get_role_from_token, require_admin
from ..notifications_service import create_notification

notifications_router = APIRouter(tags=["notifications"])


class SendNotificationRequest(BaseModel):
    target_role: str = Field(..., min_length=4, max_length=10)
    title: str = Field(..., min_length=1, max_length=120)
    message: str = Field(..., min_length=1, max_length=500)
    notif_type: str = Field(default="info", max_length=30)
    recipient_user_id: str = Field(default="", max_length=120)
    recipient_email: str = Field(default="", max_length=254)


class MarkReadRequest(BaseModel):
    is_read: bool = True


class NearbyObjectRequest(BaseModel):
    thing_id: str = Field(..., min_length=1, max_length=120)
    thing_name: str = Field(..., min_length=1, max_length=160)
    room: str = Field(default="", max_length=120)
    distance_m: float = Field(default=0, ge=0, le=5000)


class ProblemReportRequest(BaseModel):
    thing_id: str = Field(..., min_length=1, max_length=120)
    thing_name: str = Field(..., min_length=1, max_length=160)
    problem_type: str = Field(..., min_length=1, max_length=80)
    description: str = Field(..., min_length=1, max_length=500)


def _main_module():
    return sys.modules.get("main")


def _notifications_collection():
    module = _main_module()
    return getattr(module, "notifications_collection", notifications_collection) if module else notifications_collection


def _require_authenticated_user(request: Request) -> tuple[str, str, str]:
    token = extract_bearer_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Token manquant")

    user = _get_user_from_token(token)
    role = get_role_from_token(token)
    return str(user.id), str(getattr(user, "email", "") or ""), str(role or "user")


def _is_notification_accessible(doc: dict, user_id: str, role: str) -> bool:
    target_role = str(doc.get("target_role") or "").strip().lower()
    recipient_user_id = str(doc.get("recipient_user_id") or "").strip()
    recipient_email = str(doc.get("recipient_email") or "").strip().lower()

    if role == "admin":
        return target_role in {"admin", "all"}

    if target_role not in {"user", "all"}:
        return False

    if not recipient_user_id:
        return True

    if recipient_user_id == user_id:
        return True

    user_email = str(doc.get("actor_email") or "").strip().lower()
    if recipient_email and user_email and recipient_email == user_email:
        return True

    return False


def _serialize_notification(doc: dict) -> dict:
    return {
        "id": str(doc.get("_id")),
        "target_role": doc.get("target_role", ""),
        "recipient_user_id": doc.get("recipient_user_id", ""),
        "title": doc.get("title", "Notification"),
        "message": doc.get("message", ""),
        "type": doc.get("type", "info"),
        "is_read": bool(doc.get("is_read", False)),
        "created_at": doc.get("created_at", ""),
        "updated_at": doc.get("updated_at", ""),
        "actor_user_id": doc.get("actor_user_id", ""),
        "actor_email": doc.get("actor_email", ""),
        "metadata": doc.get("metadata", {}),
    }


@notifications_router.get("/notifications/me")
def get_my_notifications(
    request: Request,
    only_unread: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
):
    user_id, user_email, role = _require_authenticated_user(request)
    collection = _notifications_collection()

    if role == "admin":
        query = {"target_role": {"$in": ["admin", "all"]}}
    else:
        query = {
            "target_role": {"$in": ["user", "all"]},
            "$or": [
                {"recipient_user_id": ""},
                {"recipient_user_id": {"$exists": False}},
                {"recipient_user_id": user_id},
                {"recipient_email": user_email},
            ],
        }

    if only_unread:
        query["is_read"] = False

    rows = list(collection.find(query).sort("created_at", -1).limit(limit))
    return [_serialize_notification(row) for row in rows]


@notifications_router.get("/notifications/count")
def get_notification_count(request: Request):
    user_id, user_email, role = _require_authenticated_user(request)
    collection = _notifications_collection()

    if role == "admin":
        query = {"target_role": {"$in": ["admin", "all"]}, "is_read": False}
    else:
        query = {
            "target_role": {"$in": ["user", "all"]},
            "is_read": False,
            "$or": [
                {"recipient_user_id": ""},
                {"recipient_user_id": {"$exists": False}},
                {"recipient_user_id": user_id},
                {"recipient_email": user_email},
            ],
        }

    unread = collection.count_documents(query)
    return {"unread": int(unread)}


@notifications_router.patch("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, request: Request, data: MarkReadRequest = Body(default=MarkReadRequest())):
    user_id, _, role = _require_authenticated_user(request)
    collection = _notifications_collection()

    try:
        object_id = ObjectId(notification_id)
    except Exception:
        raise HTTPException(status_code=400, detail="notification_id invalide")

    doc = collection.find_one({"_id": object_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    if not _is_notification_accessible(doc, user_id, role):
        raise HTTPException(status_code=403, detail="Notification non accessible")

    now = datetime.now(timezone.utc).isoformat()
    collection.update_one(
        {"_id": object_id},
        {"$set": {"is_read": bool(data.is_read), "updated_at": now}},
    )

    updated = collection.find_one({"_id": object_id}) or {}
    return {"success": True, "notification": _serialize_notification(updated)}


@notifications_router.patch("/notifications/read-all")
def mark_all_notifications_read(request: Request):
    user_id, user_email, role = _require_authenticated_user(request)
    collection = _notifications_collection()
    now = datetime.now(timezone.utc).isoformat()

    if role == "admin":
        query = {"target_role": {"$in": ["admin", "all"]}, "is_read": False}
    else:
        query = {
            "target_role": {"$in": ["user", "all"]},
            "is_read": False,
            "$or": [
                {"recipient_user_id": ""},
                {"recipient_user_id": {"$exists": False}},
                {"recipient_user_id": user_id},
                {"recipient_email": user_email},
            ],
        }

    result = collection.update_many(query, {"$set": {"is_read": True, "updated_at": now}})
    return {"success": True, "updated": int(result.modified_count)}


@notifications_router.post("/notifications/send")
def send_notification(request: Request, data: SendNotificationRequest = Body(...)):
    require_admin(request)
    _, admin_email, _ = _require_authenticated_user(request)

    target_role = str(data.target_role or "").strip().lower()
    if target_role not in {"admin", "user", "all"}:
        raise HTTPException(status_code=400, detail="target_role doit etre admin, user ou all")

    created_ids: list[str | None] = []
    if target_role == "all":
        created_ids.append(
            create_notification(
                target_role="admin",
                title=data.title,
                message=data.message,
                notif_type=data.notif_type,
                actor_email=admin_email,
            )
        )
        created_ids.append(
            create_notification(
                target_role="user",
                title=data.title,
                message=data.message,
                notif_type=data.notif_type,
                recipient_user_id=data.recipient_user_id,
                recipient_email=data.recipient_email,
                actor_email=admin_email,
            )
        )
    else:
        created_ids.append(
            create_notification(
                target_role=target_role,
                title=data.title,
                message=data.message,
                notif_type=data.notif_type,
                recipient_user_id=data.recipient_user_id if target_role == "user" else "",
                recipient_email=data.recipient_email if target_role == "user" else "",
                actor_email=admin_email,
            )
        )

    return {"success": True, "created_ids": [x for x in created_ids if x]}


@notifications_router.post("/notifications/nearby-object")
def notify_nearby_object(request: Request, data: NearbyObjectRequest = Body(...)):
    user_id, user_email, role = _require_authenticated_user(request)
    if role != "user":
        raise HTTPException(status_code=403, detail="Endpoint reserve aux users")

    collection = _notifications_collection()
    cooldown_since = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()

    existing = collection.find_one(
        {
            "target_role": "user",
            "recipient_user_id": user_id,
            "metadata.action": "nearby_object",
            "metadata.thing_id": data.thing_id,
            "created_at": {"$gte": cooldown_since},
        }
    )
    if existing:
        return {"success": True, "deduped": True, "id": str(existing.get("_id"))}

    room_label = str(data.room or "votre zone")
    distance_value = int(round(float(data.distance_m or 0)))
    created_id = create_notification(
        target_role="user",
        recipient_user_id=user_id,
        recipient_email=user_email,
        actor_user_id=user_id,
        actor_email=user_email,
        title="Objet proche de votre salle",
        message=f"{data.thing_name} est proche de {room_label} (environ {distance_value}m).",
        notif_type="info",
        metadata={
            "action": "nearby_object",
            "thing_id": data.thing_id,
            "room": room_label,
            "distance_m": distance_value,
        },
    )

    return {"success": True, "deduped": False, "id": created_id}


@notifications_router.post("/problem-report")
def submit_problem_report(request: Request, data: ProblemReportRequest = Body(...)):
    """Enregistrer un signalement d'objet et notifier tous les admins"""
    user_id, user_email, role = _require_authenticated_user(request)
    if role != "user":
        raise HTTPException(status_code=403, detail="Endpoint réservé aux utilisateurs")

    user_history = _user_history_collection()
    things = _things_collection()
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    thing_id = str(data.thing_id or "").strip()
    thing_name = str(data.thing_name or "Objet").strip()
    problem_type = str(data.problem_type or "").strip()
    description = str(data.description or "").strip()

    if not thing_id or not problem_type or not description:
        raise HTTPException(status_code=400, detail="Champs requis manquants")

    # Enregistrer le signalement dans user_history
    report_doc = {
        "user_id": user_id,
        "email": user_email,
        "action": "SIGNALEMENT_OBJET",
        "detail": f"Signalement: {problem_type}",
        "description": description,
        "status": "signale",
        "date": now.strftime("%d/%m/%Y %H:%M:%S"),
        "created_at": now_iso,
        "thing_id": thing_id,
        "thing_name": thing_name,
        "problem_type": problem_type,
    }

    result = user_history.insert_one(report_doc)
    report_id = str(result.inserted_id)

    # Créer notification pour TOUS les admins
    message = f"Signalement de {user_email}: {thing_name} - {problem_type}\n{description}"
    create_notification(
        target_role="admin",
        title=f"Nouveau signalement: {thing_name}",
        message=message,
        notif_type="warning",
        actor_user_id=user_id,
        actor_email=user_email,
        metadata={
            "action": "problem_report",
            "thing_id": thing_id,
            "problem_type": problem_type,
            "report_id": report_id,
        },
    )

    return {
        "success": True,
        "report_id": report_id,
        "message": "Signalement enregistré. Les administrateurs en ont été notifiés.",
    }


def _user_history_collection():
    module = _main_module()
    return getattr(module, "user_history_collection", user_history_collection) if module else user_history_collection


def _things_collection():
    module = _main_module()
    return getattr(module, "things_collection", things_collection) if module else things_collection


@notifications_router.get("/problem-reports")
def get_problem_reports(request: Request, limit: int = Query(default=50, ge=1, le=200)):
    """Récupérer les signalements (ses propres pour user, tous pour admin)"""
    user_id, user_email, role = _require_authenticated_user(request)
    user_history = _user_history_collection()

    if role == "admin":
        # Les admins voient TOUS les signalements
        query = {"action": "SIGNALEMENT_OBJET"}
    else:
        # Les users ne voient que les leurs
        query = {"action": "SIGNALEMENT_OBJET", "user_id": user_id}

    reports = list(user_history.find(query).sort("created_at", -1).limit(limit))
    
    serialized = []
    for report in reports:
        serialized.append({
            "id": str(report.get("_id")),
            "user_id": report.get("user_id", ""),
            "email": report.get("email", ""),
            "thing_id": report.get("thing_id", ""),
            "thing_name": report.get("thing_name", ""),
            "problem_type": report.get("problem_type", ""),
            "description": report.get("description", ""),
            "created_at": report.get("created_at", ""),
            "date": report.get("date", ""),
        })

    return {"success": True, "reports": serialized}
