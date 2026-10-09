"""Plan drafting (FR-19 to FR-22).

The drafting step is grounded: every plan item is assembled only from retrieved
records, deterministic scores and selected playbooks. Missing facts are stated as
missing rather than invented, and every item exposes citations.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Tuple

from backend.app.services import compliance_service, scoring_service
from backend.app.services.sales_data_service import (
    FRESHNESS_THRESHOLD_DAYS,
    get_opportunities,
    get_playbooks_for_territory,
    get_service_issues,
    is_record_stale,
    record_age_days,
)

TERRITORY_RULE_EXEC_REVIEW_THRESHOLD = 500000


def _select_playbook(
    account: Dict[str, Any], territory_id: str
) -> Dict[str, Any] | None:
    """FR-17: retrieve an approved playbook relevant to the account."""
    for book in get_playbooks_for_territory(territory_id):
        product = book.get("product")
        if product and product.lower() in str(account.get("name", "")).lower():
            return book
    books = get_playbooks_for_territory(territory_id)
    return books[0] if books else None


def _active_opportunity(
    opportunities: List[Dict[str, Any]], rules: Dict[str, Any]
) -> Dict[str, Any] | None:
    threshold = float(rules.get("high_value_opportunity_threshold", 200000))
    active = [
        opp
        for opp in opportunities
        if str(opp.get("stage", "")).upper() not in {"AT_RISK", "CLOSED_LOST"}
    ]
    high_value = [opp for opp in active if float(opp.get("value", 0) or 0) >= threshold]
    return max(high_value, key=lambda o: float(o.get("value", 0)), default=None)


def draft_plan_items(
    accounts: List[Dict[str, Any]],
    territory_id: str,
    user_id: str,
) -> Tuple[List[Dict[str, Any]], bool, str]:
    """Build ranked plan items. Returns (items, any_stale, scoring_rules_version)."""
    rules = scoring_service.get_scoring_rules()
    drafted: List[Dict[str, Any]] = []
    any_stale = False

    for account in accounts:
        account_id = account.get("account_id", "")
        opportunities = get_opportunities(account_id)
        service_issues = get_service_issues(account_id)
        open_issues = [
            issue
            for issue in service_issues
            if str(issue.get("status", "")).upper() == "OPEN"
        ]
        open_high = any(
            str(issue.get("severity", "")).upper() == "HIGH" for issue in open_issues
        )

        score = scoring_service.compute_account_score(
            account, opportunities, service_issues, rules
        )
        playbook = _select_playbook(account, territory_id)

        facts: List[Dict[str, str]] = []
        missing: List[str] = []

        name = account.get("name")
        if name:
            facts.append(
                {
                    "text": f"{name} is a {account.get('industry', 'unknown')} account "
                    f"in territory {territory_id}.",
                    "source_id": f"account:{account_id}",
                }
            )
        else:
            missing.append("name")

        revenue = account.get("revenue")
        if revenue is None:
            missing.append("revenue")
        else:
            facts.append(
                {
                    "text": f"Trailing revenue is ${float(revenue):,.0f} with "
                    f"{float(account.get('growth', 0) or 0):+.0%} growth.",
                    "source_id": f"account:{account_id}",
                }
            )

        if account.get("product_adoption") is None:
            missing.append("product_adoption")
        else:
            facts.append(
                {
                    "text": "Product adoption is "
                    f"{float(account.get('product_adoption', 0) or 0):.0%} and engagement is "
                    f"{float(account.get('engagement', 0) or 0):.0%}.",
                    "source_id": f"account:{account_id}",
                }
            )

        for opp in opportunities:
            facts.append(
                {
                    "text": f"Open opportunity {opp.get('opportunity_id')} worth "
                    f"${float(opp.get('value', 0) or 0):,.0f} at {opp.get('stage')} stage "
                    f"(expected close {opp.get('expected_close', 'unknown')}).",
                    "source_id": f"opportunity:{opp.get('opportunity_id')}",
                }
            )

        for issue in open_issues:
            facts.append(
                {
                    "text": f"Unresolved {issue.get('severity')} service issue: "
                    f"{issue.get('issue')}.",
                    "source_id": f"service_issue:{issue.get('issue_id')}",
                }
            )

        stale = is_record_stale(account)
        stale_reason = None
        if stale:
            any_stale = True
            age = record_age_days(account)
            stale_reason = (
                f"Account record last updated {account.get('last_updated')} "
                f"({age} days old, exceeds {FRESHNESS_THRESHOLD_DAYS} day threshold)."
            )
            facts.append(
                {"text": f"Data freshness: {stale_reason}", "source_id": f"account:{account_id}"}
            )

        active_opp = _active_opportunity(opportunities, rules)
        ownership_conflict = not compliance_service.check_ownership(
            account, territory_id
        ).status == "passed"

        is_sales_pitch = False
        if ownership_conflict:
            recommended_action = (
                "Route the account to the correct representative before any outreach "
                "(ownership conflict)."
            )
            reason = "Account ownership does not match the territory; resolve before outreach."
            requires_approval = True
        elif open_issues:
            recommended_action = "Resolve the open service issue before any new sales pitch."
            reason = (
                "Unresolved service issues must be handled before a sales conversation "
                "(FR-16)."
            )
            requires_approval = False
        elif active_opp is not None:
            recommended_action = (
                f"Review the next sales milestone for opportunity "
                f"{active_opp.get('opportunity_id')}."
            )
            reason = (
                f"Active high-value opportunity worth "
                f"${float(active_opp.get('value', 0) or 0):,.0f} at "
                f"{active_opp.get('stage')} stage (FR-15)."
            )
            is_sales_pitch = True
            requires_approval = True
        elif playbook and float(account.get("expansion_potential", 0) or 0) >= 0.6:
            recommended_action = (
                f"Engage the account with the approved playbook "
                f"'{playbook.get('title')}'."
            )
            reason = "Account may benefit from another product; approved playbook selected (FR-17)."
            is_sales_pitch = True
            requires_approval = True
            facts.append(
                {
                    "text": f"Approved playbook '{playbook.get('title')}' applies: "
                    f"{str(playbook.get('content', ''))[:160]}",
                    "source_id": f"playbook:{playbook.get('document_id')}",
                }
            )
        else:
            recommended_action = "Schedule a quarterly account review."
            reason = "No unresolved issue or active high-value opportunity; review for continuity."
            requires_approval = False

        if float(account.get("revenue", 0) or 0) >= TERRITORY_RULE_EXEC_REVIEW_THRESHOLD:
            facts.append(
                {
                    "text": "Territory rule: accounts over $500k ARR require quarterly "
                    "executive review.",
                    "source_id": f"territory_rules:{territory_id}",
                }
            )

        if opportunities:
            best = max(opportunities, key=lambda o: float(o.get("value", 0) or 0))
            opportunity_summary = (
                f"{best.get('stage')} stage opportunity worth "
                f"${float(best.get('value', 0) or 0):,.0f} "
                f"(expected close {best.get('expected_close', 'unknown')})."
            )
        else:
            opportunity_summary = "No open opportunity on record."

        citations = list(dict.fromkeys(fact["source_id"] for fact in facts))
        item_id = f"item-{account_id}-{uuid.uuid4().hex[:6]}"
        contact_method = compliance_service.determine_contact_method(account)

        item = {
            "item_id": item_id,
            "account_id": account_id,
            "account_name": name or "UNKNOWN",
            "owner": account.get("owner", ""),
            "priority_rank": 0,
            "priority_score": score["priority_score"],
            "priority_level": score["priority_level"],
            "facts": facts,
            "opportunity_summary": opportunity_summary,
            "recommended_action": recommended_action,
            "reason": reason,
            "citations": citations,
            "requires_approval": requires_approval,
            "factors": score["factor_drivers"],
            "status": "PENDING",
            "stale": stale,
            "stale_reason": stale_reason,
            "missing_data": missing,
        }
        item["compliance"] = compliance_service.evaluate_item(
            account=account,
            territory_id=territory_id,
            user_id=user_id,
            item=item,
            citations=citations,
            facts=facts,
            contact_method=contact_method,
            is_sales_pitch=is_sales_pitch,
            open_high_severity_issues=open_high,
        ).model_dump()

        drafted.append(item)

    drafted.sort(key=lambda entry: entry["priority_score"], reverse=True)
    for rank, entry in enumerate(drafted, start=1):
        entry["priority_rank"] = rank

    return drafted, any_stale, str(rules.get("version"))
