from __future__ import annotations

from fastapi import APIRouter
from app.schemas import DashboardSummary
from app.services.storage import store

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary():
    return store.get_dashboard_summary()
