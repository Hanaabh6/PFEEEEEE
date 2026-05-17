from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import httpx
from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import BaseModel, Field

from ..base import things_collection
from ..config import WOT_CATALOG_TIMEOUT_SECONDS, WOT_TD_CATALOG_URL
from ..notifications_service import create_notification
from ..wot_catalog_data import get_catalog_td, list_td_summaries, summarize_td
from .main_auth import require_admin
from .main_crud import _find_thing_with_same_name, _normalize_text, _reindex_thing
from .main_localisation import ARCHI_DATA, ROOM_DATA, canonical_room_name, coords_from_room


wot_router = APIRouter(tags=["wot"])


class AddThingFromTdRequest(BaseModel):
    td_id: str = Field(..., min_length=1, max_length=160)
    local_name: str = Field(..., min_length=1, max_length=120)
    room: str = Field(..., min_length=1, max_length=120)
    floor: str = Field(default="", max_length=120)


def _catalog_base_url() -> str:
    return str(WOT_TD_CATALOG_URL or "").strip().rstrip("/")


def _external_get(path: str) -> tuple[Any, str]:
    base_url = _catalog_base_url()
    if not base_url:
        raise RuntimeError("Aucun catalogue WoT externe configure")

    url = f"{base_url}{path}"
    with httpx.Client(timeout=WOT_CATALOG_TIMEOUT_SECONDS) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json(), str(response.url)


def _summary_from_payload_item(item: dict[str, Any], source_url: str = "") -> dict[str, Any]:
    td_id = str(item.get("td_id") or item.get("id") or item.get("wot_id") or "").strip()
    td = item.get("thingDescription") or item.get("td")
    if isinstance(td, dict):
        return summarize_td(td_id or str(td.get("id") or ""), td, source_url=source_url or str(item.get("source_url") or ""))

    return {
        "td_id": td_id,
        "wot_id": str(item.get("wot_id") or "").strip(),
        "title": str(item.get("title") or item.get("name") or td_id).strip(),
        "name": str(item.get("name") or item.get("title") or td_id).strip(),
        "type": str(item.get("type") or item.get("category") or "Objet IoT").strip(),
        "description": str(item.get("description") or "").strip(),
        "properties": item.get("properties") if isinstance(item.get("properties"), list) else [],
        "actions": item.get("actions") if isinstance(item.get("actions"), list) else [],
        "events": item.get("events") if isinstance(item.get("events"), list) else [],
        "source_url": source_url or str(item.get("source_url") or "").strip(),
    }


def _catalog_from_external() -> dict[str, Any]:
    payload, _ = _external_get("/td-catalog")
    raw_items = payload.get("items") if isinstance(payload, dict) else payload
    if not isinstance(raw_items, list):
        raise RuntimeError("Format catalogue WoT invalide")

    items = []
    for raw_item in raw_items:
        if isinstance(raw_item, dict):
            summary = _summary_from_payload_item(raw_item)
            if summary.get("td_id"):
                items.append(summary)

    return {
        "source": "external",
        "catalog_url": _catalog_base_url(),
        "items": items,
    }


def _catalog_from_local(fallback_reason: str = "") -> dict[str, Any]:
    return {
        "source": "bundled",
        "catalog_url": "backend.wot_catalog_data",
        "fallback_reason": fallback_reason,
        "items": list_td_summaries(),
    }


def _td_from_external(td_id: str) -> dict[str, Any]:
    safe_id = quote(str(td_id or "").strip(), safe="")
    payload, source_url = _external_get(f"/td-catalog/{safe_id}")
    if not isinstance(payload, dict):
        raise RuntimeError("Format Thing Description invalide")

    td = payload.get("thingDescription") or payload.get("td")
    if not isinstance(td, dict) and "@context" in payload:
        td = payload
    if not isinstance(td, dict):
        raise RuntimeError("Thing Description absente du payload WoT")

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        summary = summarize_td(str(td_id), td, source_url=source_url)
    else:
        summary = _summary_from_payload_item(summary, source_url=source_url)
        summary["source_url"] = summary.get("source_url") or source_url

    return {
        "source": "external",
        "catalog_url": _catalog_base_url(),
        "summary": summary,
        "thingDescription": td,
    }


def _td_from_local(td_id: str, fallback_reason: str = "") -> dict[str, Any]:
    td = get_catalog_td(td_id)
    if not td:
        raise HTTPException(status_code=404, detail="Thing Description introuvable")
    summary = summarize_td(td_id, td, source_url=f"/td-catalog/{td_id}")
    return {
        "source": "bundled",
        "catalog_url": "backend.wot_catalog_data",
        "fallback_reason": fallback_reason,
        "summary": summary,
        "thingDescription": td,
    }


def _resolve_td(td_id: str) -> dict[str, Any]:
    fallback_reason = ""
    if _catalog_base_url():
        try:
            return _td_from_external(td_id)
        except httpx.HTTPStatusError as exc:
            fallback_reason = f"Catalogue WoT externe indisponible ({exc.response.status_code})"
        except Exception as exc:
            fallback_reason = f"Catalogue WoT externe indisponible ({exc})"

    return _td_from_local(td_id, fallback_reason=fallback_reason)


def _list_names(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [str(key).strip() for key in value.keys() if str(key).strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _first_form(entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        return {}
    forms = entry.get("forms")
    if isinstance(forms, list):
        for form in forms:
            if isinstance(form, dict):
                return form
    return {}


def _build_potential_actions_from_td(td: dict[str, Any]) -> list[dict[str, Any]]:
    actions = td.get("actions") if isinstance(td.get("actions"), dict) else {}
    result: list[dict[str, Any]] = []

    for action_name, action_spec in actions.items():
        safe_name = str(action_name or "").strip()
        if not safe_name:
            continue

        form = _first_form(action_spec)
        target = {
            "@type": "EntryPoint",
            "urlTemplate": str(form.get("href") or "").strip(),
            "httpMethod": str(form.get("htv:methodName") or form.get("method") or "POST").strip().upper(),
            "contentType": str(form.get("contentType") or "application/json").strip(),
        }
        result.append(
            {
                "@type": "Action",
                "name": safe_name,
                "description": str(action_spec.get("description") or "").strip() if isinstance(action_spec, dict) else "",
                "target": target,
            }
        )

    return result


def _build_control_from_td(td: dict[str, Any], simulated: bool = False) -> dict[str, Any] | None:
    actions = td.get("actions") if isinstance(td.get("actions"), dict) else {}
    if not actions:
        return None

    control_actions: dict[str, dict[str, Any]] = {}
    first_href = ""
    for action_name, action_spec in actions.items():
        safe_name = str(action_name or "").strip()
        if not safe_name:
            continue

        form = _first_form(action_spec)
        href = str(form.get("href") or "").strip()
        method = str(form.get("htv:methodName") or form.get("method") or "POST").strip().upper()
        if not href:
            continue

        if not first_href:
            first_href = href

        control_actions[safe_name.lower()] = {
            "method": method,
            "href": href,
            "label": safe_name,
            "contentType": str(form.get("contentType") or "application/json").strip(),
        }

    if not control_actions:
        return None

    return {
        "@type": "EntryPoint",
        "name": "WoT TD Control",
        "protocol": "WoT/HTTP",
        "contentType": "application/json",
        "endpoint": first_href,
        "health": first_href,
        "simulated": bool(simulated),
        "actions": control_actions,
    }


def _floor_for_room(room: str) -> str:
    room_norm = _normalize_text(room)
    for floor in ARCHI_DATA:
        rooms = floor.get("rooms") if isinstance(floor, dict) else []
        if any(_normalize_text(str(item)) == room_norm for item in rooms):
            return str(floor.get("name") or "").strip()
    return ""


def _resolve_known_room(room: str) -> tuple[str, dict[str, float], str]:
    room_canonical = canonical_room_name(str(room or "").strip())
    if not room_canonical or room_canonical not in ROOM_DATA:
        raise HTTPException(status_code=400, detail="Salle invalide. Veuillez choisir une salle existante.")
    return room_canonical, coords_from_room(room_canonical), _floor_for_room(room_canonical)


def _prepare_for_things_insert(item: dict[str, Any]) -> dict[str, Any]:
    # La collection things existante valide parfois created_at/updated_at comme strings.
    # Ces champs ne sont pas requis pour l'ajout WoT; on les retire pour rester compatible
    # avec les bases deja deployees.
    clean_item = dict(item)
    clean_item.pop("created_at", None)
    clean_item.pop("updated_at", None)
    return clean_item


@wot_router.get("/wot/things")
def list_wot_things(request: Request):
    require_admin(request)
    if _catalog_base_url():
        try:
            return _catalog_from_external()
        except Exception as exc:
            return _catalog_from_local(fallback_reason=str(exc))
    return _catalog_from_local()


@wot_router.get("/wot/things/{td_id}/td")
def get_wot_thing_description(td_id: str, request: Request):
    require_admin(request)
    return _resolve_td(td_id)


@wot_router.post("/things/from-td")
def add_thing_from_td(request: Request, data: AddThingFromTdRequest = Body(...)):
    require_admin(request)

    safe_name = str(data.local_name or "").strip()
    if not safe_name:
        raise HTTPException(status_code=400, detail="Le nom local de l'objet est obligatoire.")

    duplicate = _find_thing_with_same_name(safe_name)
    if duplicate:
        duplicate_name = str(duplicate.get("name") or safe_name).strip() or safe_name
        raise HTTPException(status_code=409, detail=f"Un objet avec le nom '{duplicate_name}' existe deja.")

    room_canonical, coords, inferred_floor = _resolve_known_room(data.room)
    safe_floor = str(data.floor or "").strip()
    floor_label = inferred_floor or safe_floor

    td_payload = _resolve_td(data.td_id)
    td = td_payload["thingDescription"]
    summary = td_payload["summary"]
    now_iso = datetime.now(timezone.utc).isoformat()

    properties = _list_names(td.get("properties"))
    actions = _list_names(td.get("actions"))
    events = _list_names(td.get("events"))
    thing_type = str(summary.get("type") or "Objet IoT").strip() or "Objet IoT"
    description = str(summary.get("description") or td.get("description") or "").strip()

    td_summary = {
        "td_id": str(summary.get("td_id") or data.td_id).strip(),
        "wot_id": str(summary.get("wot_id") or td.get("id") or "").strip(),
        "title": str(summary.get("title") or td.get("title") or "").strip(),
        "name": str(summary.get("name") or td.get("name") or summary.get("title") or "").strip(),
        "type": thing_type,
        "description": description,
        "properties": properties,
        "actions": actions,
        "events": events,
        "source": td_payload.get("source", ""),
        "source_url": str(summary.get("source_url") or "").strip(),
        "retrieved_at": now_iso,
    }

    new_item = {
        "@context": "https://schema.org",
        "@type": "Product",
        "id": str(uuid.uuid4())[:8],
        "name": safe_name,
        "search_name_norm": _normalize_text(safe_name),
        "type": thing_type,
        "description": description,
        "status": "disponible",
        "view_count": 0,
        "location": {
            "@type": "Place",
            "name": room_canonical,
            "room": room_canonical,
            "floor": floor_label,
            "etage": floor_label,
            "x": coords["x"],
            "y": coords["y"],
            "z": coords["z"],
        },
        "thingDescription": td,
        "td_summary": td_summary,
    }

    potential_actions = _build_potential_actions_from_td(td)
    if potential_actions:
        new_item["potentialAction"] = potential_actions

    remote_control = _build_control_from_td(td, simulated=td_payload.get("source") == "bundled")
    if remote_control:
        new_item["control"] = remote_control
        new_item["device_state"] = {
            "power": "off",
            "last_action_at": "",
            "reachable": True,
        }

    new_item = _prepare_for_things_insert(new_item)

    try:
        things_collection.insert_one(new_item)
        _reindex_thing(new_item)
        create_notification(
            target_role="admin",
            title="Objet WoT ajoute",
            message=f"Objet ajoute depuis TD: {new_item['name']} ({new_item['id']}).",
            notif_type="success",
            metadata={"thing_id": new_item["id"], "action": "add_from_td", "td_id": td_summary["td_id"]},
        )
        return {
            "success": True,
            "message": f"Objet {safe_name} ajoute depuis sa Thing Description",
            "id": new_item["id"],
            "td_id": td_summary["td_id"],
        }
    except Exception as exc:
        print(f"Erreur add from TD: {exc}")
        raise HTTPException(status_code=500, detail="Impossible d'ajouter l'objet depuis la Thing Description.")
