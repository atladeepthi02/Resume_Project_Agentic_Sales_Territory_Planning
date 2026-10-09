"""CRM-compatible export of approved actions (FR-32, FR-33, FR-34).

Exports are idempotent: repeating the same export for the same plan version with
the same approved item set returns the original export record (and content) with
``duplicate=True`` instead of creating a new one.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List

from backend.app.models.plan_schemas import ExportResult, Plan

CSV_COLUMNS = [
    "plan_id",
    "plan_version",
    "account_id",
    "account_name",
    "owner",
    "priority_rank",
    "recommended_action",
    "reason",
    "citations",
    "requires_approval",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _action_rows(plan: Plan) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for item in plan.items:
        if item.status != "APPROVED":
            continue
        rows.append(
            {
                "plan_id": plan.plan_id,
                "plan_version": plan.version,
                "account_id": item.account_id,
                "account_name": item.account_name,
                "owner": item.owner,
                "priority_rank": item.priority_rank,
                "recommended_action": item.recommended_action,
                "reason": item.reason,
                "citations": ";".join(item.citations),
                "requires_approval": item.requires_approval,
            }
        )
    return rows


def export_checksum(plan: Plan, fmt: str) -> str:
    """Deterministic fingerprint of the approved action set (FR-34)."""
    payload = {
        "plan_id": plan.plan_id,
        "plan_version": plan.version,
        "format": fmt,
        "items": sorted(
            f"{item.account_id}:{item.recommended_action}"
            for item in plan.items
            if item.status == "APPROVED"
        ),
    }
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def render_export(plan: Plan, fmt: str) -> str:
    rows = _action_rows(plan)
    if fmt == "json":
        return json.dumps(
            {"plan_id": plan.plan_id, "plan_version": plan.version, "actions": rows},
            indent=2,
        )
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def build_export(
    plan: Plan, fmt: str, existing: Dict[str, ExportResult] | None = None
) -> ExportResult:
    """Create an export result, honouring idempotency via the checksum registry."""
    checksum = export_checksum(plan, fmt)
    registry = existing or {}
    if checksum in registry:
        prior = registry[checksum]
        return prior.model_copy(update={"duplicate": True})

    result = ExportResult(
        export_id=f"exp-{uuid.uuid4().hex[:12]}",
        plan_id=plan.plan_id,
        plan_version=plan.version,
        format="json" if fmt == "json" else "csv",
        item_count=len(_action_rows(plan)),
        checksum=checksum,
        duplicate=False,
        created_at=_now(),
        content=render_export(plan, fmt),
    )
    return result
