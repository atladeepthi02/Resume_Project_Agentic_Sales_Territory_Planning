from backend.app.models.schemas import TriageOutput


def triage_request(user_query: str) -> TriageOutput:
    territory_id = "T001" if "T001" in user_query else "T002" if "T002" in user_query else "T003" if "T003" in user_query else None
    return TriageOutput(
        intent="TERRITORY_PLANNING",
        category="SALES_PLANNING",
        territory_id=territory_id,
        account_ids=[],
        priority="HIGH",
        missing_information=[],
        confidence=0.92,
        recommended_route="TERRITORY_PLANNING_WORKFLOW",
    )
