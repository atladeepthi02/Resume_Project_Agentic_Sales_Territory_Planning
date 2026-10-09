"""Identity and authorization helpers (FR-8, FR-24).

Access is enforced deterministically against an in-memory user directory so the
retrieval layer can filter unauthorized records before they reach the LLM.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# Roles: SALES_MANAGER approves plans for a territory, SALES_REP owns accounts,
# SALES_OPS configures rules, AUDITOR reviews decisions.
USERS: Dict[str, Dict[str, Any]] = {
    "mgr-001": {
        "user_id": "mgr-001",
        "name": "Alicia Ng",
        "role": "SALES_MANAGER",
        "territories": ["T001"],
    },
    "mgr-002": {
        "user_id": "mgr-002",
        "name": "Marco Diaz",
        "role": "SALES_MANAGER",
        "territories": ["T002"],
    },
    "mgr-003": {
        "user_id": "mgr-003",
        "name": "Priya Shah",
        "role": "SALES_MANAGER",
        "territories": ["T003"],
    },
    "ops-001": {
        "user_id": "ops-001",
        "name": "Sales Operations",
        "role": "SALES_OPS",
        "territories": ["*"],
    },
    "audit-001": {
        "user_id": "audit-001",
        "name": "Audit Reviewer",
        "role": "AUDITOR",
        "territories": ["*"],
    },
    "rep-042": {
        "user_id": "rep-042",
        "name": "Dana Reyes",
        "role": "SALES_REP",
        "territories": ["T001"],
        "accounts": ["ACC1001", "ACC1002"],
    },
}

DIRECTORY_ALLOWING_ALL = {"SALES_OPS", "AUDITOR"}


def get_user(user_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not user_id:
        return None
    return USERS.get(user_id)


def list_users() -> List[Dict[str, Any]]:
    return list(USERS.values())


def has_global_access(user_id: Optional[str]) -> bool:
    user = get_user(user_id)
    return bool(user and user.get("role") in DIRECTORY_ALLOWING_ALL)


def can_access_territory(user_id: Optional[str], territory_id: Optional[str]) -> bool:
    user = get_user(user_id)
    if not user:
        return False
    if user.get("role") in DIRECTORY_ALLOWING_ALL:
        return True
    territories = user.get("territories", [])
    return "*" in territories or territory_id in territories


def can_access_account(user_id: Optional[str], account: Dict[str, Any]) -> bool:
    """FR-8: only records the requesting user may see are ever retrieved."""
    user = get_user(user_id)
    if not user:
        return False

    permissions = account.get("permissions", {}) or {}
    if user_id in permissions.get("allowed_user_ids", []):
        return True

    role = user.get("role")
    if role in DIRECTORY_ALLOWING_ALL:
        return True
    if role == "SALES_MANAGER":
        return can_access_territory(user_id, account.get("territory_id"))
    if role == "SALES_REP":
        return (
            account.get("account_id") in user.get("accounts", [])
            or account.get("owner_id") == user_id
        )
    return False


def is_manager(user_id: Optional[str]) -> bool:
    """FR-29: only a sales manager may approve important actions."""
    user = get_user(user_id)
    return bool(user and user.get("role") == "SALES_MANAGER")
