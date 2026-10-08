from typing import Any, Dict, List, TypedDict


class AccountState(TypedDict, total=False):
    account_ids: List[str]
    account_data: Dict[str, Any]
    opportunity_data: Dict[str, Any]
    activity_data: Dict[str, Any]
    service_data: Dict[str, Any]