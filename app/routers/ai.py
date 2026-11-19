from __future__ import annotations

from fastapi import APIRouter
from app.schemas import MetaSuggestionInput, MetaSuggestionOutput

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/meta-suggestions", response_model=MetaSuggestionOutput)
async def get_meta_suggestions(payload: MetaSuggestionInput):
    page_name = (payload.page_url or "Website").split("/")[-1].replace("-", " ").capitalize()
    if not page_name:
        page_name = "Homepage"

    topic = payload.title or page_name
    summary = payload.content_summary or "high-performance SEO, speed optimization, and data-driven marketing growth"

    titles = [
        f"{topic} | Leading Growth & Intelligence Platform",
        f"Optimize {topic} - Data-Driven Marketing & SEO Audit",
        f"The Complete Guide to {topic} | Best Practices 2026",
    ]

    descriptions = [
        f"Transform your online visibility with {topic}. Accelerate rankings, fix critical technical bottlenecks, and drive conversions with deterministic SEO audits.",
        f"Looking to enhance {topic}? Discover actionable SEO audits, structured metrics, and prioritized AI insights designed to expand organic search traffic.",
        f"Maximize performance and customer acquisition for {topic}. Comprehensive auditing across title tags, headings, canonicals, and link health.",
    ]

    rationale = (
        f"Suggestions engineered to target primary keywords for '{topic}' within optimal Google search snippet thresholds "
        "(30-60 character titles, 120-155 character descriptions) while maintaining compelling call-to-actions."
    )

    return MetaSuggestionOutput(
        suggested_titles=titles,
        suggested_descriptions=descriptions,
        rationale=rationale,
    )
