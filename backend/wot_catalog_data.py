from __future__ import annotations

from copy import deepcopy
from typing import Any


TD_CATALOG: list[dict[str, Any]] = [
    {
        "td_id": "smart-light-001",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:smart-light-001",
            "title": "Luminaire LED intelligent",
            "name": "Luminaire LED intelligent",
            "description": "Point d'eclairage connecte compatible avec le controle d'intensite.",
            "@type": "Product",
            "category": "Eclairage",
            "securityDefinitions": {
                "nosec_sc": {"scheme": "nosec"},
            },
            "security": ["nosec_sc"],
            "properties": {
                "status": {
                    "type": "string",
                    "readOnly": True,
                    "description": "Etat courant du luminaire.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/light-001/properties/status",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "brightness": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Niveau d'intensite lumineuse.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/light-001/properties/brightness",
                            "op": ["readproperty", "writeproperty"],
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "on": {
                    "description": "Allumer le luminaire.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/light-001/actions/on",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "off": {
                    "description": "Eteindre le luminaire.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/light-001/actions/off",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "setBrightness": {
                    "description": "Modifier l'intensite lumineuse.",
                    "input": {
                        "type": "object",
                        "properties": {"value": {"type": "integer", "minimum": 0, "maximum": 100}},
                    },
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/light-001/actions/setBrightness",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
        },
    },
    {
        "td_id": "climate-sensor-002",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:climate-sensor-002",
            "title": "Capteur environnemental",
            "name": "Capteur environnemental",
            "description": "Capteur IoT mesurant temperature, humidite et presence.",
            "@type": "Product",
            "category": "Capteur",
            "securityDefinitions": {
                "bearer_sc": {"scheme": "bearer", "format": "jwt", "in": "header"},
            },
            "security": ["bearer_sc"],
            "properties": {
                "temperature": {
                    "type": "number",
                    "readOnly": True,
                    "unit": "degree celsius",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/sensor-002/properties/temperature",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "humidity": {
                    "type": "number",
                    "readOnly": True,
                    "unit": "percent",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/sensor-002/properties/humidity",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "presence": {
                    "type": "boolean",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/sensor-002/properties/presence",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "calibrate": {
                    "description": "Lancer une calibration du capteur.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/sensor-002/actions/calibrate",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                }
            },
        },
    },
    {
        "td_id": "smart-tv-003",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:smart-tv-003",
            "title": "Smart TV collaborative",
            "name": "Smart TV collaborative",
            "description": "Ecran connecte pour affichage, reunion et diffusion multimedia.",
            "@type": "Product",
            "category": "Television",
            "securityDefinitions": {
                "nosec_sc": {"scheme": "nosec"},
            },
            "security": ["nosec_sc"],
            "properties": {
                "status": {
                    "type": "string",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/status",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "volume": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/volume",
                            "op": ["readproperty", "writeproperty"],
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "on": {
                    "description": "Allumer la Smart TV.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/on",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "off": {
                    "description": "Eteindre la Smart TV.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/off",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "play": {
                    "description": "Demarrer la lecture multimedia.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/play",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "prev": {
                    "description": "Revenir au contenu precedent.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/prev",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "next": {
                    "description": "Passer au contenu suivant.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/next",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "volume-up": {
                    "description": "Augmenter le volume.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/volume-up",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "volume-down": {
                    "description": "Reduire le volume.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/volume-down",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "mute": {
                    "description": "Activer ou desactiver le son.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/mute",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "channels": {
                    "description": "Lister les chaines disponibles.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/tv-003/channels",
                            "op": "invokeaction",
                            "htv:methodName": "GET",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
        },
    },
    {
        "td_id": "access-reader-004",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:access-reader-004",
            "title": "Lecteur de badge securise",
            "name": "Lecteur de badge securise",
            "description": "Objet IoT de controle d'acces pour zones securisees.",
            "@type": "Product",
            "category": "Controle Acces",
            "securityDefinitions": {
                "bearer_sc": {"scheme": "bearer", "format": "jwt", "in": "header"},
            },
            "security": ["bearer_sc"],
            "properties": {
                "locked": {
                    "type": "boolean",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/access-004/properties/locked",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "lastBadge": {
                    "type": "string",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/access-004/properties/lastBadge",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "unlock": {
                    "description": "Ouvrir temporairement l'acces.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/access-004/actions/unlock",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "lock": {
                    "description": "Verrouiller l'acces.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/access-004/actions/lock",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
        },
    },
    {
        "td_id": "network-printer-005",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:network-printer-005",
            "title": "Imprimante reseau",
            "name": "Imprimante reseau",
            "description": "Imprimante connectee exposee via une Thing Description.",
            "@type": "Product",
            "category": "Imprimante",
            "securityDefinitions": {
                "nosec_sc": {"scheme": "nosec"},
            },
            "security": ["nosec_sc"],
            "properties": {
                "status": {
                    "type": "string",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/printer-005/properties/status",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "inkLevel": {
                    "type": "number",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/printer-005/properties/inkLevel",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "on": {
                    "description": "Mettre l'imprimante en service.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/printer-005/actions/on",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "off": {
                    "description": "Mettre l'imprimante en veille.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/printer-005/actions/off",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "printTestPage": {
                    "description": "Imprimer une page de test.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/printer-005/actions/printTestPage",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                }
            },
        },
    },
]


def _keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        return list(value.keys())
    return []


def extract_td_type(td: dict[str, Any]) -> str:
    category = str(td.get("category") or "").strip()
    if category:
        return category

    type_value = td.get("@type")
    if isinstance(type_value, list):
        for item in type_value:
            clean = str(item or "").strip()
            if clean and clean.lower() not in {"product", "thing"}:
                return clean
    elif isinstance(type_value, str) and type_value.strip().lower() not in {"product", "thing"}:
        return type_value.strip()

    return "Objet IoT"


def summarize_td(td_id: str, td: dict[str, Any], source_url: str = "") -> dict[str, Any]:
    title = str(td.get("title") or td.get("name") or td_id).strip()
    description = str(td.get("description") or "").strip()
    return {
        "td_id": td_id,
        "wot_id": str(td.get("id") or "").strip(),
        "title": title,
        "name": str(td.get("name") or title).strip(),
        "type": extract_td_type(td),
        "description": description,
        "properties": _keys(td.get("properties")),
        "actions": _keys(td.get("actions")),
        "events": _keys(td.get("events")),
        "source_url": source_url,
    }


def list_td_summaries(base_url: str = "") -> list[dict[str, Any]]:
    clean_base = base_url.rstrip("/")
    summaries = []
    for item in TD_CATALOG:
        td_id = str(item["td_id"])
        source_url = f"{clean_base}/td-catalog/{td_id}" if clean_base else f"/td-catalog/{td_id}"
        summaries.append(summarize_td(td_id, item["td"], source_url=source_url))
    return summaries


def get_catalog_td(td_id: str) -> dict[str, Any] | None:
    safe_id = str(td_id or "").strip()
    for item in TD_CATALOG:
        if item["td_id"] == safe_id:
            return deepcopy(item["td"])
    return None
