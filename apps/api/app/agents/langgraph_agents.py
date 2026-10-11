"""
LangGraph agents for AI workflows.
Defines reusable agent patterns: ReAct, Code Agent, Research Agent, etc.
"""
from typing import Dict, Any, List, Optional, Callable, TypedDict, Annotated
from dataclasses import dataclass, field
from datetime import datetime
import json
import structlog

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_ollama import ChatOllama

from app.core.config import settings
from app.services.ollama_service import ollama_service, ChatMessage
from app.services.vector_store import vector_store_service, SearchResult

logger = structlog.get_logger(__name__)


# ============================================
# Base State
# ============================================

class AgentState(TypedDict):
    """Base state for all agents."""
    messages: Annotated[List[BaseMessage], "The conversation messages"]
    context: Dict[str, Any]  # Additional context data
    current_step: str
    iterations: int
    max_iterations: int
    error: Optional[str]
    result: Optional[Dict[str, Any]]


# ============================================
# Tool Definitions
# ============================================

class VectorSearchTool(BaseTool):
    """Tool for searching the vector store."""
    name: str = "vector_search"
    description: str = "Search the knowledge base for relevant documents. Use this when you need to find information from uploaded documents."
    
    def _run(self, query: str, n_results: int = 5) -> str:
        """Synchronous version (not used in async graph)."""
        raise NotImplementedError("Use async version")
    
    async def _arun(self, query: str, n_results: int = 5) -> str:
        results = await vector_store_service.search(query, n_results=n_results)
        if not results:
            return "No relevant documents found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"[{i}] Score: {result.score:.3f}\n"
                f"Content: {result.document.content[:500]}...\n"
                f"Metadata: {result.document.metadata}"
            )
        return "\n\n".join(formatted)


class WebSearchTool(BaseTool):
    """Tool for web search (placeholder - integrate with actual search API)."""
    name: str = "web_search"
    description: str = "Search the web for current information. Use when you need up-to-date data not in the knowledge base."
    
    def _run(self, query: str) -> str:
        raise NotImplementedError("Use async version")
    
    async def _arun(self, query: str) -> str:
        # TODO: Integrate with actual search API (SerpAPI, Brave Search, etc.)
        return f"Web search not yet implemented. Query: {query}"


class CodeExecutionTool(BaseTool):
    """Tool for executing Python code (sandboxed)."""
    name: str = "code_execution"
    description: str = "Execute Python code in a sandboxed environment. Use for calculations, data processing, or testing code snippets."
    
    def _run(self, code: str) -> str:
        raise NotImplementedError("Use async version")
    
    async def _arun(self, code: str) -> str:
        # TODO: Implement sandboxed code execution (use Docker or restricted Python)
        return f"Code execution not yet implemented. Code: {code}"


class FileOperationTool(BaseTool):
    """Tool for file operations."""
    name: str = "file_operation"
    description: str = "Read, write, or list files in the workspace. Use for creating reports, saving data, or reading project files."
    
    def _run(self, operation: str, path: str, content: str = "") -> str:
        raise NotImplementedError("Use async version")
    
    async def _arun(self, operation: str, path: str, content: str = "") -> str:
        # TODO: Implement safe file operations
        return f"File operation not yet implemented: {operation} {path}"


# Available tools registry
AVAILABLE_TOOLS = {
    "vector_search": VectorSearchTool(),
    "web_search": WebSearchTool(),
    "code_execution": CodeExecutionTool(),
    "file_operation": FileOperationTool(),
}


# ============================================
# Agent Nodes
# ============================================

async def call_model(state: AgentState, model_name: str = None) -> Dict[str, Any]:
    """Call the LLM with current messages and tools."""
    model_name = model_name or settings.OLLAMA_DEFAULT_MODEL
    
    # Convert LangChain messages to Ollama format
    ollama_messages = []
    for msg in state["messages"]:
        if isinstance(msg, SystemMessage):
            ollama_messages.append(ChatMessage(role="system", content=msg.content))
        elif isinstance(msg, HumanMessage):
            ollama_messages.append(ChatMessage(role="user", content=msg.content))
        elif isinstance(msg, AIMessage):
            ollama_messages.append(ChatMessage(role="assistant", content=msg.content))
        elif isinstance(msg, ToolMessage):
            ollama_messages.append(ChatMessage(role="tool", content=msg.content))
    
    # Get available tools as OpenAI function format
    tools = []
    for tool in AVAILABLE_TOOLS.values():
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"],
                } if tool.name == "vector_search" else {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"],
                } if tool.name == "web_search" else {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python code to execute"}
                    },
                    "required": ["code"],
                } if tool.name == "code_execution" else {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["read", "write", "list"]},
                        "path": {"type": "string"},
                        "content": {"type": "string", "default": ""}
                    },
                    "required": ["operation", "path"],
                }
            }
        })
    
    response = await ollama_service.chat(
        messages=ollama_messages,
        model=model_name,
        temperature=0.1,
        tools=tools if tools else None,
    )
    
    # Convert back to LangChain message
    if response.message.tool_calls:
        tool_calls = []
        for tc in response.message.tool_calls:
            tool_calls.append({
                "id": tc.get("id", f"call_{datetime.now().timestamp()}"),
                "name": tc["function"]["name"],
                "arguments": tc["function"]["arguments"],
            })
        ai_message = AIMessage(content="", tool_calls=tool_calls)
    else:
        ai_message = AIMessage(content=response.message.content)
    
    return {
        "messages": [ai_message],
        "current_step": "model_called",
    }


async def execute_tools(state: AgentState) -> Dict[str, Any]:
    """Execute tool calls from the last AI message."""
    last_message = state["messages"][-1]
    
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return {"current_step": "no_tools", "error": "No tool calls found"}
    
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        if tool_name not in AVAILABLE_TOOLS:
            tool_messages.append(ToolMessage(
                content=f"Unknown tool: {tool_name}",
                tool_call_id=tool_call["id"],
            ))
            continue
        
        try:
            tool = AVAILABLE_TOOLS[tool_name]
            # Parse arguments if they're a JSON string
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)
            
            result = await tool._arun(**tool_args)
            tool_messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            ))
        except Exception as e:
            logger.error("Tool execution failed", tool=tool_name, error=str(e))
            tool_messages.append(ToolMessage(
                content=f"Error executing {tool_name}: {str(e)}",
                tool_call_id=tool_call["id"],
            ))
    
    return {
        "messages": tool_messages,
        "current_step": "tools_executed",
    }


def should_continue(state: AgentState) -> str:
    """Decide whether to continue or end."""
    if state.get("error"):
        return "end"
    
    last_message = state["messages"][-1]
    
    # If last message is AI with tool calls, execute tools
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "execute_tools"
    
    # If we've hit max iterations, end
    if state["iterations"] >= state["max_iterations"]:
        return "end"
    
    # Otherwise continue with model
    return "call_model"


# ============================================
# Agent Builders
# ============================================

def create_react_agent(
    system_prompt: str,
    tools: Optional[List[str]] = None,
    max_iterations: int = 10,
    model_name: str = None,
) -> StateGraph:
    """
    Create a ReAct (Reasoning + Acting) agent.
    
    Args:
        system_prompt: System prompt defining agent behavior
        tools: List of tool names to enable (None = all)
        max_iterations: Maximum reasoning steps
        model_name: Ollama model to use
    
    Returns:
        Compiled StateGraph
    """
    # Filter tools if specified
    available_tools = AVAILABLE_TOOLS
    if tools:
        available_tools = {k: v for k, v in AVAILABLE_TOOLS.items() if k in tools}
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("call_model", lambda s: call_model(s, model_name))
    workflow.add_node("execute_tools", execute_tools)
    
    # Add edges
    workflow.set_entry_point("call_model")
    workflow.add_conditional_edges(
        "call_model",
        should_continue,
        {
            "execute_tools": "execute_tools",
            "call_model": "call_model",
            "end": END,
        }
    )
    workflow.add_conditional_edges(
        "execute_tools",
        should_continue,
        {
            "execute_tools": "execute_tools",
            "call_model": "call_model",
            "end": END,
        }
    )
    
    # Compile
    return workflow.compile()


# ============================================
# Pre-built Agents
# ============================================

CODE_AGENT_SYSTEM_PROMPT = """You are an expert software engineer. You help users write, review, and debug code.
You have access to tools for searching documentation, executing code, and file operations.

When writing code:
1. Follow best practices and clean code principles
2. Add type hints and docstrings
3. Handle errors gracefully
4. Write tests when appropriate

When debugging:
1. Analyze the error message carefully
2. Search for relevant documentation if needed
3. Propose minimal, targeted fixes
4. Explain the root cause

Always think step by step and use tools when you need information."""

RESEARCH_AGENT_SYSTEM_PROMPT = """You are a research analyst. You help users find, synthesize, and analyze information.
You have access to a knowledge base (vector search) and web search.

When researching:
1. Break down complex questions into sub-questions
2. Search the knowledge base first for internal docs
3. Use web search for current/external information
4. Synthesize findings with citations
5. Present clear, actionable insights

Always cite your sources and indicate confidence levels."""

WRITING_AGENT_SYSTEM_PROMPT = """You are a professional technical writer. You help users create clear, engaging content.
You have access to the knowledge base for reference material.

When writing:
1. Understand the audience and purpose
2. Structure content logically with clear headings
3. Use active voice and concise language
4. Include examples and code snippets where helpful
5. Follow the project's style guide

Adapt your tone: technical for docs, conversational for blogs, persuasive for marketing."""


def get_code_agent(max_iterations: int = 10) -> StateGraph:
    """Get a code-focused agent."""
    return create_react_agent(
        system_prompt=CODE_AGENT_SYSTEM_PROMPT,
        tools=["vector_search", "code_execution", "file_operation"],
        max_iterations=max_iterations,
        model_name="codellama:13b-instruct",
    )


def get_research_agent(max_iterations: int = 8) -> StateGraph:
    """Get a research-focused agent."""
    return create_react_agent(
        system_prompt=RESEARCH_AGENT_SYSTEM_PROMPT,
        tools=["vector_search", "web_search"],
        max_iterations=max_iterations,
        model_name="llama3.1:8b",
    )


def get_writing_agent(max_iterations: int = 6) -> StateGraph:
    """Get a writing-focused agent."""
    return create_react_agent(
        system_prompt=WRITING_AGENT_SYSTEM_PROMPT,
        tools=["vector_search", "file_operation"],
        max_iterations=max_iterations,
        model_name="llama3.1:8b",
    )


def get_general_agent(max_iterations: int = 10) -> StateGraph:
    """Get a general-purpose agent with all tools."""
    return create_react_agent(
        system_prompt="You are a helpful AI assistant with access to various tools. Use them to help the user accomplish their goals.",
        tools=None,  # All tools
        max_iterations=max_iterations,
    )


# ============================================
# Agent Runner
# ============================================

@dataclass
class AgentRunResult:
    """Result of an agent run."""
    success: bool
    messages: List[BaseMessage]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    iterations: int
    tokens_used: int = 0


async def run_agent(
    agent: StateGraph,
    user_input: str,
    context: Optional[Dict[str, Any]] = None,
    system_prompt: Optional[str] = None,
) -> AgentRunResult:
    """
    Run an agent with the given input.
    
    Args:
        agent: Compiled LangGraph agent
        user_input: User's message
        context: Additional context data
        system_prompt: Optional override for system prompt
    
    Returns:
        AgentRunResult with messages and result
    """
    initial_state: AgentState = {
        "messages": [
            SystemMessage(content=system_prompt or "You are a helpful AI assistant."),
            HumanMessage(content=user_input),
        ],
        "context": context or {},
        "current_step": "start",
        "iterations": 0,
        "max_iterations": 10,
        "error": None,
        "result": None,
    }
    
    try:
        final_state = await agent.ainvoke(initial_state)
        
        # Extract result from last AI message
        last_ai = None
        for msg in reversed(final_state["messages"]):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                last_ai = msg
                break
        
        return AgentRunResult(
            success=True,
            messages=final_state["messages"],
            result=final_state.get("result"),
            error=None,
            iterations=final_state["iterations"],
        )
    except Exception as e:
        logger.error("Agent run failed", error=str(e))
        return AgentRunResult(
            success=False,
            messages=initial_state["messages"],
            result=None,
            error=str(e),
            iterations=0,
        )


# ============================================
# Multi-Agent Workflow Example
# ============================================

async def run_code_review_workflow(
    code: str,
    language: str = "python",
    focus_areas: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Run a multi-agent code review workflow:
    1. Code Analyzer - analyzes structure and patterns
    2. Security Reviewer - checks for security issues
    3. Performance Reviewer - checks for performance issues
    4. Synthesizer - combines all reviews into final report
    """
    focus = focus_areas or ["security", "performance", "maintainability", "best_practices"]
    
    # Step 1: Code Analysis
    code_agent = get_code_agent(max_iterations=5)
    analysis_result = await run_agent(
        code_agent,
        f"Analyze this {language} code for structure, patterns, and quality:\n\n```{language}\n{code}\n```",
        system_prompt="You are a senior code reviewer. Analyze code structure, design patterns, and maintainability. Be thorough but concise.",
    )
    
    # Step 2: Security Review (simplified - would use specialized prompt in production)
    security_result = await run_agent(
        code_agent,
        f"Review this {language} code for security vulnerabilities:\n\n```{language}\n{code}\n```",
        system_prompt="You are a security expert. Focus on: injection flaws, authentication issues, data exposure, insecure dependencies, and OWASP Top 10.",
    )
    
    # Step 3: Synthesize
    synthesizer = get_writing_agent(max_iterations=3)
    final_result = await run_agent(
        synthesizer,
        f"""Create a comprehensive code review report based on these analyses:

STRUCTURE & QUALITY ANALYSIS:
{analysis_result.messages[-1].content if analysis_result.messages else 'N/A'}

SECURITY REVIEW:
{security_result.messages[-1].content if security_result.messages else 'N/A'}

Focus areas: {', '.join(focus)}

Format as:
## Summary
## Issues Found (by severity: Critical/High/Medium/Low)
## Recommendations
## Code Examples (if applicable)""",
        system_prompt="You are a technical lead creating a code review report. Be specific, actionable, and prioritize by impact.",
    )
    
    return {
        "analysis": analysis_result.messages[-1].content if analysis_result.messages else None,
        "security": security_result.messages[-1].content if security_result.messages else None,
        "report": final_result.messages[-1].content if final_result.messages else None,
    }