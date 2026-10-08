from backend.app.graph.nodes.context_nodes import investigation_node
from backend.app.graph.workflow import run_workflow


def test_run_workflow_for_territory_plan():
    result = run_workflow("Create a territory plan for Territory T001 and identify top accounts.")

    assert result["territory_id"] == "T001"
    assert result["validation_result"] == "PASS"
    assert "Territory plan for T001" in result["final_response"]
    assert len(result["prioritization_results"]) > 0


def test_territory_plan_has_priority_accounts():
    result = run_workflow("Plan for T001")
    plan = result["territory_plan"]

    assert plan["territory_id"] == "T001"
    assert len(plan["priority_accounts"]) > 0
    assert len(plan["recommended_actions"]) > 0


def test_investigation_node_handles_missing_account_data():
    state = {}

    result = investigation_node(state)

    assert result["investigation_result"]["account_id"] == ""
    assert result["investigation_result"]["findings"] == []
