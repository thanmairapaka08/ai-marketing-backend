from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status

from app.schemas import AuditSummary, WebsiteCreate, WebsiteOut
from app.services.storage import store

router = APIRouter(prefix="/websites", tags=["Websites"])


@router.get("", response_model=List[WebsiteOut])
async def list_websites():
    return store.get_websites()


@router.post("", response_model=WebsiteOut, status_code=status.HTTP_201_CREATED)
async def create_website(payload: WebsiteCreate):
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=400, detail="Website URL is required.")
    return store.add_website(payload.url.strip(), name=payload.name)


@router.get("/{website_id}", response_model=WebsiteOut)
async def get_website(website_id: str):
    site = store.get_website(website_id)
    if not site:
        raise HTTPException(status_code=404, detail="Website not found.")
    return site


@router.delete("/{website_id}", status_code=status.HTTP_200_OK)
async def delete_website(website_id: str):
    success = store.delete_website(website_id)
    if not success:
        raise HTTPException(status_code=404, detail="Website not found.")
    return {"status": "deleted", "id": website_id}


@router.get("/{website_id}/audits", response_model=List[AuditSummary])
async def get_website_audits(website_id: str):
    site = store.get_website(website_id)
    if not site:
        raise HTTPException(status_code=404, detail="Website not found.")
    return store.get_audits(website_id=website_id)
