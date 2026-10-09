from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List

# FR-3: records whose freshness exceeds this threshold are flagged.
try:
    from backend.app.config.settings import settings as _settings

    FRESHNESS_THRESHOLD_DAYS = _settings.data_freshness_threshold_days
except Exception:  # pragma: no cover - settings are always importable in practice
    FRESHNESS_THRESHOLD_DAYS = 30
# Fixed reference date keeps freshness deterministic for tests and demos.
REFERENCE_DATE = date(2026, 10, 9)


def build_sample_data() -> Dict[str, Any]:
    territories = [
        {
            "territory_id": "T001",
            "name": "North Region",
            "owner": "Alicia Ng",
            "owner_id": "mgr-001",
            "source_system": "CRM",
            "last_updated": "2026-10-05",
            "rules": [
                "Accounts over $500k ARR require quarterly executive review.",
                "High risk accounts must have a documented action plan.",
            ],
            "capacity": 12,
        },
        {
            "territory_id": "T002",
            "name": "South Region",
            "owner": "Marco Diaz",
            "owner_id": "mgr-002",
            "source_system": "CRM",
            "last_updated": "2026-10-06",
            "rules": [
                "Expansion account plans require manager approval.",
                "Renewal opportunities over 120 days require escalation.",
            ],
            "capacity": 10,
        },
        {
            "territory_id": "T003",
            "name": "Central Region",
            "owner": "Priya Shah",
            "owner_id": "mgr-003",
            "source_system": "CRM",
            "last_updated": "2026-10-04",
            "rules": [
                "All customer escalations must be resolved within 5 business days.",
            ],
            "capacity": 8,
        },
    ]

    accounts = [
        {
            "account_id": "ACC1001",
            "territory_id": "T001",
            "name": "Northwind Foods",
            "industry": "Retail",
            "revenue": 980000,
            "growth": 0.18,
            "product_adoption": 0.72,
            "engagement": 0.81,
            "health": "HEALTHY",
            "open_issues": 1,
            "strategic_importance": 0.9,
            "expansion_potential": 0.78,
            "risk_level": 0.2,
            "owner": "Alicia Ng",
            "owner_id": "mgr-001",
            "source_system": "CRM",
            "last_updated": "2026-10-05",
            "preferred_contact_method": "EMAIL",
            "permissions": {
                "allowed_roles": ["SALES_MANAGER", "SALES_OPS", "AUDITOR"],
                "allowed_user_ids": ["rep-042"],
            },
        },
        {
            "account_id": "ACC1002",
            "territory_id": "T001",
            "name": "Harbor Retail Group",
            "industry": "Wholesale",
            "revenue": 520000,
            "growth": 0.14,
            "product_adoption": 0.58,
            "engagement": 0.62,
            "health": "WATCH",
            "open_issues": 2,
            "strategic_importance": 0.76,
            "expansion_potential": 0.67,
            "risk_level": 0.42,
            "owner": "Alicia Ng",
            "owner_id": "mgr-001",
            "source_system": "CRM",
            "last_updated": "2026-07-15",
            "preferred_contact_method": "PHONE",
            "permissions": {
                "allowed_roles": ["SALES_MANAGER", "SALES_OPS", "AUDITOR"],
                "allowed_user_ids": ["rep-042"],
            },
        },
        {
            "account_id": "ACC2001",
            "territory_id": "T002",
            "name": "Summit Health",
            "industry": "Healthcare",
            "revenue": 760000,
            "growth": 0.21,
            "product_adoption": 0.88,
            "engagement": 0.9,
            "health": "HEALTHY",
            "open_issues": 0,
            "strategic_importance": 0.82,
            "expansion_potential": 0.8,
            "risk_level": 0.1,
            "owner": "Marco Diaz",
            "owner_id": "mgr-002",
            "source_system": "CRM",
            "last_updated": "2026-10-06",
            "preferred_contact_method": "EMAIL",
            "permissions": {
                "allowed_roles": ["SALES_MANAGER", "SALES_OPS", "AUDITOR"],
            },
        },
        {
            "account_id": "ACC2002",
            "territory_id": "T002",
            "name": "Delta Manufacturing",
            "industry": "Manufacturing",
            "revenue": 440000,
            "growth": -0.04,
            "product_adoption": 0.36,
            "engagement": 0.41,
            "health": "AT_RISK",
            "open_issues": 3,
            "strategic_importance": 0.6,
            "expansion_potential": 0.39,
            "risk_level": 0.76,
            "owner": "Marco Diaz",
            "owner_id": "rep-042",
            "source_system": "CRM",
            "last_updated": "2026-10-03",
            "preferred_contact_method": "PHONE",
            "permissions": {
                "allowed_roles": ["SALES_MANAGER", "SALES_OPS", "AUDITOR"],
            },
        },
        {
            "account_id": "ACC3001",
            "territory_id": "T003",
            "name": "Cedar Logistics",
            "industry": "Logistics",
            "revenue": 660000,
            "growth": 0.12,
            "product_adoption": 0.77,
            "engagement": 0.75,
            "health": "HEALTHY",
            "open_issues": 1,
            "strategic_importance": 0.7,
            "expansion_potential": 0.65,
            "risk_level": 0.22,
            "owner": "Priya Shah",
            "owner_id": "mgr-003",
            "source_system": "CRM",
            "last_updated": "2026-09-20",
            "preferred_contact_method": "EMAIL",
            "permissions": {
                "allowed_roles": ["SALES_MANAGER", "SALES_OPS", "AUDITOR"],
            },
        },
    ]

    opportunities = [
        {
            "opportunity_id": "OP-101",
            "account_id": "ACC1001",
            "value": 220000,
            "stage": "PROPOSAL",
            "expected_close": "2026-11-30",
            "product": "Analytics Plus",
        },
        {
            "opportunity_id": "OP-102",
            "account_id": "ACC1002",
            "value": 150000,
            "stage": "QUALIFYING",
            "expected_close": "2026-11-15",
            "product": "Customer Insights",
        },
        {
            "opportunity_id": "OP-201",
            "account_id": "ACC2001",
            "value": 260000,
            "stage": "NEGOTIATION",
            "expected_close": "2026-10-25",
            "product": "Expansion Suite",
        },
        {
            "opportunity_id": "OP-202",
            "account_id": "ACC2002",
            "value": 90000,
            "stage": "AT_RISK",
            "expected_close": "2026-09-28",
            "product": "Renewal",
        },
        {
            "opportunity_id": "OP-301",
            "account_id": "ACC3001",
            "value": 180000,
            "stage": "DISCOVERY",
            "expected_close": "2026-12-01",
            "product": "Operations Cloud",
        },
    ]

    activities = [
        {"account_id": "ACC1001", "type": "call", "date": "2026-09-11", "result": "positive"},
        {"account_id": "ACC1002", "type": "email", "date": "2026-09-09", "result": "follow-up"},
        {"account_id": "ACC2001", "type": "meeting", "date": "2026-09-12", "result": "executive"},
        {"account_id": "ACC2002", "type": "call", "date": "2026-09-02", "result": "at_risk"},
        {"account_id": "ACC3001", "type": "demo", "date": "2026-09-07", "result": "good"},
    ]

    service_issues = [
        {
            "issue_id": "SI-1002",
            "account_id": "ACC1002",
            "issue": "API latency complaint",
            "severity": "MEDIUM",
            "status": "OPEN",
            "source_system": "SUPPORT_DESK",
            "last_updated": "2026-10-02",
        },
        {
            "issue_id": "SI-2002",
            "account_id": "ACC2002",
            "issue": "Dashboard outage",
            "severity": "HIGH",
            "status": "OPEN",
            "source_system": "SUPPORT_DESK",
            "last_updated": "2026-10-07",
        },
    ]

    contacts = [
        {"account_id": "ACC1001", "name": "Elena Brooks", "role": "VP Operations"},
        {"account_id": "ACC1002", "name": "Sam Hunt", "role": "Director of Sales"},
        {"account_id": "ACC2001", "name": "Jenna Kline", "role": "COO"},
        {"account_id": "ACC2002", "name": "Rafi Sayeed", "role": "Head of Procurement"},
        {"account_id": "ACC3001", "name": "Noah Lee", "role": "Regional Director"},
    ]

    playbooks = [
        {
            "document_id": "playbook-product-expansion",
            "title": "Product Expansion Playbook",
            "category": "sales_playbook",
            "territory": "T001",
            "product": "Analytics Plus",
            "content": "Focus on accounts with strong revenue growth and adoption gaps. Confirm decision maker, establish executive sponsor, and propose staged expansion steps.",
            "effective_date": "2026-01-01",
            "source": "sales_playbooks.pdf",
            "last_updated": "2026-09-01",
        },
        {
            "document_id": "playbook-at-risk-recovery",
            "title": "At Risk Account Recovery",
            "category": "account_management",
            "territory": "T002",
            "product": "Renewal",
            "content": "If revenue is declining and service issues are open, schedule a recovery review and align support, renewal options, and executive outreach.",
            "effective_date": "2026-02-01",
            "source": "account_recovery_policy.pdf",
            "last_updated": "2026-09-15",
        },
        {
            "document_id": "playbook-adoption-nudge",
            "title": "Adoption Nudge Playbook",
            "category": "sales_playbook",
            "territory": "T003",
            "product": "Operations Cloud",
            "content": "For healthy accounts with room to expand, review usage, propose a training session and a lightweight add-on to raise product adoption.",
            "effective_date": "2026-03-01",
            "source": "sales_playbooks.pdf",
            "last_updated": "2026-09-10",
        },
    ]

    # FR-25: contact policies govern whether proposed outreach is permitted.
    contact_policies = [
        {
            "policy_id": "CP-EMAIL",
            "method": "EMAIL",
            "allowed": True,
            "notes": "Email outreach permitted during normal business hours.",
        },
        {
            "policy_id": "CP-PHONE",
            "method": "PHONE",
            "allowed": True,
            "notes": "Phone outreach permitted; avoid accounts with an unresolved high-severity issue.",
        },
        {
            "policy_id": "CP-ONSITE",
            "method": "ONSITE",
            "allowed": False,
            "notes": "Onsite visits require manager approval and are out of scope for v1 outreach.",
        },
    ]

    return {
        "territories": territories,
        "accounts": accounts,
        "opportunities": opportunities,
        "activities": activities,
        "service_issues": service_issues,
        "contacts": contacts,
        "playbooks": playbooks,
        "contact_policies": contact_policies,
    }


DATA = build_sample_data()


def get_territories() -> List[Dict[str, Any]]:
    return DATA["territories"]


def get_territory(territory_id: str) -> Dict[str, Any]:
    for territory in DATA["territories"]:
        if territory["territory_id"] == territory_id:
            return territory
    return {}


def get_accounts_by_territory(territory_id: str) -> List[Dict[str, Any]]:
    return [account for account in DATA["accounts"] if account["territory_id"] == territory_id]


def get_account(account_id: str) -> Dict[str, Any]:
    for account in DATA["accounts"]:
        if account["account_id"] == account_id:
            return account
    return {}


def get_account_history(account_id: str) -> List[Dict[str, Any]]:
    history = []
    for activity in DATA["activities"]:
        if activity["account_id"] == account_id:
            history.append(activity)
    return history


def get_opportunities(account_id: str) -> List[Dict[str, Any]]:
    return [opp for opp in DATA["opportunities"] if opp["account_id"] == account_id]


def get_service_issues(account_id: str) -> List[Dict[str, Any]]:
    return [issue for issue in DATA["service_issues"] if issue["account_id"] == account_id]


def get_account_contacts(account_id: str) -> List[Dict[str, Any]]:
    return [contact for contact in DATA["contacts"] if contact["account_id"] == account_id]


def get_territory_rules(territory_id: str) -> List[str]:
    territory = get_territory(territory_id)
    return territory.get("rules", [])


def calculate_account_kpis(account_id: str) -> Dict[str, Any]:
    account = get_account(account_id)
    opportunities = get_opportunities(account_id)
    pipeline_value = sum(item["value"] for item in opportunities)
    account_health = account.get("health", "WATCH")
    metrics = {
        "revenue": account.get("revenue", 0),
        "revenue_growth": account.get("growth", 0.0),
        "pipeline_value": pipeline_value,
        "product_adoption": account.get("product_adoption", 0.0),
        "open_issues": account.get("open_issues", 0),
        "engagement_score": account.get("engagement", 0.0),
        "expansion_potential": account.get("expansion_potential", 0.0),
    }

    trend = "GROWING" if account.get("growth", 0) > 0 else "DECLINING"
    health = "HEALTHY" if account_health == "HEALTHY" else "WATCH" if account_health == "WATCH" else "AT_RISK"
    return {
        "account_id": account_id,
        "metrics": metrics,
        "trend": trend,
        "health": health,
        "confidence": 0.94,
    }


def prioritize_accounts(territory_id: str) -> List[Dict[str, Any]]:
    accounts = get_accounts_by_territory(territory_id)
    results = []
    for account in accounts:
        score = (
            account.get("growth", 0) * 35
            + account.get("expansion_potential", 0) * 25
            + account.get("engagement", 0) * 15
            + account.get("strategic_importance", 0) * 20
            + min(account.get("revenue", 0) / 100000.0, 10) * 10
            - account.get("risk_level", 0) * 30
        )
        score = max(0.0, min(score, 100.0))
        level = "HIGH" if score >= 70 else "MEDIUM" if score >= 45 else "LOW"
        results.append(
            {
                "account_id": account["account_id"],
                "priority_score": round(score, 2),
                "priority_level": level,
                "drivers": ["Strong revenue growth", "Expansion opportunity"] if score >= 65 else ["Balanced pipeline"],
                "risks": ["Service issue"] if account.get("open_issues", 0) > 0 else [],
                "evidence": ["Revenue trend", "Account record"],
            }
        )
    return sorted(results, key=lambda item: item["priority_score"], reverse=True)


def get_dashboard_metrics() -> Dict[str, Any]:
    high_priority = 0
    for territory in DATA["territories"]:
        high_priority += sum(
            1
            for item in prioritize_accounts(territory["territory_id"])
            if item["priority_level"] == "HIGH"
        )
    return {
        "total_territories": len(DATA["territories"]),
        "total_accounts": len(DATA["accounts"]),
        "high_priority_accounts": high_priority,
        "open_opportunities": len(DATA["opportunities"]),
        "pipeline_value": sum(item["value"] for item in DATA["opportunities"]),
        "status": "ready",
    }


def get_retrieved_documents(query: str) -> List[Dict[str, Any]]:
    docs = []
    q = query.lower()
    for playbook in DATA["playbooks"]:
        if any(word in playbook["title"].lower() or word in playbook["content"].lower() for word in q.split()):
            docs.append({
                "document_id": playbook.get("document_id", playbook["title"]),
                "title": playbook["title"],
                "content": playbook["content"],
                "source": playbook["source"],
                "category": playbook["category"],
                "effective_date": playbook["effective_date"],
                "territory": playbook.get("territory"),
                "last_updated": playbook.get("last_updated"),
            })
    return docs


def get_all_accounts() -> List[Dict[str, Any]]:
    return DATA["accounts"]


def get_contact_policies() -> List[Dict[str, Any]]:
    return DATA["contact_policies"]


def get_contact_policy(method: str) -> Dict[str, Any]:
    for policy in DATA["contact_policies"]:
        if policy["method"] == method.upper():
            return policy
    return {}


def get_playbooks() -> List[Dict[str, Any]]:
    return DATA["playbooks"]


def get_playbooks_for_territory(territory_id: str) -> List[Dict[str, Any]]:
    return [book for book in DATA["playbooks"] if book.get("territory") in (None, territory_id)]


def _parse_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def record_age_days(record: Dict[str, Any], reference: date | None = None) -> int | None:
    """Return the age of a record in days, or None when no usable timestamp exists."""
    parsed = _parse_date(record.get("last_updated"))
    if parsed is None:
        return None
    ref = reference or REFERENCE_DATE
    return (ref - parsed).days


def is_record_stale(
    record: Dict[str, Any],
    threshold_days: int = FRESHNESS_THRESHOLD_DAYS,
    reference: date | None = None,
) -> bool:
    """FR-3: flag records whose freshness exceeds the configurable threshold."""
    age = record_age_days(record, reference=reference)
    return age is not None and age > threshold_days
