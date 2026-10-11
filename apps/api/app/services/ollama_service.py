"""
Ollama service for local LLM inference.
Provides async client for chat, embeddings, and model management.
"""
import asyncio
import json
import time
from typing import AsyncGenerator, List, Optional, Dict, Any
from dataclasses import dataclass

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


@dataclass
class OllamaModel:
    name: str
    size: int
    modified_at: str
    digest: str
    details: Dict[str, Any]


@dataclass
class ChatMessage:
    role: str  # system, user, assistant, tool
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None


@dataclass
class ChatResponse:
    message: ChatMessage
    done: bool
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int


class OllamaService:
    """Async client for Ollama API."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def health_check(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error("Ollama health check failed", error=str(e))
            return False
    
    async def list_models(self) -> List[OllamaModel]:
        """List available models."""
        client = await self._get_client()
        response = await client.get("/api/tags")
        response.raise_for_status()
        data = response.json()
        return [
            OllamaModel(
                name=m["name"],
                size=m["size"],
                modified_at=m["modified_at"],
                digest=m["digest"],
                details=m.get("details", {}),
            )
            for m in data.get("models", [])
        ]
    
    async def pull_model(self, name: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Pull a model from Ollama registry. Yields progress updates."""
        client = await self._get_client()
        async with client.stream(
            "POST",
            "/api/pull",
            json={"name": name, "stream": True},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    yield json.loads(line)
    
    async def delete_model(self, name: str) -> bool:
        """Delete a model."""
        client = await self._get_client()
        response = await client.delete("/api/delete", json={"name": name})
        return response.status_code == 200
    
    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        num_predict: int = -1,
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
        format: Optional[str] = None,  # json, yaml, etc.
    ) -> ChatResponse | AsyncGenerator[ChatResponse, None]:
        """
        Send chat completion request.
        
        If stream=True, returns async generator of ChatResponse chunks.
        If stream=False, returns single ChatResponse.
        """
        model = model or settings.OLLAMA_DEFAULT_MODEL
        
        payload = {
            "model": model,
            "messages": [
                {"role": m.role, "content": m.content}
                for m in messages
            ],
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": num_predict,
            },
            "stream": stream,
        }
        
        if tools:
            payload["tools"] = tools
        if format:
            payload["format"] = format
        
        client = await self._get_client()
        
        if stream:
            return self._stream_chat(client, payload)
        else:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            return self._parse_chat_response(response.json())
    
    async def _stream_chat(
        self,
        client: httpx.AsyncClient,
        payload: Dict
    ) -> AsyncGenerator[ChatResponse, None]:
        """Stream chat responses."""
        async with client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    yield self._parse_chat_response(data)
    
    def _parse_chat_response(self, data: Dict) -> ChatResponse:
        """Parse Ollama chat response."""
        msg = data.get("message", {})
        return ChatResponse(
            message=ChatMessage(
                role=msg.get("role", "assistant"),
                content=msg.get("content", ""),
                tool_calls=msg.get("tool_calls"),
                tool_call_id=msg.get("tool_call_id"),
            ),
            done=data.get("done", False),
            total_duration=data.get("total_duration", 0),
            load_duration=data.get("load_duration", 0),
            prompt_eval_count=data.get("prompt_eval_count", 0),
            prompt_eval_duration=data.get("prompt_eval_duration", 0),
            eval_count=data.get("eval_count", 0),
            eval_duration=data.get("eval_duration", 0),
        )
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
        format: Optional[str] = None,
    ) -> str | AsyncGenerator[str, None]:
        """Generate completion from a prompt (legacy /api/generate endpoint)."""
        model = model or settings.OLLAMA_DEFAULT_MODEL
        
        payload = {
            "model": model,
            "prompt": prompt,
            "options": {"temperature": temperature},
            "stream": stream,
        }
        if format:
            payload["format"] = format
        
        client = await self._get_client()
        
        if stream:
            return self._stream_generate(client, payload)
        else:
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
    
    async def _stream_generate(
        self,
        client: httpx.AsyncClient,
        payload: Dict
    ) -> AsyncGenerator[str, None]:
        """Stream generate responses."""
        async with client.stream("POST", "/api/generate", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done"):
                        break
    
    async def embeddings(
        self,
        input: str | List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """Generate embeddings for text."""
        model = model or "nomic-embed-text"  # Default embedding model
        
        if isinstance(input, str):
            input = [input]
        
        client = await self._get_client()
        response = await client.post(
            "/api/embed",
            json={"model": model, "input": input}
        )
        response.raise_for_status()
        return response.json().get("embeddings", [])
    
    async def get_model_info(self, name: str) -> Dict[str, Any]:
        """Get detailed model information."""
        client = await self._get_client()
        response = await client.post("/api/show", json={"name": name})
        response.raise_for_status()
        return response.json()


# Singleton instance
ollama_service = OllamaService()


async def get_ollama_service() -> OllamaService:
    """Dependency for FastAPI to get Ollama service."""
    return ollama_service