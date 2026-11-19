from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional


class InMemoryStore:
    def __init__(self) -> None:
        self.users: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, str] = {}  # token -> email
        self.websites: Dict[str, Dict[str, Any]] = {}
        self.audits: Dict[str, Dict[str, Any]] = {}
        self.comparisons: Dict[str, Dict[str, Any]] = {}

        self._seed_data()

    def _seed_data(self) -> None:
        # Default test user
        self.users["demo@example.com"] = {
            "id": "usr_demo123",
            "email": "demo@example.com",
            "password_hash": "demo123_hash",
            "full_name": "Alex Mercer",
            "created_at": "2026-01-15T09:00:00Z",
        }

        # Seed initial website
        site_id = "site_1"
        self.websites[site_id] = {
            "id": site_id,
            "url": "https://example.com",
            "domain": "example.com",
            "name": "Example Corp",
            "latest_score": 88,
            "last_audit_at": "2026-11-17T14:30:00Z",
            "audit_count": 3,
            "created_at": "2026-10-01T10:00:00Z",
        }

        # Seed initial audit
        audit_id = "audit_demo_1"
        now_iso = "2026-11-17T14:30:00Z"
        self.audits[audit_id] = {
            "id": audit_id,
            "audit_id": audit_id,
            "url": "https://example.com",
            "domain": "example.com",
            "website_id": site_id,
            "status": "completed",
            "overall_score": 88,
            "score": 88,
            "pages_crawled": 5,
            "high_priority_issues": 1,
            "created_at": now_iso,
            "completed_at": now_iso,
            "crawl_warnings": [],
            "metrics": {
                "overall_score": 88,
                "title_meta": {
                    "score": 90,
                    "status": "good",
                    "missing_titles": 0,
                    "title_length_issues": 0,
                    "missing_descriptions": 0,
                    "description_length_issues": 1,
                    "issues": [{
                        "message": "Meta description is 165 characters (optimal is 70-160)",
                        "severity": "medium",
                        "url": "https://example.com",
                    }],
                    "suggestions": ["Trim meta description to 155 characters for optimal Google SERP display."],
                    "affected_urls": ["https://example.com"],
                },
                "broken_links": {
                    "score": 100,
                    "status": "good",
                    "working_links": 14,
                    "broken_count": 0,
                    "unreachable_count": 0,
                    "issues": [],
                    "suggestions": ["All internal links returned HTTP 200 OK."],
                    "affected_urls": [],
                },
                "image_alt": {
                    "score": 85,
                    "status": "good",
                    "total_images": 8,
                    "images_with_alt": 7,
                    "images_missing_alt": 1,
                    "coverage": 88,
                    "issues": [{
                        "message": "1 image missing descriptive alt text",
                        "severity": "medium",
                        "url": "https://example.com",
                    }],
                    "suggestions": ["Add descriptive alt text to hero and feature images."],
                    "affected_urls": ["https://example.com"],
                },
                "headings": {
                    "score": 95,
                    "status": "good",
                    "pages_with_single_h1": 1,
                    "pages_missing_h1": 0,
                    "pages_multiple_h1": 0,
                    "issues": [],
                    "suggestions": ["Clear single H1 heading hierarchy."],
                    "affected_urls": [],
                },
                "canonical": {
                    "score": 100,
                    "status": "good",
                    "valid_canonical": 1,
                    "missing_canonical": 0,
                    "invalid_canonical": 0,
                    "coverage": 100,
                    "issues": [],
                    "suggestions": ["Self-referencing canonical tag is present and valid."],
                    "affected_urls": [],
                },
                "secondary_checks": [
                    {
                        "name": "HTTPS Protocol",
                        "check": "https_enforced",
                        "status": "passed",
                        "passed": True,
                        "message": "Enforced with valid SSL certificate",
                    },
                    {
                        "name": "OpenGraph Tags",
                        "check": "opengraph_tags",
                        "status": "passed",
                        "passed": True,
                        "message": "og:title, og:description, and og:image configured",
                    },
                    {
                        "name": "Robots.txt",
                        "check": "robots_txt",
                        "status": "passed",
                        "passed": True,
                        "message": "Disallow rules valid, sitemap declared",
                    },
                    {
                        "name": "XML Sitemap",
                        "check": "sitemap_xml",
                        "status": "passed",
                        "passed": True,
                        "message": "Sitemap indexed and accessible",
                    },
                ],
                "crawl_warnings": [],
            },
            "pages": [
                {
                    "url": "https://example.com",
                    "status_code": 200,
                    "title": "Example Domain - Official Portal",
                    "title_length": 32,
                    "meta_description_length": 165,
                    "h1_count": 1,
                    "images_missing_alt": 1,
                    "canonical": "https://example.com",
                    "issues_count": 2,
                },
                {
                    "url": "https://example.com/about",
                    "status_code": 200,
                    "title": "About Example Domain",
                    "title_length": 20,
                    "meta_description_length": 110,
                    "h1_count": 1,
                    "images_missing_alt": 0,
                    "canonical": "https://example.com/about",
                    "issues_count": 0,
                },
            ],
            "recommendations": [
                {
                    "id": 1,
                    "title": "Shorten Homepage Meta Description",
                    "description": "Your meta description is 165 characters long. Search engines cut off snippets after ~160 characters.",
                    "priority": "medium",
                    "expected_impact": "Prevents truncation in search engine result pages",
                    "estimated_effort": "Low (5 mins)",
                    "category": "Meta & Content",
                    "metric": "title_meta",
                    "affected_urls": ["https://example.com"],
                    "steps": [
                        "Open index.html or CMS page settings.",
                        "Trim description to between 120 and 155 characters.",
                    ],
                    "source": "gemini",
                },
                {
                    "id": 2,
                    "title": "Add Alt Attribute to Hero Header Graphic",
                    "description": "1 image is currently unlabelled, reducing accessibility score and image search visibility.",
                    "priority": "medium",
                    "expected_impact": "WCAG compliance and image pack discovery",
                    "estimated_effort": "Low (5 mins)",
                    "category": "Accessibility & Media",
                    "metric": "image_alt",
                    "affected_urls": ["https://example.com"],
                    "steps": [
                        "Inspect image tags without alt attributes.",
                        "Add concise contextual description in alt attribute.",
                    ],
                    "source": "rule_based",
                },
            ],
        }

    # Website operations
    def get_websites(self) -> List[Dict[str, Any]]:
        return list(self.websites.values())

    def get_website(self, website_id: str) -> Optional[Dict[str, Any]]:
        return self.websites.get(str(website_id))

    def add_website(self, url: str, name: Optional[str] = None) -> Dict[str, Any]:
        from urllib.parse import urlparse
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        domain = urlparse(url).hostname or url
        site_id = f"site_{uuid.uuid4().hex[:8]}"
        site = {
            "id": site_id,
            "url": url,
            "domain": domain,
            "name": name or domain.capitalize(),
            "latest_score": None,
            "last_audit_at": None,
            "audit_count": 0,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        self.websites[site_id] = site
        return site

    def delete_website(self, website_id: str) -> bool:
        if str(website_id) in self.websites:
            del self.websites[str(website_id)]
            return True
        return False

    # Audit operations
    def get_audits(self, website_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        results = list(self.audits.values())
        if website_id:
            results = [a for a in results if str(a.get("website_id")) == str(website_id)]
        if status:
            results = [a for a in results if a.get("status") == status]
        return sorted(results, key=lambda a: a.get("created_at", ""), reverse=True)

    def get_audit(self, audit_id: str) -> Optional[Dict[str, Any]]:
        return self.audits.get(audit_id)

    def save_audit(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        audit_id = audit_data.get("id") or audit_data.get("audit_id") or f"audit_{uuid.uuid4().hex[:8]}"
        audit_data["id"] = audit_id
        audit_data["audit_id"] = audit_id
        self.audits[audit_id] = audit_data

        # Update website stats if matching website exists
        domain = audit_data.get("domain")
        score = audit_data.get("overall_score")
        completed_at = audit_data.get("completed_at") or datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        found_site = False
        for site in self.websites.values():
            if site.get("domain") == domain or site.get("url") == audit_data.get("url"):
                site["latest_score"] = score
                site["last_audit_at"] = completed_at
                site["audit_count"] = (site.get("audit_count") or 0) + 1
                found_site = True
                break

        if not found_site and domain:
            new_site = self.add_website(audit_data.get("url"), name=domain.capitalize())
            new_site["latest_score"] = score
            new_site["last_audit_at"] = completed_at
            new_site["audit_count"] = 1

        return audit_data

    def delete_audit(self, audit_id: str) -> bool:
        if audit_id in self.audits:
            del self.audits[audit_id]
            return True
        return False

    # Dashboard Summary
    def get_dashboard_summary(self) -> Dict[str, Any]:
        audits = list(self.audits.values())
        websites = list(self.websites.values())

        scores = [a["overall_score"] for a in audits if a.get("overall_score") is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else None

        critical_issues = sum(a.get("high_priority_issues", 0) for a in audits)

        # Build trend points
        sorted_audits = sorted(audits, key=lambda a: a.get("created_at", ""))
        trend = []
        for a in sorted_audits[-7:]:
            dt_raw = a.get("created_at", "")[:10]
            trend.append({"date": dt_raw, "score": a.get("overall_score")})

        # Fallback trend if few audits
        if len(trend) < 3:
            today = datetime.date.today()
            trend = [
                {"date": (today - datetime.timedelta(days=12)).isoformat(), "score": 76},
                {"date": (today - datetime.timedelta(days=8)).isoformat(), "score": 82},
                {"date": (today - datetime.timedelta(days=4)).isoformat(), "score": 85},
                {"date": today.isoformat(), "score": avg_score or 88},
            ]

        # Collect preview recommendations
        recs: List[Dict[str, Any]] = []
        for a in audits:
            for r in a.get("recommendations", []):
                recs.append(r)
                if len(recs) >= 5:
                    break
            if len(recs) >= 5:
                break

        # Website performance
        perf = []
        for site in websites:
            perf.append({
                "domain": site.get("domain"),
                "url": site.get("url"),
                "score": site.get("latest_score"),
                "last_audit_at": site.get("last_audit_at"),
            })

        return {
            "total_websites": len(websites),
            "total_audits": len(audits),
            "average_score": avg_score,
            "critical_issues": critical_issues,
            "score_trend": trend,
            "recent_audits": sorted(audits, key=lambda a: a.get("created_at", ""), reverse=True)[:5],
            "recommendations_preview": recs,
            "website_performance": perf,
        }


# Global store instance
store = InMemoryStore()
