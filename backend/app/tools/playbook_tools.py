from backend.app.services.sales_data_service import get_retrieved_documents


def get_sales_playbook(query: str):
    return {"playbooks": get_retrieved_documents(query)}
