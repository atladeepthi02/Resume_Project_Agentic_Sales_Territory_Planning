"""Scoring-rules configuration API (FR-12).

Lets Sales Operations inspect and update ranking weights without code changes.
"""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field
from fastapi import APIRouter

from backend.app.services import scoring_service
from backend.app.services.observability import log_event

router = APIRouter(prefix="/v1/scoring-rules", tags=["configuration"])


class ScoringRulesUpdate(BaseModel):
    weights: Dict[str, float] = Field(default_factory=dict)
    thresholds: Dict[str, float] = Field(default_factory=dict)
    updates: Dict[str, Any] = Field(default_factory=dict)


@router.get("")
def get_rules() -> Dict[str, Any]:
    return scoring_service.get_scoring_rules()


@router.put("")
def update_rules(payload: ScoringRulesUpdate) -> Dict[str, Any]:
    overrides: Dict[str, Any] = {**payload.updates}
    if payload.weights:
        overrides["weights"] = payload.weights
    if payload.thresholds:
        overrides["thresholds"] = payload.thresholds
    rules = scoring_service.update_scoring_rules(overrides)
    log_event("scoring_rules_updated", keys=sorted(overrides.keys()))
    return rules
