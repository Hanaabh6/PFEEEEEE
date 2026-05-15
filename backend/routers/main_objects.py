import uuid
import unicodedata
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ..base import things_collection
from .main_auth import require_admin
from .main_localisation import canonical_room_name as _canonical_room_name, coords_from_room as _coords_from_room

objects_router = APIRouter(tags=["objects"])

# Templates d'objets (Stored locally in the backend as constants)
THING_TEMPLATES = {
    "lamp": {
        "type": "Eclairage",
        "description": "Système d'éclairage intelligent.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Smart Light",
            "properties": {"status": {"type": "string"}},
            "actions": {"on": {}, "off": {}}
        }
    },
    "microphone": {
        "type": "Microphone",
        "description": "Microphone de conférence ou mural.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Connected Microphone",
            "properties": {"mute": {"type": "boolean"}}
        }
    },
    "camera": {
        "type": "Caméra",
        "description": "Caméra de surveillance réseau.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Security Camera",
            "properties": {"stream": {"type": "string"}}
        }
    },
    "sensor": {
        "type": "Capteur",
        "description": "Capteur multi-fonction (température, humidité, présence).",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Smart Sensor",
            "properties": {"value": {"type": "number"}}
        }
    },
    "ac": {
        "type": "Climatiseur",
        "description": "Système de climatisation et chauffage.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "HVAC System",
            "properties": {"temperature": {"type": "number"}}
        }
    },
    "switch": {
        "type": "Interrupteur Connecte",
        "description": "Interrupteur ou commutateur intelligent.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Smart Switch",
            "actions": {"toggle": {}}
        }
    },
    "coffee": {
        "type": "machine a café",
        "description": "Distributeur ou machine à café connectée.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Coffee Machine",
            "actions": {"brew": {}}
        }
    },
    "tv": {
        "type": "Television",
        "description": "Écran d'affichage ou Smart TV.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Smart Display",
            "properties": {"volume": {"type": "integer"}}
        }
    },
    "scanner": {
        "type": "Scanner",
        "description": "Numériseur de documents réseau.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Network Scanner",
            "actions": {"scan": {}}
        }
    },
    "button": {
        "type": "Bouton",
        "description": "Bouton d'appel d'urgence ou sonnette.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Smart Button",
            "events": {"pressed": {}}
        }
    },
    "access": {
        "type": "Contrôle Accès",
        "description": "Lecteur de badge ou serrure connectée.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Access Control",
            "actions": {"unlock": {}}
        }
    },
    "alarm": {
        "type": "Alarme",
        "description": "Système d'alarme ou sirène incendie.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Smart Alarm",
            "actions": {"arm": {}, "disarm": {}}
        }
    },
    "printer": {
        "type": "Imprimante",
        "description": "Imprimante laser ou jet d'encre réseau.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Network Printer",
            "properties": {"inkLevel": {"type": "number"}}
        }
    },
    "speaker": {
        "type": "Haut-parleur",
        "description": "Enceinte audio ou haut-parleur d'annonce.",
        "thingDescription": {
            "@context": "https://www.w3.org/2019/wot/td/v1",
            "title": "Smart Speaker",
            "actions": {"play": {}, "stop": {}}
        }
    }
}

class AddObjectFromTemplateRequest(BaseModel):
    name: str
    location: str


def _normalize_text(text: str) -> str:
    if not text:
        return ""
    value = str(text).lower().strip()
    value = unicodedata.normalize("NFD", value)
    return "".join(ch for ch in value if unicodedata.category(ch) != "Mn")

@objects_router.post("/objects/add/{obj_type}")
def add_object_from_template(obj_type: str, data: AddObjectFromTemplateRequest, admin=Depends(require_admin)):
    """
    Implémente la création d'un objet via un template W3C TD prédéfini.
    """
    template = THING_TEMPLATES.get(obj_type.lower())
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    room_canonical = _canonical_room_name(data.location)
    coords = _coords_from_room(room_canonical)
    endpoint = template.get("endpoint", "")

    new_item = {
        "@context": "https://schema.org",
        "@type": "Product",
        "id": str(uuid.uuid4())[:8],
        "name": data.name,
        "search_name_norm": _normalize_text(data.name),
        "type": template["type"],
        "description": template.get("description", ""),
        "status": "disponible",
        "view_count": 0,
        "location": {
            "@type": "Place",
            "name": room_canonical,
            "room": room_canonical,
            "x": coords["x"],
            "y": coords["y"],
            "z": coords["z"],
        }
    }

    # Add optional semantic fields only if they exist in the project logic
    if "thingDescription" in template:
        new_item["thingDescription"] = template["thingDescription"]
    if "schemaMetadata" in template:
        new_item["schemaMetadata"] = template["schemaMetadata"]

    # Add control/actions ONLY if endpoint is defined (following your DB structure)
    if endpoint:
        new_item["control"] = {
            "@type": "EntryPoint",
            "name": "REST Control",
            "protocol": "REST",
            "contentType": "application/json",
            "endpoint": endpoint,
            "health": f"{endpoint}/health",
            "actions": {
                "on": {"method": "POST", "href": f"{endpoint}/actions/on"},
                "off": {"method": "POST", "href": f"{endpoint}/actions/off"}
            }
        }
        new_item["device_state"] = {
            "power": "off",
            "last_action_at": "",
            "reachable": True
        }
        new_item["potentialAction"] = [
            {
                "@type": "ActivateAction",
                "name": "on",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{endpoint}/actions/on",
                    "httpMethod": "POST",
                    "contentType": "application/json"
                }
            },
            {
                "@type": "DeactivateAction",
                "name": "off",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{endpoint}/actions/off",
                    "httpMethod": "POST",
                    "contentType": "application/json"
                }
            }
        ]

    try:
        things_collection.insert_one(new_item)
        # Import local to avoid circular deps if any
        from .main_crud import _reindex_thing
        _reindex_thing(new_item)
        
        return {
            "success": True,
            "message": f"Objet {data.name} ajouté avec succès",
            "id": new_item["id"]
        }
    except Exception as e:
        print(f"Error adding object: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de l'objet")
