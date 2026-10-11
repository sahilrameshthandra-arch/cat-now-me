"""
Agent endpoints for running AI agents.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import structlog

from app.agents.langgraph_agents import (
    get_code_agent,
    get_research_agent,
    get_writing_agent,
    get_general_agent,
    run_agent,
    run_code_review_workflow,
    AgentRunResult,
)
from app.core.security import get_current_active_user, TokenData
from app.core.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter()


# Request/Response Models
class AgentRunRequest(BaseModel):
    prompt: str = Field(..., description="User input for the agent")
    agent_type: str = Field(default="general", description="Type of agent: code, research, writing, general")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    system_prompt: Optional[str] = Field(default=None, description="Custom system prompt")
    max_iterations: Optional[int] = Field(default=10, ge=1, le=20)


class AgentRunResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    iterations: int
    agent_type: str


class CodeReviewRequest(BaseModel):
    code: str = Field(..., description="Code to review")
    language: str = Field(default="python", description="Programming language")
    focus_areas: Optional[List[str]] = Field(default=None, description="Focus areas for review")


class CodeReviewResponse(BaseModel):
    analysis: Optional[str] = None
    security: Optional[str] = None
    report: Optional[str] = None
    error: Optional[str] = None


class AgentInfo(BaseModel):
    id: str
    name: str
    description: str
    model: str
    tools: List[str]


# Available agents
AGENTS = {
    "code": AgentInfo(
        id="code",
        name="Code Agent",
        description="Expert software engineer for writing, reviewing, and debugging code",
        model="codellama:13b-instruct",
        tools=["vector_search", "code_execution", "file_operation"],
    ),
    "research": AgentInfo(
        id="research",
        name="Research Agent",
        description="Research analyst for finding, synthesizing, and analyzing information",
        model="llama3.1:8b",
        tools=["vector_search", "web_search"],
    ),
    "writing": AgentInfo(
        id="writing",
        name="Writing Agent",
        description="Technical writer for creating clear, engaging content",
        model="llama3.1:8b",
        tools=["vector_search", "file_operation"],
    ),
    "general": AgentInfo(
        id="general",
        name="General Agent",
        description="General-purpose assistant with all available tools",
        model=settings.OLLAMA_DEFAULT_MODEL,
        tools=list(settings.OLLAMA_MODELS),
    ),
}


def get_agent(agent_type: str):
    """Get agent by type."""
    agents_map = {
        "code": get_code_agent,
        "research": get_research_agent,
        "writing": get_writing_agent,
        "general": get_general_agent,
    }
    if agent_type not in agents_map:
        raise HTTPException(status_code=404, detail=f"Agent type '{agent_type}' not found")
    return agents_map[agent_type]()


@router.get("", response_model=List[AgentInfo])
async def list_agents(current_user: TokenData = Depends(get_current_active_user)):
    """List available agents."""
    return list(AGENTS.values())


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent_info(agent_id: str, current_user: TokenData = Depends(get_current_active_user)):
    """Get agent details."""
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AGENTS[agent_id]


@router.post("/run", response_model=AgentRunResponse)
async def run_agent_endpoint(
    request: AgentRunRequest,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Run an agent with the given prompt."""
    try:
        agent = get_agent(request.agent_type)
        
        result = await run_agent(
            agent=agent,
            user_input=request.prompt,
            context=request.context,
            system_prompt=request.system_prompt,
        )
        
        # Extract final response
        response_text = None
        if result.messages:
            for msg in reversed(result.messages):
                if hasattr(msg, 'content') and msg.content and not getattr(msg, 'tool_calls', None):
                    response_text = msg.content
                    break
        
        return AgentRunResponse(
            success=result.success,
            response=response_text,
            error=result.error,
            iterations=result.iterations,
            agent_type=request.agent_type,
        )
    except Exception as e:
        logger.error("Agent run failed", error=str(e), agent_type=request.agent_type)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code-review", response_model=CodeReviewResponse)
async def code_review(
    request: CodeReviewRequest,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Run multi-agent code review workflow."""
    try:
        result = await run_code_review_workflow(
            code=request.code,
            language=request.language,
            focus_areas=request.focus_areas,
        )
        return CodeReviewResponse(**result)
    except Exception as e:
        logger.error("Code review failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code-review/async")
async def code_review_async(
    request: CodeReviewRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Start async code review (returns immediately with task ID)."""
    # TODO: Implement with Celery or background task queue
    task_id = f"review_{current_user.user_id}_{hash(request.code)}"
    background_tasks.add_task(run_code_review_workflow, request.code, request.language, request.focus_areas)
    return {"task_id": task_id, "status": "started"}


@router.get("/models")
async def list_ollama_models(current_user: TokenData = Depends(get_current_active_user)):
    """List available Ollama models."""
    try:
        models = await ollama_service.list_models()
        return {
            "models": [
                {
                    "name": m.name,
                    "size": m.size,
                    "modified_at": m.modified_at,
                    "details": m.details,
                }
                for m in models
            ]
        }
    except Exception as e:
        logger.error("Failed to list models", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to connect to Ollama")