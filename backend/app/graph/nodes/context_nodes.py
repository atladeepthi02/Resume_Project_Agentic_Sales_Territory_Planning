from backend.app.graph.state import AgentState
from backend.app.services.sales_data_service import get_retrieved_documents, get_territory_rules


def rag_node(state: AgentState) -> AgentState:
    query = state.get("user_query", "")
    territory_id = state.get("territory_id")
    docs = get_retrieved_documents(query)
    if territory_id:
        docs.append({
            "title": "Territory policy",
            "content": " ".join(get_territory_rules(territory_id)),
            "source": "territory_rules",
            "category": "policy",
        })
    state["retrieved_documents"] = docs
    return state


def investigation_node(state: AgentState) -> AgentState:
    account_data = state.get("account_data", {})
    accounts = account_data.get("accounts", [])
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