from typing import Any, Dict


def create_sales_task(account_id: str, action_type: str, reason: str) -> Dict[str, Any]:
    return {"action_type": action_type, "account_id": account_id, "status": "EXECUTED", "task_id": f"TASK-{account_id}-001", "reason": reason}


def create_follow_up(account_id: str, reason: str) -> Dict[str, Any]:
    return {"action_type": "CREATE_FOLLOW_UP", "account_id": account_id, "status": "EXECUTED", "reason": reason}


def create_manager_escalation(account_id: str, reason: str) -> Dict[str, Any]:
    return {"action_type": "CREATE_MANAGER_ESCALATION", "account_id": account_id, "status": "PENDING_APPROVAL", "reason": reason}


def schedule_account_review(account_id: str, reason: str) -> Dict[str, Any]:
    return {"action_type": "SCHEDULE_ACCOUNT_REVIEW", "account_id": account_id, "status": "EXECUTED", "reason": reason}
