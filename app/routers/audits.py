from __future__ import annotations

import datetime
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response, status
from fastapi.responses import Response

from app.schemas import (
    AuditCreate,
    AuditDetail,
    AuditMetrics,
    AuditStatusResponse,
    AuditSummary,
    CreateAuditResponse,
    PageResult,
    Recommendation,
)
from app.services.report_generator import (
    generate_csv_report,
    generate_json_report,
    generate_pdf_report,
)
from app.services.seo_analyzer import SSRFValidationError, analyze_url
from app.services.storage import store

router = APIRouter(prefix="/audits", tags=["Audits"])


@router.post("", response_model=CreateAuditResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(payload: AuditCreate):
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=400, detail="Target URL is required.")

    target_url = payload.url.strip()
    try:
        # Run real SEO crawler and analyzer
        analysis = await analyze_url(target_url)
    except SSRFValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed to execute: {str(e)}")

    audit_id = f"audit_{uuid.uuid4().hex[:10]}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    audit_record = {
        "id": audit_id,
        "audit_id": audit_id,
        "url": analysis["url"],
        "domain": analysis["domain"],
        "website_id": payload.website_id,
        "status": "completed",
        "overall_score": analysis["overall_score"],
        "score": analysis["overall_score"],
        "pages_crawled": len(analysis.get("pages", [])),
        "high_priority_issues": analysis.get("high_priority_issues", 0),
        "created_at": now_iso,
        "completed_at": now_iso,
        "metrics": analysis["metrics"],
        "pages": analysis["pages"],
        "recommendations": analysis["recommendations"],
        "crawl_warnings": analysis["crawl_warnings"],
    }

    store.save_audit(audit_record)

    return CreateAuditResponse(audit_id=audit_id, status="completed")


@router.get("", response_model=List[AuditSummary])
async def list_audits(
    website_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    return store.get_audits(website_id=website_id, status=status)


@router.get("/{audit_id}", response_model=AuditDetail)
async def get_audit(audit_id: str):
    audit = store.get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return audit


@router.get("/{audit_id}/status", response_model=AuditStatusResponse)
async def get_audit_status(audit_id: str):
    audit = store.get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return AuditStatusResponse(
        audit_id=audit_id,
        status=audit.get("status", "completed"),
        pages_crawled=audit.get("pages_crawled", 1),
        pages_discovered=audit.get("pages_crawled", 1),
        pages_total=audit.get("pages_crawled", 1),
        current_url=audit.get("url"),
        message="Audit completed successfully.",
    )


@router.get("/{audit_id}/pages", response_model=List[PageResult])
async def get_audit_pages(audit_id: str):
    audit = store.get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return audit.get("pages", [])


@router.get("/{audit_id}/metrics", response_model=AuditMetrics)
async def get_audit_metrics(audit_id: str):
    audit = store.get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return audit.get("metrics", {"overall_score": 0})


@router.get("/{audit_id}/recommendations", response_model=List[Recommendation])
async def get_audit_recommendations(audit_id: str):
    audit = store.get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return audit.get("recommendations", [])


@router.delete("/{audit_id}")
async def delete_audit(audit_id: str):
    success = store.delete_audit(audit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return {"status": "deleted", "id": audit_id}


# --- Report Exports ---
@router.get("/{audit_id}/export/pdf")
async def export_pdf(audit_id: str):
    audit = store.get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    pdf_bytes = generate_pdf_report(audit)
    filename = f"seo-audit-{audit_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{audit_id}/export/csv")
async def export_csv(audit_id: str):
    audit = store.get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    csv_str = generate_csv_report(audit)
    filename = f"seo-audit-{audit_id}.csv"
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{audit_id}/export/json")
async def export_json(audit_id: str):
    audit = store.get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    json_str = generate_json_report(audit)
    filename = f"seo-audit-{audit_id}.json"
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
