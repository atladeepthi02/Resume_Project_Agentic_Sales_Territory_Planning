from backend.app.graph.state import AgentState


def validation_node(state: AgentState) -> AgentState:
    state["validation_result"] = "PASS" if state.get("territory_id") else "RETRY"
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