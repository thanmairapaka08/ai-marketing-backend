from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


# --- Auth Models ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str = ""


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: Union[str, int]
    email: str
    full_name: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    session_expires_at: Optional[str] = None


class LoginResponse(BaseModel):
    user: UserOut
    message: str = "Logged in successfully"
    token_type: str = "bearer"


# --- Website Models ---
class WebsiteCreate(BaseModel):
    url: str
    name: Optional[str] = None


class WebsiteOut(BaseModel):
    id: Union[str, int]
    url: str
    domain: str
    name: Optional[str] = None
    latest_score: Optional[int] = None
    last_audit_at: Optional[str] = None
    audit_count: int = 0
    created_at: Optional[str] = None


# --- Audit Models ---
AuditStatus = Literal[
    "queued",
    "running",
    "completed",
    "partially_completed",
    "failed",
    "cancelled",
]


class AuditCreate(BaseModel):
    url: str
    website_id: Optional[Union[str, int]] = None


class CreateAuditResponse(BaseModel):
    audit_id: str
    status: AuditStatus


class AuditStatusResponse(BaseModel):
    audit_id: str
    status: AuditStatus
    pages_crawled: int = 1
    pages_discovered: int = 1
    pages_total: int = 1
    current_url: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class AffectedPage(BaseModel):
    url: str
    issue: Optional[str] = None
    detail: Optional[str] = None


class MetricResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    status: Optional[str] = None
    severity: Optional[str] = None
    affected_urls: List[Union[str, AffectedPage]] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    issues: List[Union[str, Dict[str, Any]]] = Field(default_factory=list)

    # Allow arbitrary extra fields for metric-specific stats (missing_titles, broken_count, etc.)
    model_config = {"extra": "allow"}


class SecondaryCheck(BaseModel):
    name: Optional[str] = None
    check: Optional[str] = None
    status: Optional[str] = None
    passed: bool = True
    message: Optional[str] = None
    detail: Optional[str] = None


class AuditMetrics(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    title_meta: Optional[MetricResult] = None
    broken_links: Optional[MetricResult] = None
    image_alt: Optional[MetricResult] = None
    headings: Optional[MetricResult] = None
    canonical: Optional[MetricResult] = None
    secondary_checks: List[SecondaryCheck] = Field(default_factory=list)
    crawl_warnings: List[Union[str, Dict[str, Any]]] = Field(default_factory=list)


class AuditSummary(BaseModel):
    id: str
    audit_id: str
    url: str
    domain: str
    website_id: Optional[Union[str, int]] = None
    status: AuditStatus
    overall_score: Optional[int] = None
    score: Optional[int] = None
    pages_crawled: Optional[int] = 1
    high_priority_issues: Optional[int] = 0
    created_at: str
    completed_at: Optional[str] = None


class AuditDetail(AuditSummary):
    metrics: Optional[AuditMetrics] = None
    crawl_warnings: List[Union[str, Dict[str, Any]]] = Field(default_factory=list)


class PageResult(BaseModel):
    url: str
    status_code: int = 200
    title: Optional[str] = None
    title_length: Optional[int] = None
    meta_description_length: Optional[int] = None
    h1_count: Optional[int] = None
    images_missing_alt: Optional[int] = None
    canonical: Optional[str] = None
    issues_count: int = 0


class Recommendation(BaseModel):
    id: Union[str, int]
    title: str
    description: Optional[str] = None
    priority: Literal["high", "medium", "low"] = "medium"
    impact: Optional[str] = None
    expected_impact: Optional[str] = None
    effort: Optional[str] = None
    estimated_effort: Optional[str] = None
    category: Optional[str] = None
    metric: Optional[str] = None
    affected_urls: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    source: str = "rule_based"


# --- Dashboard Models ---
class TrendPoint(BaseModel):
    date: str
    score: Optional[int] = None


class WebsitePerformance(BaseModel):
    domain: Optional[str] = None
    url: Optional[str] = None
    score: Optional[int] = None
    last_audit_at: Optional[str] = None


class DashboardSummary(BaseModel):
    total_websites: int = 0
    total_audits: int = 0
    average_score: Optional[float] = None
    critical_issues: int = 0
    score_trend: List[TrendPoint] = Field(default_factory=list)
    recent_audits: List[AuditSummary] = Field(default_factory=list)
    recommendations_preview: List[Recommendation] = Field(default_factory=list)
    website_performance: List[WebsitePerformance] = Field(default_factory=list)


# --- Competitor Models ---
class CompareInput(BaseModel):
    website_id: Union[str, int]
    competitor_urls: List[str]


class ComparisonSite(BaseModel):
    url: str
    is_primary: bool = False
    overall_score: Optional[int] = None
    status: str = "completed"
    metrics: Dict[str, Optional[int]] = Field(default_factory=dict)


class ComparisonResult(BaseModel):
    comparison_id: str
    id: str
    status: str = "completed"
    sites: List[ComparisonSite] = Field(default_factory=list)


# --- AI Models ---
class MetaSuggestionInput(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    page_url: Optional[str] = None
    content_summary: Optional[str] = None


class MetaSuggestionOutput(BaseModel):
    suggested_titles: List[str]
    suggested_descriptions: List[str]
    rationale: str
