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
            "category": "Éclairage",
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
            "category": "Télévision",
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
            "category": "Contrôle Accès",
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
    {
        "td_id": "conference-microphone-006",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:conference-microphone-006",
            "title": "Microphone de conference",
            "name": "Microphone de conference",
            "description": "Microphone connecte pour reunion, captation vocale et mode muet.",
            "@type": "Product",
            "category": "Microphone",
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
                            "href": "https://wot-gateway.example.com/microphone-006/properties/status",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "muted": {
                    "type": "boolean",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/microphone-006/properties/muted",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "gain": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/microphone-006/properties/gain",
                            "op": ["readproperty", "writeproperty"],
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "mute": {
                    "description": "Mettre le microphone en sourdine.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/microphone-006/actions/mute",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "unmute": {
                    "description": "Reactiver la captation audio.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/microphone-006/actions/unmute",
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
        "td_id": "security-camera-007",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:security-camera-007",
            "title": "Caméra réseau intelligente",
            "name": "Caméra réseau intelligente",
            "description": "Camera connectee pour surveillance, flux video et detection de mouvement.",
            "@type": "Product",
            "category": "Caméra",
            "securityDefinitions": {
                "bearer_sc": {"scheme": "bearer", "format": "jwt", "in": "header"},
            },
            "security": ["bearer_sc"],
            "properties": {
                "streamUrl": {
                    "type": "string",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/camera-007/properties/streamUrl",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "recording": {
                    "type": "boolean",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/camera-007/properties/recording",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "motionDetected": {
                    "type": "boolean",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/camera-007/properties/motionDetected",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "startRecording": {
                    "description": "Demarrer l'enregistrement video.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/camera-007/actions/startRecording",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "stopRecording": {
                    "description": "Arreter l'enregistrement video.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/camera-007/actions/stopRecording",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "snapshot": {
                    "description": "Capturer une image instantanee.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/camera-007/actions/snapshot",
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
        "td_id": "hvac-controller-008",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:hvac-controller-008",
            "title": "Climatiseur intelligent",
            "name": "Climatiseur intelligent",
            "description": "Systeme de climatisation connecte pour regulation thermique des espaces.",
            "@type": "Product",
            "category": "Climatiseur",
            "securityDefinitions": {
                "bearer_sc": {"scheme": "bearer", "format": "jwt", "in": "header"},
            },
            "security": ["bearer_sc"],
            "properties": {
                "power": {
                    "type": "string",
                    "enum": ["on", "off"],
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/hvac-008/properties/power",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "targetTemperature": {
                    "type": "number",
                    "minimum": 16,
                    "maximum": 30,
                    "unit": "degree celsius",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/hvac-008/properties/targetTemperature",
                            "op": ["readproperty", "writeproperty"],
                            "contentType": "application/json",
                        }
                    ],
                },
                "mode": {
                    "type": "string",
                    "enum": ["cool", "heat", "fan", "auto"],
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/hvac-008/properties/mode",
                            "op": ["readproperty", "writeproperty"],
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "on": {
                    "description": "Allumer le climatiseur.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/hvac-008/actions/on",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "off": {
                    "description": "Eteindre le climatiseur.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/hvac-008/actions/off",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "setTemperature": {
                    "description": "Definir la temperature cible.",
                    "input": {
                        "type": "object",
                        "properties": {"value": {"type": "number", "minimum": 16, "maximum": 30}},
                    },
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/hvac-008/actions/setTemperature",
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
        "td_id": "smart-switch-009",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:smart-switch-009",
            "title": "Interrupteur connecte",
            "name": "Interrupteur connecte",
            "description": "Interrupteur mural connecte pour piloter un circuit ou un equipement.",
            "@type": "Product",
            "category": "Interrupteur",
            "securityDefinitions": {
                "nosec_sc": {"scheme": "nosec"},
            },
            "security": ["nosec_sc"],
            "properties": {
                "state": {
                    "type": "boolean",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/switch-009/properties/state",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "lastToggle": {
                    "type": "string",
                    "format": "date-time",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/switch-009/properties/lastToggle",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "on": {
                    "description": "Activer le circuit.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/switch-009/actions/on",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "off": {
                    "description": "Desactiver le circuit.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/switch-009/actions/off",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "toggle": {
                    "description": "Basculer l'etat de l'interrupteur.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/switch-009/actions/toggle",
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
        "td_id": "coffee-machine-010",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:coffee-machine-010",
            "title": "Machine Café connectée",
            "name": "Machine Café connectée",
            "description": "Machine cafe intelligente pour preparation, maintenance et suivi des niveaux.",
            "@type": "Product",
            "category": "Machine a Café",
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
                            "href": "https://wot-gateway.example.com/coffee-010/properties/status",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "waterLevel": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/coffee-010/properties/waterLevel",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "beansLevel": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/coffee-010/properties/beansLevel",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "brew": {
                    "description": "Lancer la preparation d'une boisson.",
                    "input": {
                        "type": "object",
                        "properties": {"recipe": {"type": "string"}},
                    },
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/coffee-010/actions/brew",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "rinse": {
                    "description": "Lancer un rincage rapide.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/coffee-010/actions/rinse",
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
        "td_id": "document-scanner-011",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:document-scanner-011",
            "title": "Scanner reseau",
            "name": "Scanner reseau",
            "description": "Scanner connecte pour numerisation et partage de documents.",
            "@type": "Product",
            "category": "Scanner",
            "securityDefinitions": {
                "bearer_sc": {"scheme": "bearer", "format": "jwt", "in": "header"},
            },
            "security": ["bearer_sc"],
            "properties": {
                "status": {
                    "type": "string",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/scanner-011/properties/status",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "resolution": {
                    "type": "integer",
                    "minimum": 150,
                    "maximum": 1200,
                    "unit": "dpi",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/scanner-011/properties/resolution",
                            "op": ["readproperty", "writeproperty"],
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "scan": {
                    "description": "Numeriser un document.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/scanner-011/actions/scan",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "cancel": {
                    "description": "Annuler la numerisation en cours.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/scanner-011/actions/cancel",
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
        "td_id": "smart-button-012",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:smart-button-012",
            "title": "Bouton connecte",
            "name": "Bouton connecte",
            "description": "Bouton d'appel ou de scenario pour declencher une action locale.",
            "@type": "Product",
            "category": "Bouton",
            "securityDefinitions": {
                "nosec_sc": {"scheme": "nosec"},
            },
            "security": ["nosec_sc"],
            "properties": {
                "batteryLevel": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/button-012/properties/batteryLevel",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "lastPress": {
                    "type": "string",
                    "format": "date-time",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/button-012/properties/lastPress",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "press": {
                    "description": "Simuler ou enregistrer un appui bouton.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/button-012/actions/press",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                }
            },
            "events": {
                "pressed": {
                    "description": "Evenement emis lorsqu'un appui est detecte.",
                    "data": {"type": "string", "format": "date-time"},
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/button-012/events/pressed",
                            "op": "subscribeevent",
                            "contentType": "application/json",
                        }
                    ],
                }
            },
        },
    },
    {
        "td_id": "smart-alarm-014",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:smart-alarm-014",
            "title": "Alarme intelligente",
            "name": "Alarme intelligente",
            "description": "Alarme connectee pour signalisation sonore et supervision securite.",
            "@type": "Product",
            "category": "Alarme",
            "securityDefinitions": {
                "bearer_sc": {"scheme": "bearer", "format": "jwt", "in": "header"},
            },
            "security": ["bearer_sc"],
            "properties": {
                "armed": {
                    "type": "boolean",
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/alarm-014/properties/armed",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
                "alarmState": {
                    "type": "string",
                    "enum": ["idle", "warning", "triggered"],
                    "readOnly": True,
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/alarm-014/properties/alarmState",
                            "op": "readproperty",
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "arm": {
                    "description": "Armer l'alarme.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/alarm-014/actions/arm",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "disarm": {
                    "description": "Desarmer l'alarme.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/alarm-014/actions/disarm",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "trigger": {
                    "description": "Declencher un signal d'alerte.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/alarm-014/actions/trigger",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "silence": {
                    "description": "Mettre temporairement l'alarme en silence.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/alarm-014/actions/silence",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "reset": {
                    "description": "Reinitialiser l'etat de l'alarme apres intervention.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/alarm-014/actions/reset",
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
        "td_id": "smart-speaker-015",
        "td": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/",
            ],
            "id": "urn:dev:wot:intellibuild:smart-speaker-015",
            "title": "Haut-parleur connecte",
            "name": "Haut-parleur connecte",
            "description": "Haut-parleur intelligent pour annonces, diffusion audio et alertes.",
            "@type": "Product",
            "category": "Haut-parleur",
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
                            "href": "https://wot-gateway.example.com/speaker-015/properties/status",
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
                            "href": "https://wot-gateway.example.com/speaker-015/properties/volume",
                            "op": ["readproperty", "writeproperty"],
                            "contentType": "application/json",
                        }
                    ],
                },
                "muted": {
                    "type": "boolean",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/speaker-015/properties/muted",
                            "op": ["readproperty", "writeproperty"],
                            "contentType": "application/json",
                        }
                    ],
                },
            },
            "actions": {
                "play": {
                    "description": "Demarrer la diffusion audio.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/speaker-015/actions/play",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "stop": {
                    "description": "Arreter la diffusion audio.",
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/speaker-015/actions/stop",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
                "announce": {
                    "description": "Diffuser une annonce vocale.",
                    "input": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    },
                    "forms": [
                        {
                            "href": "https://wot-gateway.example.com/speaker-015/actions/announce",
                            "op": "invokeaction",
                            "htv:methodName": "POST",
                            "contentType": "application/json",
                        }
                    ],
                },
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
