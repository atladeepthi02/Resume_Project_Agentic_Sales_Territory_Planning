from backend.app.services.sales_data_service import calculate_account_kpis, prioritize_accounts


def calculate_account_kpis_tool(account_id: str):
    return calculate_account_kpis(account_id)


def rank_accounts_tool(territory_id: str):
    return {"territory_id": territory_id, "results": prioritize_accounts(territory_id)}
