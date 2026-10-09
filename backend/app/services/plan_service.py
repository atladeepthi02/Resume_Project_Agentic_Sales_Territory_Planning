"""Plan lifecycle service backing the /v1/plans API (PRD sections 6-10).

Holds plan versions, the human approval gate, idempotency keys and the audit
trail. Persistence is in-memory for the v1 prototype; the interface is the seam
where a real store would be substituted.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.models.plan_schemas import (
    ApprovalRecord,
    ApprovePlanRequest,
    AuditEvent,
    AuditTrail,
    CreatePlanRequest,
    ExportResult,
    Plan,
    PlanSummary,
    RejectPlanRequest,
    UpdatePlanRequest,
)
from backend.app.services import (
    compliance_service,
    export_service,
    identity_service,
    plan_drafting_service,
)
from backend.app.services.plan_errors import (
    InvalidPlanStateError,
    NoApprovedItemsError,
    PlanNotFoundError,
    TerritoryNotFoundError,
    UnauthorizedError,
)
from backend.app.services.sales_data_service import (
    get_accounts_by_territory,
    get_territory,
)

APPROVABLE_STATES = {"PENDING_APPROVAL"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PlanStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._plans: Dict[str, Plan] = {}
        self._audit: Dict[str, List[AuditEvent]] = {}
        self._exports: Dict[str, Dict[str, ExportResult]] = {}
        self._idempotency: Dict[str, Any] = {}

    # -- idempotency -----------------------------------------------------
    def get_idempotent(self, key: Optional[str]) -> Any | None:
        if not key:
            return None
        with self._lock:
            return self._idempotency.get(key)

    def remember_idempotent(self, key: Optional[str], value: Any) -> None:
        if not key:
            return
        with self._lock:
            self._idempotency[key] = value

    def reset(self) -> None:
        with self._lock:
            self._plans.clear()
            self._audit.clear()
            self._exports.clear()
            self._idempotency.clear()

    # -- audit -----------------------------------------------------------
    def _record(
        self, plan_id: str, event_type: str, actor: str, version: int, details: Dict[str, Any]
    ) -> None:
        event = AuditEvent(
            event_id=f"evt-{uuid.uuid4().hex[:10]}",
            event_type=event_type,
            actor=actor,
            timestamp=_now(),
            plan_version=version,
            details=details,
        )
        self._audit.setdefault(plan_id, []).append(event)

    # -- queries ---------------------------------------------------------
    def get_plan(self, plan_id: str) -> Plan:
        with self._lock:
            plan = self._plans.get(plan_id)
        if plan is None:
            raise PlanNotFoundError(f"Plan {plan_id} was not found.")
        return plan

    def list_plans(self) -> List[PlanSummary]:
        with self._lock:
            plans = list(self._plans.values())
        return [
            PlanSummary(
                plan_id=plan.plan_id,
                territory_id=plan.territory_id,
                status=plan.status,
                version=plan.version,
                item_count=len(plan.items),
                created_at=plan.created_at,
                updated_at=plan.updated_at,
            )
            for plan in sorted(plans, key=lambda p: p.created_at, reverse=True)
        ]

    def get_audit(self, plan_id: str) -> AuditTrail:
        self.get_plan(plan_id)
        with self._lock:
            events = list(self._audit.get(plan_id, []))
        return AuditTrail(plan_id=plan_id, events=events)

    # -- commands --------------------------------------------------------
    def create_plan(self, request: CreatePlanRequest) -> Plan:
        """FR-1..FR-19: retrieve authorized records and draft a cited plan."""
        territory = get_territory(request.territory_id)
        if not territory:
            raise TerritoryNotFoundError(
                f"Territory {request.territory_id} was not found."
            )
        if not identity_service.get_user(request.user_id):
            raise UnauthorizedError(f"Unknown user {request.user_id}.")
        if not identity_service.can_access_territory(request.user_id, request.territory_id):
            raise UnauthorizedError(
                f"User {request.user_id} is not authorized for territory "
                f"{request.territory_id}."
            )

        accounts = get_accounts_by_territory(request.territory_id)
        authorized = [
            account
            for account in accounts
            if identity_service.can_access_account(request.user_id, account)
        ]
        excluded = [
            account["account_id"] for account in accounts if account not in authorized
        ]

        allowed_ids = request.filters.get("account_ids")
        if allowed_ids:
            authorized = [
                account for account in authorized if account["account_id"] in allowed_ids
            ]

        items, any_stale, rules_version = plan_drafting_service.draft_plan_items(
            authorized, request.territory_id, request.user_id
        )

        min_level = request.filters.get("min_priority_level")
        if min_level:
            items = [
                item
                for item in items
                if _level_ordinal(item["priority_level"]) >= _level_ordinal(min_level)
            ]
            for rank, item in enumerate(items, start=1):
                item["priority_rank"] = rank

        validation = compliance_service.evaluate_plan(items)
        plan_id = f"plan-{uuid.uuid4().hex[:12]}"
        timestamp = _now()
        plan = Plan(
            plan_id=plan_id,
            territory_id=request.territory_id,
            user_id=request.user_id,
            status="PENDING_APPROVAL",
            version=1,
            time_window=request.time_window,
            created_at=timestamp,
            updated_at=timestamp,
            items=items,
            validation=validation,
            stale_data=any_stale,
            excluded_account_ids=excluded,
            scoring_rules_version=rules_version,
        )
        with self._lock:
            self._plans[plan_id] = plan
            self._record(
                plan_id,
                "PLAN_CREATED",
                request.user_id,
                plan.version,
                {
                    "territory_id": request.territory_id,
                    "item_count": len(items),
                    "excluded_account_ids": excluded,
                    "validation_status": validation.status,
                },
            )
        return plan

    def edit_plan(self, plan_id: str, request: UpdatePlanRequest) -> Plan:
        """FR-30 / US-4: a manager edits the draft before approving."""
        plan = self.get_plan(plan_id)
        if plan.status not in APPROVABLE_STATES:
            raise InvalidPlanStateError(
                f"Plan {plan_id} is {plan.status} and can no longer be edited."
            )
        if not identity_service.is_manager(request.user_id):
            raise UnauthorizedError(
                f"User {request.user_id} is not authorized to edit plan {plan_id}."
            )

        patches = {patch.item_id: patch for patch in request.items}
        updated_items = []
        for item in plan.items:
            patch = patches.get(item.item_id)
            if patch:
                data = item.model_dump()
                for field in ("recommended_action", "reason", "requires_approval"):
                    value = getattr(patch, field)
                    if value is not None:
                        data[field] = value
                updated_items.append(type(item)(**data))
            else:
                updated_items.append(item)

        new_version = plan.version + 1
        updated = plan.model_copy(
            update={
                "items": updated_items,
                "version": new_version,
                "updated_at": _now(),
                "validation": compliance_service.evaluate_plan(
                    [item.model_dump() for item in updated_items]
                ),
            }
        )
        with self._lock:
            self._plans[plan_id] = updated
            self._record(
                plan_id,
                "PLAN_EDITED",
                request.user_id,
                new_version,
                {"edited_item_ids": list(patches.keys())},
            )
        return updated

    def approve_plan(self, plan_id: str, request: ApprovePlanRequest) -> Plan:
        """FR-29..FR-31: manager approval gate, recorded with user and version."""
        plan = self.get_plan(plan_id)
        if plan.status == "REJECTED":
            raise InvalidPlanStateError(f"Plan {plan_id} was rejected and cannot be approved.")
        if not identity_service.is_manager(request.user_id):
            raise UnauthorizedError(
                f"User {request.user_id} is not a sales manager and cannot approve plans."
            )
        if not identity_service.can_access_territory(request.user_id, plan.territory_id):
            raise UnauthorizedError(
                f"User {request.user_id} cannot approve plans for territory "
                f"{plan.territory_id}."
            )

        target_ids = set(request.item_ids) if request.item_ids else None
        updated_items = []
        approved_ids: List[str] = []
        for item in plan.items:
            if item.status == "APPROVED":
                updated_items.append(item)
                continue
            if target_ids is None or item.item_id in target_ids:
                updated_items.append(item.model_copy(update={"status": "APPROVED"}))
                approved_ids.append(item.item_id)
            else:
                updated_items.append(item)

        if not approved_ids:
            raise InvalidPlanStateError("No matching items were available to approve.")

        all_approved = all(item.status == "APPROVED" for item in updated_items)
        record = ApprovalRecord(
            approver_id=request.user_id,
            decision="APPROVED",
            timestamp=_now(),
            plan_version=plan.version,
            item_ids=approved_ids,
            reason=request.reason,
        )
        updated = plan.model_copy(
            update={
                "items": updated_items,
                "status": "APPROVED" if all_approved else "PENDING_APPROVAL",
                "approval": record,
                "updated_at": _now(),
            }
        )
        with self._lock:
            self._plans[plan_id] = updated
            self._record(
                plan_id,
                "PLAN_APPROVED",
                request.user_id,
                plan.version,
                {"approved_item_ids": approved_ids, "plan_status": updated.status},
            )
        return updated

    def reject_plan(self, plan_id: str, request: RejectPlanRequest) -> Plan:
        plan = self.get_plan(plan_id)
        if plan.status == "EXPORTED":
            raise InvalidPlanStateError(f"Plan {plan_id} was exported and cannot be rejected.")
        if not identity_service.is_manager(request.user_id):
            raise UnauthorizedError(
                f"User {request.user_id} is not authorized to reject plan {plan_id}."
            )

        target_ids = set(request.item_ids) if request.item_ids else None
        updated_items = []
        rejected_ids: List[str] = []
        for item in plan.items:
            if target_ids is None or item.item_id in target_ids:
                updated_items.append(item.model_copy(update={"status": "REJECTED"}))
                rejected_ids.append(item.item_id)
            else:
                updated_items.append(item)

        all_rejected = bool(updated_items) and all(
            item.status == "REJECTED" for item in updated_items
        )
        record = ApprovalRecord(
            approver_id=request.user_id,
            decision="REJECTED",
            timestamp=_now(),
            plan_version=plan.version,
            item_ids=rejected_ids,
            reason=request.reason,
        )
        updated = plan.model_copy(
            update={
                "items": updated_items,
                "status": "REJECTED" if all_rejected else plan.status,
                "approval": record,
                "updated_at": _now(),
            }
        )
        with self._lock:
            self._plans[plan_id] = updated
            self._record(
                plan_id,
                "PLAN_REJECTED",
                request.user_id,
                plan.version,
                {"rejected_item_ids": rejected_ids, "reason": request.reason},
            )
        return updated

    def export_plan(self, plan_id: str, fmt: str) -> ExportResult:
        """FR-32..FR-34: export approved items in a CRM-compatible format."""
        plan = self.get_plan(plan_id)
        approved = [item for item in plan.items if item.status == "APPROVED"]
        if not approved:
            raise NoApprovedItemsError(
                f"Plan {plan_id} has no approved items to export."
            )

        with self._lock:
            registry = self._exports.setdefault(plan_id, {})
            result = export_service.build_export(plan, fmt, registry)
            if not result.duplicate:
                registry[result.checksum] = result
                self._plans[plan_id] = plan.model_copy(
                    update={"status": "EXPORTED", "updated_at": _now()}
                )
                self._record(
                    plan_id,
                    "PLAN_EXPORTED",
                    plan.user_id,
                    plan.version,
                    {
                        "export_id": result.export_id,
                        "format": result.format,
                        "item_count": result.item_count,
                    },
                )
            else:
                self._record(
                    plan_id,
                    "PLAN_EXPORT_DUPLICATE",
                    plan.user_id,
                    plan.version,
                    {"export_id": result.export_id, "format": result.format},
                )
        return result


def _level_ordinal(level: str) -> int:
    return {"LOW": 0, "MEDIUM": 1, "HIGH": 2}.get(str(level).upper(), 0)


plan_store = PlanStore()

# Convenience module-level accessors used by the API layer.
create_plan = plan_store.create_plan
get_plan = plan_store.get_plan
list_plans = plan_store.list_plans
edit_plan = plan_store.edit_plan
approve_plan = plan_store.approve_plan
reject_plan = plan_store.reject_plan
export_plan = plan_store.export_plan
get_audit = plan_store.get_audit
