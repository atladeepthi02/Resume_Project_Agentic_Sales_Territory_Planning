import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.plans import router as plans_router
from backend.app.api.scoring import router as scoring_router
from backend.app.config.settings import settings
from backend.app.graph.workflow import run_workflow
from backend.app.models.schemas import ApprovalRequest, WorkflowRequest
from backend.app.services.observability import CorrelationIdMiddleware
from backend.app.services.sales_data_service import get_dashboard_metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sales_agent_api")

app = FastAPI(title="Agentic Sales Territory Planning Assistant", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)

# Plan-centric API described in the PRD (section 10).
app.include_router(plans_router)
app.include_router(scoring_router)


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "environment": settings.app_env}


@app.get("/health")
def liveness() -> Dict[str, Any]:
    """PRD section 10: liveness and readiness probe."""
    return {"status": "ok", "environment": settings.app_env, "version": app.version}


@app.get("/api/metrics")
def metrics() -> Dict[str, Any]:
    return get_dashboard_metrics()


@app.post("/api/chat")
async def chat(request: WorkflowRequest) -> Dict[str, Any]:
    try:
        result = run_workflow(request.user_query, request.session_id, request.user_id)
        return {"workflow": result["workflow_id"], "response": result["final_response"], "status": "ok"}
    except Exception as exc:  # pragma: no cover - defensive API guard
        logger.exception("chat request failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/agent/run")
async def agent_run(request: WorkflowRequest) -> Dict[str, Any]:
    result = run_workflow(request.user_query, request.session_id, request.user_id)
    return {"workflow": result["workflow_id"], "result": result}


@app.post("/api/territories/analyze")
async def analyze_territory(request: WorkflowRequest) -> Dict[str, Any]:
    return run_workflow(request.user_query, request.session_id, request.user_id)


@app.post("/api/territories/plan")
async def territory_plan(request: WorkflowRequest) -> Dict[str, Any]:
    return run_workflow(request.user_query, request.session_id, request.user_id)


@app.post("/api/accounts/prioritize")
async def prioritize_accounts(request: WorkflowRequest) -> Dict[str, Any]:
    return run_workflow(request.user_query, request.session_id, request.user_id)


@app.post("/api/accounts/analyze")
async def account_analyze(request: WorkflowRequest) -> Dict[str, Any]:
    return run_workflow(request.user_query, request.session_id, request.user_id)


@app.post("/api/documents/upload")
async def upload_documents() -> Dict[str, str]:
    return {"status": "uploaded", "message": "Document upload accepted"}


@app.post("/api/documents/ingest")
async def ingest_documents() -> Dict[str, str]:
    return {"status": "ingested", "message": "Document ingestion complete"}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    return {"session_id": session_id, "status": "active"}


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str) -> Dict[str, Any]:
    return {"workflow_id": workflow_id, "status": "completed"}


@app.post("/api/approval/{workflow_id}")
async def approval(workflow_id: str, request: ApprovalRequest | None = None) -> Dict[str, Any]:
    decision = request.decision if request is not None else "PENDING"
    logger.info("workflow %s approval decision: %s", workflow_id, decision)
    return {"workflow_id": workflow_id, "approval": decision}
