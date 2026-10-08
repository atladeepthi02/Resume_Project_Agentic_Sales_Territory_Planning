from backend.app.graph.state import AgentState
from backend.app.services.sales_data_service import (
    calculate_account_kpis,
    get_accounts_by_territory,
    get_territory,
    prioritize_accounts,
)


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
    state["kpi_results"] = [
        calculate_account_kpis(account["account_id"]) for account in accounts
    ]
    state["confidence"] = 0.9
    return state


def prioritization_node(state: AgentState) -> AgentState:
    territory_id = state.get("territory_id")
    if territory_id:
        state["prioritization_results"] = prioritize_accounts(territory_id)
    return state