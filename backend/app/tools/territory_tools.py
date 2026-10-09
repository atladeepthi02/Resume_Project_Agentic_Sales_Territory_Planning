from backend.app.services.sales_data_service import (
    get_accounts_by_territory,
    get_territories,
    get_territory,
    get_territory_rules,
)


def get_territory_tool(territory_id: str):
    return get_territory(territory_id)


def get_territories_tool():
    return {"territories": [
        {"territory_id": item["territory_id"], "name": item["name"], "owner": item["owner"]}
        for item in get_territories()
    ]}


def get_accounts_by_territory_tool(territory_id: str):
    return {"territory_id": territory_id, "accounts": get_accounts_by_territory(territory_id)}


def get_territory_rules_tool(territory_id: str):
    return {"territory_id": territory_id, "rules": get_territory_rules(territory_id)}
