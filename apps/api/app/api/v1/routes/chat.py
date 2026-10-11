"""
Chat endpoints for direct LLM interaction (without agents).
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, AsyncGenerator
from fastapi.responses import StreamingResponse
import json
import structlog

from app.services.ollama_service import ollama_service, ChatMessage
from app.core.security import get_current_active_user, TokenData
from app.core.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter()


class ChatMessageRequest(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant|tool)$")
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ChatRequest(BaseModel):
    messages: List[ChatMessageRequest] = Field(..., min_length=1)
    model: Optional[str] = Field(default=None, description="Ollama model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=1, le=100)
    num_predict: int = Field(default=-1, ge=-1)
    stream: bool = Field(default=False)
    format: Optional[str] = Field(default=None, pattern="^(json|yaml)?$")


class ChatResponse(BaseModel):
    message: ChatMessageRequest
    done: bool
    total_duration: int
    eval_count: int
    eval_duration: int


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stream: bool = Field(default=False)
    format: Optional[str] = Field(default=None, pattern="^(json|yaml)?$")


class EmbeddingsRequest(BaseModel):
    input: List[str] = Field(..., min_length=1)
    model: Optional[str] = None


class EmbeddingsResponse(BaseModel):
    embeddings: List[List[float]]


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Non-streaming chat completion."""
    try:
        messages = [
            ChatMessage(
                role=m.role,
                content=m.content,
                tool_calls=m.tool_calls,
                tool_call_id=m.tool_call_id,
            )
            for m in request.messages
        ]
        
        response = await ollama_service.chat(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            num_predict=request.num_predict,
            stream=False,
            format=request.format,
        )
        
        return ChatResponse(
            message=ChatMessageRequest(
                role=response.message.role,
                content=response.message.content,
                tool_calls=response.message.tool_calls,
                tool_call_id=response.message.tool_call_id,
            ),
            done=response.done,
            total_duration=response.total_duration,
            eval_count=response.eval_count,
            eval_duration=response.eval_duration,
        )
    except Exception as e:
        logger.error("Chat failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Streaming chat completion (Server-Sent Events)."""
    try:
        messages = [
            ChatMessage(
                role=m.role,
                content=m.content,
                tool_calls=m.tool_calls,
                tool_call_id=m.tool_call_id,
            )
            for m in request.messages
        ]
        
        async def generate():
            async for chunk in await ollama_service.chat(
                messages=messages,
                model=request.model,
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                num_predict=request.num_predict,
                stream=True,
                format=request.format,
            ):
                yield f"data: {json.dumps({
                    'message': {
                        'role': chunk.message.role,
                        'content': chunk.message.content,
                        'tool_calls': chunk.message.tool_calls,
                        'tool_call_id': chunk.message.tool_call_id,
                    },
                    'done': chunk.done,
                })}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        logger.error("Streaming chat failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate(
    request: GenerateRequest,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Simple text generation (legacy /api/generate compatible)."""
    try:
        if request.stream:
            async def generate_stream():
                async for chunk in await ollama_service.generate(
                    prompt=request.prompt,
                    model=request.model,
                    temperature=request.temperature,
                    stream=True,
                    format=request.format,
                ):
                    yield f"data: {json.dumps({'response': chunk, 'done': False})}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
            )
        else:
            response = await ollama_service.generate(
                prompt=request.prompt,
                model=request.model,
                temperature=request.temperature,
                stream=False,
                format=request.format,
            )
            return {"response": response, "done": True}
    except Exception as e:
        logger.error("Generate failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings", response_model=EmbeddingsResponse)
async def embeddings(
    request: EmbeddingsRequest,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Generate embeddings for text inputs."""
    try:
        embeddings = await ollama_service.embeddings(
            input=request.input,
            model=request.model,
        )
        return EmbeddingsResponse(embeddings=embeddings)
    except Exception as e:
        logger.error("Embeddings failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))