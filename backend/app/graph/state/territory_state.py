from typing import Any, Dict, List, Optional, TypedDict


class TerritoryState(TypedDict, total=False):
    territory_id: Optional[str]
    territory_data: Dict[str, Any]
    kpi_results: List[Dict[str, Any]]
    prioritization_results: List[Dict[str, Any]]
    retrieved_documents: List[Dict[str, Any]]
    selected_playbooks: List[Dict[str, Any]]
    investigation_result: Dict[str, Any]
    territory_plan: Dict[str, Any]
    proposed_actions: List[Dict[str, Any]]
    human_approval: Dict[str, Any]