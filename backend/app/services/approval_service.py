from typing import Any, Dict


def requires_approval(action_type: str) -> bool:
    return action_type in {"CHANGING_OWNERSHIP", "PRICING_EXCEPTION", "STRATEGIC_PLAN_CHANGE"}


def approve_action(action: Dict[str, Any]) -> Dict[str, Any]:
    return {"workflow_id": action.get("workflow_id"), "status": "APPROVED"}
