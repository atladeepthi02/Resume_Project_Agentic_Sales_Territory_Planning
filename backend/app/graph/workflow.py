from __future__ import annotations

import uuid
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from backend.app.graph.state import AgentState
from backend.app.graph.nodes.context_nodes import investigation_node, rag_node
from backend.app.graph.nodes.data_nodes import kpi_node, prioritization_node, territory_data_node
from backend.app.graph.nodes.planning_nodes import next_best_action_node, territory_planning_node
from backend.app.graph.nodes.response_nodes import response_node, validation_node
from backend.app.graph.nodes.triage_node import triage_node


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
