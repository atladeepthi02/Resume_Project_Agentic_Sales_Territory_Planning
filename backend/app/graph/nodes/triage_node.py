from backend.app.graph.state import AgentState


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