import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config.settings import settings
from backend.app.graph.workflow import run_workflow
from backend.app.models.schemas import WorkflowRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sales_agent_api")

app = FastAPI(title="Agentic Sales Territory Planning Assistant", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "environment": settings.app_env}


@app.get("/api/metrics")
def metrics() -> Dict[str, Any]:
    return {"workflow_count": 0, "api_latency_ms": 0, "status": "ready"}


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
async def approval(workflow_id: str) -> Dict[str, Any]:
    return {"workflow_id": workflow_id, "approval": "PENDING"}
