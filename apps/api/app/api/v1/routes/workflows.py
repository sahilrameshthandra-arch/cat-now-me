"""
Workflow endpoints for n8n integration and automation.
"""
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import structlog
import httpx
import uuid
from datetime import datetime

from app.core.security import get_current_active_user, TokenData
from app.core.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter()

# n8n configuration
N8N_BASE_URL = "http://localhost:5678"
N8N_API_KEY = ""  # Set via environment variable in production


class WorkflowCreate(BaseModel):
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(default=None, description="Workflow description")
    nodes: List[Dict[str, Any]] = Field(default_factory=list, description="Workflow nodes")
    connections: Dict[str, Any] = Field(default_factory=dict, description="Workflow connections")
    active: bool = Field(default=False, description="Whether workflow is active")


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    active: bool
    created_at: str
    updated_at: str
    n8n_id: Optional[str] = None


class WorkflowExecutionRequest(BaseModel):
    workflow_id: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    webhook_data: Optional[Dict[str, Any]] = None


class WorkflowExecutionResponse(BaseModel):
    execution_id: str
    workflow_id: str
    status: str
    started_at: str
    finished_at: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WebhookRegistration(BaseModel):
    workflow_id: str
    path: str
    method: str = Field(default="POST", pattern="^(GET|POST|PUT|DELETE)$")


async def get_n8n_client() -> httpx.AsyncClient:
    """Get configured n8n HTTP client."""
    headers = {}
    if N8N_API_KEY:
        headers["X-N8N-API-KEY"] = N8N_API_KEY
    
    return httpx.AsyncClient(
        base_url=N8N_BASE_URL,
        headers=headers,
        timeout=30.0,
    )


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(current_user: TokenData = Depends(get_current_active_user)):
    """List all workflows from n8n."""
    try:
        async with await get_n8n_client() as client:
            response = await client.get("/api/v1/workflows")
            response.raise_for_status()
            data = response.json()
            
            workflows = []
            for wf in data.get("data", []):
                workflows.append(WorkflowResponse(
                    id=wf.get("id", ""),
                    name=wf.get("name", ""),
                    description=wf.get("description"),
                    active=wf.get("active", False),
                    created_at=wf.get("createdAt", ""),
                    updated_at=wf.get("updatedAt", ""),
                    n8n_id=wf.get("id"),
                ))
            return workflows
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="n8n service unavailable")
    except Exception as e:
        logger.error("Failed to list workflows", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, current_user: TokenData = Depends(get_current_active_user)):
    """Get a specific workflow from n8n."""
    try:
        async with await get_n8n_client() as client:
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Workflow not found")
            response.raise_for_status()
            wf = response.json()
            
            return WorkflowResponse(
                id=wf.get("id", ""),
                name=wf.get("name", ""),
                description=wf.get("description"),
                active=wf.get("active", False),
                created_at=wf.get("createdAt", ""),
                updated_at=wf.get("updatedAt", ""),
                n8n_id=wf.get("id"),
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="n8n service unavailable")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get workflow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    workflow: WorkflowCreate,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Create a new workflow in n8n."""
    try:
        async with await get_n8n_client() as client:
            payload = {
                "name": workflow.name,
                "description": workflow.description,
                "nodes": workflow.nodes,
                "connections": workflow.connections,
                "active": workflow.active,
                "settings": {},
            }
            response = await client.post("/api/v1/workflows", json=payload)
            response.raise_for_status()
            wf = response.json()
            
            return WorkflowResponse(
                id=wf.get("id", ""),
                name=wf.get("name", ""),
                description=wf.get("description"),
                active=wf.get("active", False),
                created_at=wf.get("createdAt", ""),
                updated_at=wf.get("updatedAt", ""),
                n8n_id=wf.get("id"),
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="n8n service unavailable")
    except Exception as e:
        logger.error("Failed to create workflow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow: WorkflowCreate,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Update an existing workflow in n8n."""
    try:
        async with await get_n8n_client() as client:
            payload = {
                "name": workflow.name,
                "description": workflow.description,
                "nodes": workflow.nodes,
                "connections": workflow.connections,
                "active": workflow.active,
            }
            response = await client.put(f"/api/v1/workflows/{workflow_id}", json=payload)
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Workflow not found")
            response.raise_for_status()
            wf = response.json()
            
            return WorkflowResponse(
                id=wf.get("id", ""),
                name=wf.get("name", ""),
                description=wf.get("description"),
                active=wf.get("active", False),
                created_at=wf.get("createdAt", ""),
                updated_at=wf.get("updatedAt", ""),
                n8n_id=wf.get("id"),
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="n8n service unavailable")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update workflow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str, current_user: TokenData = Depends(get_current_active_user)):
    """Delete a workflow from n8n."""
    try:
        async with await get_n8n_client() as client:
            response = await client.delete(f"/api/v1/workflows/{workflow_id}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Workflow not found")
            response.raise_for_status()
            return {"message": "Workflow deleted", "id": workflow_id}
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="n8n service unavailable")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete workflow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/activate")
async def activate_workflow(workflow_id: str, current_user: TokenData = Depends(get_current_active_user)):
    """Activate a workflow in n8n."""
    try:
        async with await get_n8n_client() as client:
            response = await client.post(f"/api/v1/workflows/{workflow_id}/activate")
            response.raise_for_status()
            return {"message": "Workflow activated", "id": workflow_id}
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="n8n service unavailable")
    except Exception as e:
        logger.error("Failed to activate workflow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/deactivate")
async def deactivate_workflow(workflow_id: str, current_user: TokenData = Depends(get_current_active_user)):
    """Deactivate a workflow in n8n."""
    try:
        async with await get_n8n_client() as client:
            response = await client.post(f"/api/v1/workflows/{workflow_id}/deactivate")
            response.raise_for_status()
            return {"message": "Workflow deactivated", "id": workflow_id}
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="n8n service unavailable")
    except Exception as e:
        logger.error("Failed to deactivate workflow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Execute a workflow synchronously or asynchronously."""
    try:
        async with await get_n8n_client() as client:
            payload = {
                "workflowData": request.input_data,
            }
            if request.webhook_data:
                payload["webhookData"] = request.webhook_data
            
            response = await client.post(
                f"/api/v1/workflows/{request.workflow_id}/execute",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            
            return WorkflowExecutionResponse(
                execution_id=result.get("executionId", str(uuid.uuid4())),
                workflow_id=request.workflow_id,
                status=result.get("status", "unknown"),
                started_at=result.get("startedAt", datetime.utcnow().isoformat()),
                finished_at=result.get("finishedAt"),
                output=result.get("data"),
                error=result.get("error"),
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="n8n service unavailable")
    except Exception as e:
        logger.error("Failed to execute workflow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/{webhook_path}")
async def receive_webhook(
    webhook_path: str,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Receive webhook from n8n (no auth required - called by n8n)."""
    try:
        body = await request.json()
        logger.info("Received webhook", path=webhook_path, data=body)
        
        # TODO: Process webhook - trigger agents, update DB, etc.
        # This is where you'd connect n8n workflows to your AI agents
        
        return {"status": "received", "path": webhook_path}
    except Exception as e:
        logger.error("Webhook processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Get workflow execution status."""
    try:
        async with await get_n8n_client() as client:
            response = await client.get(f"/api/v1/executions/{execution_id}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Execution not found")
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="n8n service unavailable")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get execution", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_workflow_templates(current_user: TokenData = Depends(get_current_active_user)):
    """Get predefined workflow templates for common use cases."""
    templates = [
        {
            "id": "code-review-webhook",
            "name": "Code Review on PR",
            "description": "Trigger AI code review when a PR is opened",
            "category": "development",
            "webhook_path": "/webhook/code-review",
        },
        {
            "id": "content-generation",
            "name": "Content Generation Pipeline",
            "description": "Generate blog posts from topics using AI agents",
            "category": "content",
            "webhook_path": "/webhook/generate-content",
        },
        {
            "id": "data-processing",
            "name": "Data Processing Pipeline",
            "description": "Process uploaded files, extract text, and store in vector DB",
            "category": "data",
            "webhook_path": "/webhook/process-data",
        },
        {
            "id": "monitoring-alert",
            "name": "Monitoring Alert Handler",
            "description": "Process alerts and create incident tickets",
            "category": "operations",
            "webhook_path": "/webhook/alert",
        },
    ]
    return {"templates": templates}