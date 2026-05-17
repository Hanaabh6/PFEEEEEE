from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .wot_catalog_data import get_catalog_td, list_td_summaries, summarize_td


app = FastAPI(title="IntelliBuild WoT TD Catalog")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "wot-td-catalog"}


@app.get("/td-catalog")
def list_catalog(request: Request) -> dict:
    base_url = _base_url(request)
    return {
        "source": "intellibuild-external-wot-catalog",
        "items": list_td_summaries(base_url),
    }


@app.get("/td-catalog/{td_id}")
def get_td(td_id: str, request: Request) -> dict:
    td = get_catalog_td(td_id)
    if not td:
        raise HTTPException(status_code=404, detail="Thing Description introuvable")

    source_url = f"{_base_url(request)}/td-catalog/{td_id}"
    return {
        "source": "intellibuild-external-wot-catalog",
        "summary": summarize_td(td_id, td, source_url=source_url),
        "thingDescription": td,
    }
