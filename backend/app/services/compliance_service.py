"""Deterministic compliance checks (FR-23 to FR-27).

Every check is rule-based Python; the LLM is never trusted to police policy.
Results feed plan validation, the manager approval gate and the audit trail.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from backend.app.models.plan_schemas import ComplianceCheck, ComplianceResult
from backend.app.services import identity_service
from backend.app.services.sales_data_service import get_contact_policy

REQUIRED_ITEM_FIELDS = (
    "account_id",
    "account_name",
    "recommended_action",
    "reason",
    "priority_rank",
)


def determine_contact_method(account: Dict[str, Any]) -> str:
    return str(account.get("preferred_contact_method") or "EMAIL").upper()


def check_ownership(account: Dict[str, Any], territory_id: str) -> ComplianceCheck:
    """FR-23 / FR-18: the account is assigned to a representative for its territory."""
    owner_id = account.get("owner_id")
    if not owner_id:
        return ComplianceCheck(
            check="ownership",
            status="failed",
            detail=f"Account {account.get('account_id')} has no assigned representative.",
        )
    if not identity_service.can_access_territory(owner_id, territory_id):
        owner = identity_service.get_user(owner_id)
        owner_label = owner.get("name") if owner else "unknown user"
        return ComplianceCheck(
            check="ownership",
            status="failed",
            detail=(
                f"Ownership conflict: {owner_label} ({owner_id}) is not assigned to "
                f"territory {territory_id}; route per ownership rules."
            ),
        )
    return ComplianceCheck(
        check="ownership",
        status="passed",
        detail=f"Account owner {owner_id} is assigned to territory {territory_id}.",
    )


def check_access(user_id: str, account: Dict[str, Any]) -> ComplianceCheck:
    """FR-24: the requesting user is authorized to see the account."""
    if identity_service.can_access_account(user_id, account):
        return ComplianceCheck(
            check="access",
            status="passed",
            detail=f"User {user_id} is authorized for account {account.get('account_id')}.",
        )
    return ComplianceCheck(
        check="access",
        status="failed",
        detail=f"User {user_id} is not authorized for account {account.get('account_id')}.",
    )


def check_contact_policy(
    account: Dict[str, Any],
    contact_method: str,
    is_sales_pitch: bool,
    open_high_severity_issues: bool,
) -> ComplianceCheck:
    """FR-25: the proposed contact method is permitted by contact policy."""
    policy = get_contact_policy(contact_method)
    if not policy:
        return ComplianceCheck(
            check="contact_policy",
            status="failed",
            detail=f"No contact policy found for method {contact_method}.",
        )
    if not policy.get("allowed", False):
        return ComplianceCheck(
            check="contact_policy",
            status="failed",
            detail=policy.get("notes", f"Method {contact_method} is not permitted."),
        )
    if is_sales_pitch and open_high_severity_issues:
        return ComplianceCheck(
            check="contact_policy",
            status="failed",
            detail=(
                "Sales outreach is not permitted while the account has an unresolved "
                "high-severity service issue; resolve the issue first."
            ),
        )
    return ComplianceCheck(
        check="contact_policy",
        status="passed",
        detail=policy.get("notes", f"Method {contact_method} is permitted."),
    )


def check_evidence(facts: Sequence[Dict[str, Any]], citations: Sequence[str]) -> ComplianceCheck:
    """FR-26: each recommendation carries supporting, traceable evidence."""
    uncited = [fact for fact in facts if not fact.get("source_id")]
    if uncited or not citations:
        return ComplianceCheck(
            check="evidence",
            status="failed",
            detail="Recommendation is missing a source record or document citation.",
        )
    return ComplianceCheck(
        check="evidence",
        status="passed",
        detail=f"{len(citations)} citation(s) support this recommendation.",
    )


def check_required_fields(item: Dict[str, Any]) -> ComplianceCheck:
    """FR-27: required fields are present and correctly typed."""
    missing = [
        field
        for field in REQUIRED_ITEM_FIELDS
        if item.get(field) in (None, "", [])
    ]
    if missing:
        return ComplianceCheck(
            check="schema",
            status="failed",
            detail=f"Missing required field(s): {', '.join(missing)}.",
        )
    if not isinstance(item.get("priority_rank"), int):
        return ComplianceCheck(
            check="schema",
            status="failed",
            detail="priority_rank must be an integer.",
        )
    return ComplianceCheck(
        check="schema", status="passed", detail="All required fields present and typed."
    )


def _as_check(check: Any) -> ComplianceCheck:
    if isinstance(check, ComplianceCheck):
        return check
    return ComplianceCheck(**check)


def _aggregate(checks: List[Any]) -> ComplianceResult:
    normalized = [_as_check(check) for check in checks]
    if any(check.status == "failed" for check in normalized):
        status = "failed"
    elif any(check.status == "warning" for check in normalized):
        status = "warning"
    else:
        status = "passed"
    return ComplianceResult(status=status, checks=normalized)


def evaluate_item(
    account: Dict[str, Any],
    territory_id: str,
    user_id: str,
    item: Dict[str, Any],
    citations: Sequence[str],
    facts: Sequence[Dict[str, Any]],
    contact_method: str,
    is_sales_pitch: bool,
    open_high_severity_issues: bool,
) -> ComplianceResult:
    checks = [
        check_required_fields(item),
        check_ownership(account, territory_id),
        check_access(user_id, account),
        check_evidence(facts, citations),
        check_contact_policy(
            account, contact_method, is_sales_pitch, open_high_severity_issues
        ),
    ]
    return _aggregate(checks)


def evaluate_plan(items: List[Dict[str, Any]]) -> ComplianceResult:
    """Plan-level rollup of item compliance used for the approval gate."""
    if not items:
        return _aggregate(
            [ComplianceCheck(check="plan_content", status="failed", detail="Plan has no items.")]
        )
    checks: List[Any] = []
    for item in items:
        compliance = item.get("compliance", {}) if isinstance(item, dict) else item.compliance
        if isinstance(compliance, dict):
            checks.extend(compliance.get("checks", []))
        else:
            checks.extend(compliance.checks)
    return _aggregate(checks)
