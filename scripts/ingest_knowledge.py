from backend.app.rag.vector_store import SalesKnowledgeRAG
from backend.app.services.sales_data_service import get_retrieved_documents


def main():
    vector_store = SalesKnowledgeRAG()
    docs = [
        {
            "document_id": "playbook-1",
            "title": "Product Expansion Playbook",
            "content": "Focus on accounts with strong revenue growth and adoption gaps. Confirm decision maker, establish executive sponsor, and propose staged expansion steps.",
            "source": "sales_playbooks.pdf",
            "category": "sales_playbook",
            "territory": "T001",
        },
        {
            "document_id": "policy-1",
            "title": "At Risk Account Recovery",
            "content": "If revenue is declining and service issues are open, schedule a recovery review and align support, renewal options, and executive outreach.",
            "source": "account_recovery_policy.pdf",
            "category": "account_management",
            "territory": "T002",
        },
    ]
    vector_store.ingest_documents(docs)
    print(f"Ingested {len(docs)} documents into local sales knowledge store.")


if __name__ == "__main__":
    main()
