from __future__ import annotations

import uuid
from typing import Any, Dict, List

from langgraph.graph import END, StateGraph

from backend.app.graph.state import AgentState
from backend.app.services.sales_data_service import (
    calculate_account_kpis,
    get_account,
    get_accounts_by_territory,
    get_retrieved_documents,
    get_territory,
    get_territory_rules,
    prioritize_accounts,
)
from backend.app.rag.vector_store import SalesKnowledgeRAG

rag_store = SalesKnowledgeRAG()


def triage_node(state: AgentState) -> AgentState:
    query = state.get("user_query", "")
    territory_id = None
    if "T001" in query:
        territory_id = "T001"
    elif "T002" in query:
        territory_id = "T002"
    elif "T003" in query:
        territory_id = "T003"
    elif "north" in query.lower():
        territory_id = "T001"

    state["intent"] = "TERRITORY_PLANNING" if "plan" in query.lower() else "ACCOUNT_PRIORITIZATION"
    state["territory_id"] = territory_id
    state["entities"] = {"territory_id": territory_id}
    return state


def territory_data_node(state: AgentState) -> AgentState:
    territory_id = state.get("territory_id")
    if territory_id:
        state["territory_data"] = get_territory(territory_id)
        state["account_data"] = {"accounts": get_accounts_by_territory(territory_id)}
    else:
        state["territory_data"] = {}
        state["account_data"] = {"accounts": []}
    return state


def kpi_node(state: AgentState) -> AgentState:
    account_data = state.get("account_data", {})
    accounts = account_data.get("accounts", [])
    kpis = []
    for account in accounts:
        kpis.append(calculate_account_kpis(account["account_id"]))
    state["kpi_results"] = kpis
    state["confidence"] = 0.9
    return state


def prioritization_node(state: AgentState) -> AgentState:
    territory_id = state.get("territory_id")
    if territory_id:
        state["prioritization_results"] = prioritize_accounts(territory_id)
    return state


def rag_node(state: AgentState) -> AgentState:
    query = state.get("user_query", "")
    territory_id = state.get("territory_id")
    docs = get_retrieved_documents(query)
    if territory_id:
        docs.extend([
            {"title": "Territory policy", "content": " ".join(get_territory_rules(territory_id)), "source": "territory_rules", "category": "policy"}
        ])
    state["retrieved_documents"] = docs
    return state


def investigation_node(state: AgentState) -> AgentState:
    accounts = state["account_data"].get("accounts", [])
    findings = []
    risks = []
    opportunities = []
    for account in accounts:
        if account.get("growth", 0) > 0.12:
            opportunities.append(f"Expansion opportunity for {account['name']}")
        if account.get("risk_level", 0) > 0.5:
            risks.append(f"At-risk account: {account['name']}")
        if account.get("open_issues", 0) > 0:
            findings.append(f"Open service issues for {account['name']}")
    state["investigation_result"] = {
        "account_id": accounts[0]["account_id"] if accounts else "",
        "findings": findings,
        "risks": risks,
        "opportunities": opportunities,
        "evidence": ["Account health summary", "Territory review"],
        "policy_references": ["High risk accounts must have a documented action plan."],
        "confidence": 0.88,
        "requires_human_review": False,
    }
    return state


def territory_planning_node(state: AgentState) -> AgentState:
    territory_id = state.get("territory_id")
    priority_accounts = [item["account_id"] for item in state.get("prioritization_results", [])[:3]]
    state["territory_plan"] = {
        "territory_id": territory_id,
        "summary": f"Territory {territory_id} has stable growth and several high-value expansion opportunities.",
        "priority_accounts": priority_accounts,
        "recommended_actions": ["Review high-priority accounts", "Schedule account reviews", "Resolve at-risk service issues"],
        "coverage_gaps": ["Follow-up with delayed opportunities"],
        "risks": ["Service issue concentration", "Potential churn in lower engagement accounts"],
        "sources": ["Territory rules", "Account KPIs"],
    }
    return state


def next_best_action_node(state: AgentState) -> AgentState:
    proposed = []
    for item in state.get("prioritization_results", [])[:3]:
        proposed.append({
            "action_type": "SCHEDULE_ACCOUNT_REVIEW",
            "account_id": item["account_id"],
            "reason": "High priority account with growth potential and active opportunity pipeline.",
            "required_approval": False,
            "status": "PENDING",
        })
    state["proposed_actions"] = proposed
    return state


def validation_node(state: AgentState) -> AgentState:
    if state.get("territory_id"):
        state["validation_result"] = "PASS"
    else:
        state["validation_result"] = "RETRY"
    return state


def response_node(state: AgentState) -> AgentState:
    territory_id = state.get("territory_id") or "Unknown"
    plan = state.get("territory_plan", {})
    state["final_response"] = (
        f"Territory plan for {territory_id} is ready. "
        f"Priority accounts: {', '.join(plan.get('priority_accounts', [])) or 'none'}. "
        f"Recommended actions: {', '.join(plan.get('recommended_actions', []))}."
    )
    return state


def build_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("triage_node", triage_node)
    workflow.add_node("load_territory_data", territory_data_node)
    workflow.add_node("compute_kpis", kpi_node)
    workflow.add_node("rank_accounts", prioritization_node)
    workflow.add_node("retrieve_policy_context", rag_node)
    workflow.add_node("investigate_accounts", investigation_node)
    workflow.add_node("build_territory_plan", territory_planning_node)
    workflow.add_node("draft_next_best_actions", next_best_action_node)
    workflow.add_node("validate_recommendations", validation_node)
    workflow.add_node("finalize_response", response_node)

    workflow.set_entry_point("triage_node")
    workflow.add_edge("triage_node", "load_territory_data")
    workflow.add_edge("load_territory_data", "compute_kpis")
    workflow.add_edge("compute_kpis", "rank_accounts")
    workflow.add_edge("rank_accounts", "retrieve_policy_context")
    workflow.add_edge("retrieve_policy_context", "investigate_accounts")
    workflow.add_edge("investigate_accounts", "build_territory_plan")
    workflow.add_edge("build_territory_plan", "draft_next_best_actions")
    workflow.add_edge("draft_next_best_actions", "validate_recommendations")
    workflow.add_edge("validate_recommendations", "finalize_response")
    workflow.add_edge("finalize_response", END)
    return workflow.compile()


workflow_app = build_workflow()


def run_workflow(user_query: str, session_id: str | None = None, user_id: str | None = None) -> Dict[str, Any]:
    initial_state: AgentState = {
        "session_id": session_id,
        "user_id": user_id,
        "workflow_id": str(uuid.uuid4()),
        "user_query": user_query,
        "conversation_history": [],
        "intent": None,
        "entities": {},
        "territory_id": None,
        "account_ids": [],
        "account_data": {"accounts": []},
        "tool_results": {},
        "errors": [],
        "retry_count": 0,
        "confidence": 0.0,
        "validation_result": "PASS",
    }
    result = workflow_app.invoke(initial_state)
    return result
