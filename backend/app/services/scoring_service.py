"""Deterministic account scoring (FR-11, FR-12, FR-13, FR-14).

Weights and thresholds live in ``backend/app/config/scoring_rules.json`` so Sales
Operations can tune prioritisation without code changes. All arithmetic happens
here in Python, never in the LLM (FR-10).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

RULES_PATH = Path(__file__).resolve().parent.parent / "config" / "scoring_rules.json"

DEFAULT_RULES: Dict[str, Any] = {
    "version": "2026-10-01",
    "weights": {
        "opportunity_value": 0.30,
        "past_sales_performance": 0.20,
        "product_adoption": 0.15,
        "unresolved_service_issues": 0.15,
        "opportunity_stage": 0.15,
        "territory_rules": 0.05,
    },
    "service_issue_penalty_weight": 0.20,
    "opportunity_value_normalizer": 250000,
    "revenue_normalizer": 1000000,
    "high_value_opportunity_threshold": 200000,
    "thresholds": {"high": 70.0, "medium": 45.0},
}

STAGE_SCORES: Dict[str, float] = {
    "NEGOTIATION": 1.0,
    "PROPOSAL": 0.85,
    "QUALIFICATION": 0.6,
    "QUALIFYING": 0.6,
    "DISCOVERY": 0.4,
    "AT_RISK": 0.1,
}

_OVERRIDES: Dict[str, Any] = {}


def get_scoring_rules() -> Dict[str, Any]:
    """Return the current scoring rules, layering runtime overrides last."""
    rules = _load_rules_file()
    merged = {**rules, **{k: v for k, v in _OVERRIDES.items() if k != "weights"}}
    merged["weights"] = {**rules.get("weights", {}), **_OVERRIDES.get("weights", {})}
    merged["thresholds"] = {**rules.get("thresholds", {}), **_OVERRIDES.get("thresholds", {})}
    return merged


def update_scoring_rules(overrides: Dict[str, Any]) -> Dict[str, Any]:
    """FR-12: Sales Operations can change weights/rules without code changes."""
    global _OVERRIDES
    if "weights" in overrides and isinstance(overrides["weights"], dict):
        _OVERRIDES["weights"] = {**_OVERRIDES.get("weights", {}), **overrides["weights"]}
    if "thresholds" in overrides and isinstance(overrides["thresholds"], dict):
        _OVERRIDES["thresholds"] = {**_OVERRIDES.get("thresholds", {}), **overrides["thresholds"]}
    for key, value in overrides.items():
        if key not in {"weights", "thresholds"}:
            _OVERRIDES[key] = value
    return get_scoring_rules()


def reset_scoring_rules() -> None:
    global _OVERRIDES
    _OVERRIDES = {}


@lru_cache(maxsize=1)
def _load_rules_file() -> Dict[str, Any]:
    try:
        with RULES_PATH.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return json.loads(json.dumps(DEFAULT_RULES))
    merged = json.loads(json.dumps(DEFAULT_RULES))
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _stage_score(stage: str) -> float:
    return STAGE_SCORES.get(str(stage).upper(), 0.25)


def compute_account_score(
    account: Dict[str, Any],
    opportunities: List[Dict[str, Any]],
    service_issues: List[Dict[str, Any]],
    rules: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Score one account and expose the factors behind the position (FR-11/14)."""
    rules = rules or get_scoring_rules()
    weights = rules["weights"]

    pipeline_value = sum(float(opp.get("value", 0) or 0) for opp in opportunities)
    best_stage = max((_stage_score(opp.get("stage", "")) for opp in opportunities), default=0.0)

    opportunity_value_factor = _clamp(pipeline_value / float(rules["opportunity_value_normalizer"]))
    revenue_factor = _clamp(float(account.get("revenue", 0) or 0) / float(rules["revenue_normalizer"]))
    growth_factor = _clamp((float(account.get("growth", 0) or 0) + 0.1) / 0.4)
    performance_factor = 0.6 * revenue_factor + 0.4 * growth_factor
    adoption_factor = _clamp(float(account.get("product_adoption", 0) or 0))

    open_issues = [
        issue for issue in service_issues if str(issue.get("status", "")).upper() == "OPEN"
    ]
    issue_pressure = _clamp(len(open_issues) / 3.0)
    service_health_factor = 1.0 - issue_pressure
    rules_factor = _clamp(float(account.get("strategic_importance", 0.5) or 0.0))

    factors = {
        "opportunity_value": opportunity_value_factor,
        "past_sales_performance": performance_factor,
        "product_adoption": adoption_factor,
        "unresolved_service_issues": service_health_factor,
        "opportunity_stage": best_stage,
        "territory_rules": rules_factor,
    }

    weighted = sum(factors[name] * float(weights.get(name, 0.0)) for name in factors)
    penalty = issue_pressure * float(rules.get("service_issue_penalty_weight", 0.0))
    score = _clamp(weighted - penalty) * 100.0

    thresholds = rules["thresholds"]
    if score >= float(thresholds["high"]):
        level = "HIGH"
    elif score >= float(thresholds["medium"]):
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "priority_score": round(score, 2),
        "priority_level": level,
        "pipeline_value": pipeline_value,
        "factors": {name: round(value * 100.0, 2) for name, value in factors.items()},
        "factor_drivers": _describe_drivers(factors, len(open_issues)),
        "open_service_issues": len(open_issues),
        "high_value_opportunity": pipeline_value >= float(rules["high_value_opportunity_threshold"]),
        "scoring_rules_version": rules.get("version"),
    }


def _describe_drivers(factors: Dict[str, float], open_issues: int) -> List[str]:
    """Human-readable reasons a factor moved the score (FR-14)."""
    labels = {
        "opportunity_value": "Opportunity value",
        "past_sales_performance": "Past sales performance",
        "product_adoption": "Product adoption",
        "unresolved_service_issues": "Unresolved service issues",
        "opportunity_stage": "Opportunity stage",
        "territory_rules": "Territory / business rules",
    }
    drivers = []
    for name, value in sorted(factors.items(), key=lambda item: item[1], reverse=True):
        direction = "supports prioritisation" if value >= 0.5 else "reduces prioritisation"
        drivers.append(f"{labels.get(name, name)}: {direction} ({round(value * 100)}%)")
    if open_issues:
        drivers.append(f"{open_issues} unresolved service issue(s) applied a priority penalty")
    return drivers
