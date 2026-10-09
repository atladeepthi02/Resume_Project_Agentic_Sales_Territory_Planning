"""Pydantic schemas for the plan-centric API (PRD section 10).

These models are the single source of truth for request/response validation and
for the plan-item shape used across the workflow, compliance checks and export.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

ComplianceStatus = Literal["passed", "failed", "warning"]
ItemStatus = Literal["PENDING", "APPROVED", "REJECTED"]
PlanStatus = Literal["PENDING_APPROVAL", "APPROVED", "REJECTED", "EXPORTED"]
PlanDecision = Literal["APPROVED", "REJECTED"]
ExportFormat = Literal["csv", "json"]


class ComplianceCheck(BaseModel):
    check: str
    status: ComplianceStatus
    detail: str = ""


class ComplianceResult(BaseModel):
    status: ComplianceStatus = "passed"
    checks: List[ComplianceCheck] = Field(default_factory=list)

    @field_validator("status")
    @classmethod
    def _keep_literal(cls, value: str) -> str:
        return value


class PlanItemFact(BaseModel):
    text: str
    source_id: str


class PlanItem(BaseModel):
    item_id: str
    account_id: str
    account_name: str
    owner: str = ""
    priority_rank: int = 0
    priority_score: float = 0.0
    priority_level: str = "MEDIUM"
    facts: List[PlanItemFact] = Field(default_factory=list)
    opportunity_summary: str = "No open opportunity on record."
    recommended_action: str
    reason: str
    citations: List[str] = Field(default_factory=list)
    requires_approval: bool = True
    compliance: ComplianceResult = Field(default_factory=ComplianceResult)
    factors: List[str] = Field(default_factory=list)
    status: ItemStatus = "PENDING"
    stale: bool = False
    stale_reason: Optional[str] = None
    missing_data: List[str] = Field(default_factory=list)


class ApprovalRecord(BaseModel):
    approver_id: str
    decision: PlanDecision
    timestamp: str
    plan_version: int
    item_ids: List[str] = Field(default_factory=list)
    reason: Optional[str] = None


class AuditEvent(BaseModel):
    event_id: str
    event_type: str
    actor: str
    timestamp: str
    plan_version: int
    details: Dict[str, Any] = Field(default_factory=dict)


class Plan(BaseModel):
    plan_id: str
    territory_id: str
    user_id: str
    status: PlanStatus = "PENDING_APPROVAL"
    version: int = 1
    time_window: str = "CURRENT_QUARTER"
    created_at: str
    updated_at: str
    items: List[PlanItem] = Field(default_factory=list)
    validation: ComplianceResult = Field(default_factory=ComplianceResult)
    approval: Optional[ApprovalRecord] = None
    stale_data: bool = False
    excluded_account_ids: List[str] = Field(default_factory=list)
    scoring_rules_version: Optional[str] = None


class CreatePlanRequest(BaseModel):
    territory_id: str
    user_id: str
    time_window: str = "CURRENT_QUARTER"
    filters: Dict[str, Any] = Field(default_factory=dict)


class PlanItemPatch(BaseModel):
    item_id: str
    recommended_action: Optional[str] = None
    reason: Optional[str] = None
    requires_approval: Optional[bool] = None


class UpdatePlanRequest(BaseModel):
    user_id: str
    items: List[PlanItemPatch] = Field(default_factory=list)


class ApprovePlanRequest(BaseModel):
    user_id: str
    item_ids: Optional[List[str]] = None
    reason: Optional[str] = None


class RejectPlanRequest(BaseModel):
    user_id: str
    item_ids: Optional[List[str]] = None
    reason: str = "Rejected by reviewer."


class AuditTrail(BaseModel):
    plan_id: str
    events: List[AuditEvent] = Field(default_factory=list)


class ExportResult(BaseModel):
    export_id: str
    plan_id: str
    plan_version: int
    format: ExportFormat
    item_count: int
    checksum: str
    duplicate: bool = False
    created_at: str
    content: str


class PlanSummary(BaseModel):
    plan_id: str
    territory_id: str
    status: PlanStatus
    version: int
    item_count: int
    created_at: str
    updated_at: str
