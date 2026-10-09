from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


IntentType = Literal[
    "TERRITORY_PLANNING",
    "ACCOUNT_PRIORITIZATION",
    "ACCOUNT_ANALYSIS",
    "OPPORTUNITY_ANALYSIS",
    "RISK_ANALYSIS",
    "NEXT_BEST_ACTION",
    "SALES_KPI_ANALYSIS",
    "PLAYBOOK_RECOMMENDATION",
    "TERRITORY_COMPARISON",
    "ACCOUNT_FOLLOW_UP",
    "CRM_ACTION",
    "GENERAL_SALES_QUERY",
]


class TriageOutput(BaseModel):
    intent: IntentType = "TERRITORY_PLANNING"
    category: str = "SALES_PLANNING"
    territory_id: Optional[str] = None
    account_ids: List[str] = Field(default_factory=list)
    product: Optional[str] = None
    time_period: str = "CURRENT_QUARTER"
    priority: str = "MEDIUM"
    missing_information: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    recommended_route: str = "TERRITORY_PLANNING_WORKFLOW"


class KPIOutput(BaseModel):
    account_id: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    trend: str = "STABLE"
    health: str = "HEALTHY"
    confidence: float = 0.0


class PrioritizationOutput(BaseModel):
    account_id: str
    priority_score: float = 0.0
    priority_level: str = "MEDIUM"
    drivers: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)


class InvestigationOutput(BaseModel):
    account_id: str
    findings: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    policy_references: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    requires_human_review: bool = False


class TerritoryPlanOutput(BaseModel):
    territory_id: str
    summary: str
    priority_accounts: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    coverage_gaps: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)


class ActionOutput(BaseModel):
    action_type: str
    account_id: str
    reason: str
    required_approval: bool = False
    status: Literal["PENDING", "APPROVED", "EXECUTED", "REJECTED", "FAILED"] = "PENDING"


class WorkflowRequest(BaseModel):
    user_query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ApprovalRequest(BaseModel):
    decision: Literal["APPROVED", "REJECTED", "PENDING"] = "PENDING"


class AgentState(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    workflow_id: Optional[str] = None
    user_query: str = ""
    conversation_history: List[str] = Field(default_factory=list)
    intent: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    territory_id: Optional[str] = None
    account_ids: List[str] = Field(default_factory=list)
    territory_data: Dict[str, Any] = Field(default_factory=dict)
    account_data: Dict[str, Any] = Field(default_factory=dict)
    opportunity_data: Dict[str, Any] = Field(default_factory=dict)
    activity_data: Dict[str, Any] = Field(default_factory=dict)
    service_data: Dict[str, Any] = Field(default_factory=dict)
    kpi_results: List[KPIOutput] = Field(default_factory=list)
    prioritization_results: List[PrioritizationOutput] = Field(default_factory=list)
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)
    selected_playbooks: List[Dict[str, Any]] = Field(default_factory=list)
    investigation_result: Optional[InvestigationOutput] = None
    territory_plan: Optional[TerritoryPlanOutput] = None
    proposed_actions: List[ActionOutput] = Field(default_factory=list)
    tool_results: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    validation_result: str = "PASS"
    human_approval: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    retry_count: int = 0
    final_response: str = ""
