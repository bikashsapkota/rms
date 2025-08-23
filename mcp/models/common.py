"""Common data models for MCP responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


class MCPResponse(BaseModel):
    """Base MCP response model."""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class MCPError(BaseModel):
    """MCP error response."""
    error: str
    code: str
    details: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    """Tool call request."""
    name: str
    arguments: Dict[str, Any]


class ToolResponse(BaseModel):
    """Tool execution response."""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: Optional[float] = None


class ConversationMessage(BaseModel):
    """Conversation message."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    tool_calls: Optional[List[ToolCall]] = None
    tool_responses: Optional[List[ToolResponse]] = None


class ConversationSession(BaseModel):
    """Conversation session state."""
    session_id: str
    restaurant_id: str
    messages: List[ConversationMessage]
    created_at: datetime
    last_activity: datetime
    model_name: str
    context: Optional[Dict[str, Any]] = None