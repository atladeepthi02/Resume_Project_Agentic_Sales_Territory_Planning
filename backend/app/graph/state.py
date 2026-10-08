from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    session_id: Optional[str]
    user_id: Optional[str]
    workflow_id: Optional[str]
    user_query: str
    conversation_history: List[str]
    intent: Optional[str]
    entities: Dict[str, Any]
    territory_id: Optional[str]
    account_ids: List[str]
    territory_data: Dict[str, Any]
    account_data: Dict[str, Any]
    opportunity_data: Dict[str, Any]
    activity_data: Dict[str, Any]
    service_data: Dict[str, Any]
    kpi_results: List[Dict[str, Any]]
    prioritization_results: List[Dict[str, Any]]
    retrieved_documents: List[Dict[str, Any]]
    selected_playbooks: List[Dict[str, Any]]
    investigation_result: Dict[str, Any]
    territory_plan: Dict[str, Any]
    proposed_actions: List[Dict[str, Any]]
    tool_results: Dict[str, Any]
    confidence: float
    validation_result: str
    human_approval: Dict[str, Any]
    errors: List[str]
    retry_count: int
    final_response: str
