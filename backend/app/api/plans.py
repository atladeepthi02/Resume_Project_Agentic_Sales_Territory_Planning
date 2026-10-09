"""Plan-centric REST API (PRD section 10).

All endpoints validate request/response bodies with Pydantic, and mutating
endpoints accept an ``Idempotency-Key`` header so retries are safe (FR-34).
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Header, HTTPException, Query

from backend.app.models.plan_schemas import (
    ApprovePlanRequest,
    AuditTrail,
    CreatePlanRequest,
    ExportResult,
    Plan,
    PlanSummary,
    RejectPlanRequest,
    UpdatePlanRequest,
)
from backend.app.services import plan_service
from backend.app.services.observability import log_event
from backend.app.services.plan_errors import (
    InvalidPlanStateError,
    NoApprovedItemsError,
    PlanError,
    PlanNotFoundError,
    TerritoryNotFoundError,
    UnauthorizedError,
)

router = APIRouter(prefix="/v1/plans", tags=["plans"])


def _status_for(exc: PlanError) -> int:
    if isinstance(exc, (PlanNotFoundError, TerritoryNotFoundError)):
        return 404
    if isinstance(exc, UnauthorizedError):
        return 403
    if isinstance(exc, (InvalidPlanStateError, NoApprovedItemsError)):
        return 409
    return 500


def _raise(exc: PlanError) -> None:
    raise HTTPException(status_code=_status_for(exc), detail=str(exc)) from exc


def _idempotent(key: str | None, action):
    """FR-34: replay the original result for a repeated idempotency key."""
    if key:
        cached = plan_service.plan_store.get_idempotent(key)
        if cached is not None:
            log_event("idempotent_replay", idempotency_key=key)
            return cached
    result = action()
    if key:
        plan_service.plan_store.remember_idempotent(key, result)
    return result


@router.post("", response_model=Plan, status_code=201)
def create_plan(request: CreatePlanRequest) -> Dict[str, Any]:
    try:
        plan = plan_service.create_plan(request)
    except PlanError as exc:
        _raise(exc)
    log_event(
        "plan_created",
        plan_id=plan.plan_id,
        territory_id=plan.territory_id,
        item_count=len(plan.items),
    )
    return plan.model_dump()


@router.get("", response_model=List[PlanSummary])
def list_plans() -> List[Dict[str, Any]]:
    return [summary.model_dump() for summary in plan_service.list_plans()]


@router.get("/{plan_id}", response_model=Plan)
def get_plan(plan_id: str) -> Dict[str, Any]:
    try:
        plan = plan_service.get_plan(plan_id)
    except PlanError as exc:
        _raise(exc)
    return plan.model_dump()


@router.patch("/{plan_id}", response_model=Plan)
def edit_plan(plan_id: str, request: UpdatePlanRequest) -> Dict[str, Any]:
    try:
        plan = plan_service.edit_plan(plan_id, request)
    except PlanError as exc:
        _raise(exc)
    log_event("plan_edited", plan_id=plan_id, version=plan.version)
    return plan.model_dump()


@router.post("/{plan_id}/approve", response_model=Plan)
def approve_plan(
    plan_id: str,
    request: ApprovePlanRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Dict[str, Any]:
    def action() -> Plan:
        try:
            return plan_service.approve_plan(plan_id, request)
        except PlanError as exc:
            _raise(exc)

    plan = _idempotent(idempotency_key, action)
    log_event("plan_approved", plan_id=plan_id, status=plan.status)
    return plan.model_dump()


@router.post("/{plan_id}/reject", response_model=Plan)
def reject_plan(
    plan_id: str,
    request: RejectPlanRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Dict[str, Any]:
    def action() -> Plan:
        try:
            return plan_service.reject_plan(plan_id, request)
        except PlanError as exc:
            _raise(exc)

    plan = _idempotent(idempotency_key, action)
    log_event("plan_rejected", plan_id=plan_id, status=plan.status)
    return plan.model_dump()


@router.post("/{plan_id}/export", response_model=ExportResult)
def export_plan(
    plan_id: str,
    format: str = Query(default="csv", pattern="^(csv|json)$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Dict[str, Any]:
    def action() -> ExportResult:
        try:
            return plan_service.export_plan(plan_id, format)
        except PlanError as exc:
            _raise(exc)

    result = _idempotent(idempotency_key, action)
    log_event(
        "plan_exported",
        plan_id=plan_id,
        format=result.format,
        duplicate=result.duplicate,
    )
    return result.model_dump()


@router.get("/{plan_id}/audit", response_model=AuditTrail)
def get_audit(plan_id: str) -> Dict[str, Any]:
    try:
        trail = plan_service.get_audit(plan_id)
    except PlanError as exc:
        _raise(exc)
    return trail.model_dump()
