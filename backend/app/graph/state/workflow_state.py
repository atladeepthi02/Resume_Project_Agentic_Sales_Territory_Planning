from typing import Any, Dict, List, Optional, TypedDict


class WorkflowState(TypedDict, total=False):
    session_id: Optional[str]
    user_id: Optional[str]
    workflow_id: Optional[str]
    user_query: str
    conversation_history: List[str]
    intent: Optional[str]
    entities: Dict[str, Any]
    tool_results: Dict[str, Any]
    confidence: float
    validation_result: str
    errors: List[str]
    retry_count: int
    final_response: str