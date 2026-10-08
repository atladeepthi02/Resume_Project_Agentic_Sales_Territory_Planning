from backend.app.services.sales_data_service import (
    get_account,
    get_account_contacts,
    get_account_history,
    get_opportunities,
    get_service_issues,
)


def get_account_tool(account_id: str):
    return {"account": get_account(account_id)}


def get_account_history_tool(account_id: str):
    return {"account_id": account_id, "history": get_account_history(account_id)}


def get_opportunities_tool(account_id: str):
    return {"account_id": account_id, "opportunities": get_opportunities(account_id)}


def get_service_issues_tool(account_id: str):
    return {"account_id": account_id, "issues": get_service_issues(account_id)}


def get_account_contacts_tool(account_id: str):
    return {"account_id": account_id, "contacts": get_account_contacts(account_id)}
