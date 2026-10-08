from backend.app.graph.state import AgentState


def territory_planning_node(state: AgentState) -> AgentState:
    territory_id = state.get("territory_id")
    priority_accounts = [
        item["account_id"] for item in state.get("prioritization_results", [])[:3]
    ]
    state["territory_plan"] = {
        "territory_id": territory_id,
        "summary": f"Territory {territory_id} has stable growth and several high-value expansion opportunities.",
        "priority_accounts": priority_accounts,
        "recommended_actions": [
            "Review high-priority accounts",
            "Schedule account reviews",
            "Resolve at-risk service issues",
        ],
        "coverage_gaps": ["Follow-up with delayed opportunities"],
        "risks": ["Service issue concentration", "Potential churn in lower engagement accounts"],
        "sources": ["Territory rules", "Account KPIs"],
    }
    return state


def next_best_action_node(state: AgentState) -> AgentState:
    state["proposed_actions"] = [
        {
            "action_type": "SCHEDULE_ACCOUNT_REVIEW",
            "account_id": item["account_id"],
            "reason": "High priority account with growth potential and active opportunity pipeline.",
            "required_approval": False,
            "status": "PENDING",
        }
        for item in state.get("prioritization_results", [])[:3]
    ]
    return state