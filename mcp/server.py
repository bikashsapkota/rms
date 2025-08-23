"""MCP Server for Restaurant Management System with Ollama integration."""

import asyncio
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from config import Config
from clients.rms_client import RMSAPIClient
from clients.ollama_client import OllamaClient
from tools.base import ToolRegistry
from tools.reservations import (
    CheckAvailabilityTool, CreateReservationTool, GetReservationTool,
    UpdateReservationTool, CancelReservationTool
)
from models.common import ConversationMessage, ConversationSession

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="RMS MCP Server",
    description="Model Context Protocol server for Restaurant Management System with Ollama integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global clients and registry
rms_client: Optional[RMSAPIClient] = None
ollama_client: Optional[OllamaClient] = None
tool_registry: Optional[ToolRegistry] = None

# Active conversations
active_sessions: Dict[str, ConversationSession] = {}


class ChatMessage(BaseModel):
    """Chat message request model."""
    message: str
    session_id: Optional[str] = None
    restaurant_id: Optional[str] = None
    model_name: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str
    tool_calls: List[Dict[str, Any]] = []
    tool_responses: List[Dict[str, Any]] = []
    model_info: Optional[Dict[str, Any]] = None


class ToolExecutionRequest(BaseModel):
    """Tool execution request model."""
    tool_name: str
    arguments: Dict[str, Any]


@app.on_event("startup")
async def startup():
    """Initialize clients and tools on startup."""
    global rms_client, ollama_client, tool_registry
    
    logger.info("Starting MCP Server...")
    
    # Initialize RMS client
    rms_client = RMSAPIClient()
    
    # Check RMS API health
    try:
        health = await rms_client.health_check()
        if health:
            logger.info("RMS API is healthy")
        else:
            logger.warning("RMS API health check failed")
    except Exception as e:
        logger.error(f"Failed to check RMS API health: {e}")
    
    # Initialize Ollama client
    ollama_client = OllamaClient()
    
    # Check Ollama availability and pull model if needed
    try:
        model_available = await ollama_client.check_model_availability()
        if not model_available:
            logger.info("Pulling Ollama model...")
            await ollama_client.pull_model_if_needed()
        
        logger.info(f"Ollama client initialized with model: {ollama_client.model_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Ollama client: {e}")
    
    # Initialize tool registry
    tool_registry = ToolRegistry()
    
    # Register reservation tools
    tool_registry.register(CheckAvailabilityTool(rms_client))
    tool_registry.register(CreateReservationTool(rms_client))
    tool_registry.register(GetReservationTool(rms_client))
    tool_registry.register(UpdateReservationTool(rms_client))
    tool_registry.register(CancelReservationTool(rms_client))
    
    logger.info(f"Registered {len(tool_registry.get_all_tools())} tools")
    logger.info("MCP Server startup complete")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    global rms_client
    
    logger.info("Shutting down MCP Server...")
    
    if rms_client:
        await rms_client.__aexit__(None, None, None)
    
    logger.info("MCP Server shutdown complete")


@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "RMS MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol server for Restaurant Management System",
        "ollama_model": ollama_client.model_name if ollama_client else None,
        "tools_available": len(tool_registry.get_all_tools()) if tool_registry else 0,
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    health_status = {
        "mcp_server": "healthy",
        "rms_api": "unknown",
        "ollama": "unknown",
        "timestamp": datetime.now().isoformat()
    }
    
    # Check RMS API
    if rms_client:
        try:
            rms_healthy = await rms_client.health_check()
            health_status["rms_api"] = "healthy" if rms_healthy else "unhealthy"
        except Exception as e:
            health_status["rms_api"] = f"error: {str(e)}"
    
    # Check Ollama
    if ollama_client:
        try:
            model_available = await ollama_client.check_model_availability()
            health_status["ollama"] = "healthy" if model_available else "model_not_available"
        except Exception as e:
            health_status["ollama"] = f"error: {str(e)}"
    
    return health_status


@app.get("/tools")
async def get_tools():
    """Get available MCP tools."""
    if not tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not initialized")
    
    return {
        "tools": tool_registry.get_tool_schemas(),
        "count": len(tool_registry.get_all_tools())
    }


@app.post("/execute-tool")
async def execute_tool(request: ToolExecutionRequest):
    """Execute a specific MCP tool."""
    if not tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not initialized")
    
    try:
        result = await tool_registry.execute_tool(request.tool_name, request.arguments)
        return result.dict()
    except Exception as e:
        logger.error(f"Error executing tool {request.tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatMessage) -> ChatResponse:
    """Chat with Ollama using MCP tools."""
    if not ollama_client or not tool_registry:
        raise HTTPException(status_code=503, detail="Clients not initialized")
    
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        restaurant_id = request.restaurant_id or Config.DEFAULT_RESTAURANT_ID
        
        if session_id not in active_sessions:
            active_sessions[session_id] = ConversationSession(
                session_id=session_id,
                restaurant_id=restaurant_id,
                messages=[],
                created_at=datetime.now(),
                last_activity=datetime.now(),
                model_name=request.model_name or ollama_client.model_name
            )
        
        session = active_sessions[session_id]
        session.last_activity = datetime.now()
        
        # Check if this is a general question that shouldn't use tools
        general_keywords = [
            "what can you do", "what do you do", "help", "hello", "hi", 
            "how does this work", "what are your capabilities", "introduction",
            "what can i do", "how can you help", "what's possible"
        ]
        
        is_general_query = any(keyword in request.message.lower() for keyword in general_keywords)
        
        # Chat with Ollama - disable tools for general queries
        if is_general_query:
            chat_result = await ollama_client.chat_with_tools(
                message=request.message,
                conversation_history=session.messages,
                tools_available=False
            )
            
            # If no response generated, provide a default capabilities message
            if not chat_result.get("content", "").strip():
                chat_result["content"] = """I'm a restaurant reservation assistant for Demo Restaurant! I can help you with:

• **Check Availability** - Find available tables for specific dates and times
• **Make Reservations** - Book tables when you provide your contact details
• **View Reservations** - Look up existing bookings with your confirmation number
• **Modify Reservations** - Update your existing reservations
• **Cancel Reservations** - Cancel bookings if needed

Just ask me something like:
- "Check availability for 4 people tomorrow at 7 PM"
- "Book a table for 2 people on 2025-08-25 at 6:30 PM"
- "Look up my reservation"

How can I help you with your dining plans?"""
        else:
            chat_result = await ollama_client.chat_with_tools(
                message=request.message,
                conversation_history=session.messages,
                tools_available=True
            )
        
        # Process tool calls if any
        tool_responses = []
        if chat_result.get("tool_calls"):
            for tool_call in chat_result["tool_calls"]:
                # Validate create_reservation tool calls
                if tool_call.name == "create_reservation":
                    missing_fields = []
                    required_fields = ["customer_name", "customer_email", "customer_phone", "date", "time", "party_size"]
                    
                    for field in required_fields:
                        value = str(tool_call.arguments.get(field, "")).strip().lower()
                        if not value or value == "" or value == "unknown" or value == "none":
                            missing_fields.append(field)
                    
                    if missing_fields:
                        # Generate helpful message asking for missing information
                        field_names = {
                            "customer_name": "name",
                            "customer_email": "email address", 
                            "customer_phone": "phone number",
                            "date": "date",
                            "time": "time", 
                            "party_size": "party size"
                        }
                        missing_names = [field_names.get(field, field) for field in missing_fields]
                        
                        if len(missing_names) == 1:
                            missing_text = missing_names[0]
                        elif len(missing_names) == 2:
                            missing_text = f"{missing_names[0]} and {missing_names[1]}"
                        else:
                            missing_text = f"{', '.join(missing_names[:-1])}, and {missing_names[-1]}"
                        
                        error_response = {
                            "tool_name": tool_call.name,
                            "success": False,
                            "result": None,
                            "error": f"I'd be happy to book that table for you! However, I need your {missing_text} to complete the reservation. Could you please provide that information?",
                            "execution_time": 0.0
                        }
                        tool_responses.append(error_response)
                        continue
                
                # Execute the tool if validation passes
                try:
                    tool_result = await tool_registry.execute_tool(
                        tool_call.name,
                        tool_call.arguments
                    )
                    tool_responses.append(tool_result.dict())
                except Exception as e:
                    logger.error(f"Error executing tool {tool_call.name}: {e}")
                    tool_responses.append({
                        "tool_name": tool_call.name,
                        "success": False,
                        "error": str(e)
                    })
        
        # Add messages to session
        user_message = ConversationMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now()
        )
        session.messages.append(user_message)
        
        assistant_message = ConversationMessage(
            role="assistant",
            content=chat_result.get("content", ""),
            timestamp=datetime.now(),
            tool_calls=chat_result.get("tool_calls", []),
            tool_responses=tool_responses
        )
        session.messages.append(assistant_message)
        
        # Generate response content - use AI response or tool error messages
        response_content = chat_result.get("content", "")
        
        # If no AI response but we have tool errors, use the error message
        if not response_content and tool_responses:
            for tool_response in tool_responses:
                if not tool_response.get("success", True) and tool_response.get("error"):
                    response_content = tool_response["error"]
                    break
        
        return ChatResponse(
            response=response_content,
            session_id=session_id,
            tool_calls=[tc.dict() for tc in chat_result.get("tool_calls", [])],
            tool_responses=tool_responses,
            model_info=ollama_client.get_model_info()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get conversation session details."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    return session.dict()


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del active_sessions[session_id]
    return {"message": f"Session {session_id} deleted"}


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message = message_data.get("message", "")
            session_id = message_data.get("session_id", str(uuid.uuid4()))
            
            if not ollama_client:
                await websocket.send_text(json.dumps({
                    "error": "Ollama client not initialized"
                }))
                continue
            
            # Stream response
            response_chunks = []
            async for chunk in ollama_client.stream_chat(message):
                response_chunks.append(chunk)
                await websocket.send_text(json.dumps({
                    "type": "chunk",
                    "content": chunk,
                    "session_id": session_id
                }))
            
            # Send completion
            await websocket.send_text(json.dumps({
                "type": "complete",
                "full_response": "".join(response_chunks),
                "session_id": session_id
            }))
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "error": str(e)
        }))


@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Simple demo page for testing the MCP server."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RMS MCP Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .chat-container { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin: 10px 0; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background-color: #e3f2fd; }
            .assistant { background-color: #f1f8e9; }
            .tool-call { background-color: #fff3e0; font-size: 0.9em; }
            input[type="text"] { width: 70%; padding: 10px; }
            button { padding: 10px 20px; margin-left: 10px; }
        </style>
    </head>
    <body>
        <h1>RMS MCP Demo</h1>
        <p>Try asking: "Check availability for 4 people tomorrow at 7 PM" or "Book a table for 2 people on 2025-08-25 at 19:00"</p>
        
        <div class="chat-container" id="chatContainer"></div>
        
        <div>
            <input type="text" id="messageInput" placeholder="Type your message..." />
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <script>
            let sessionId = null;
            
            function addMessage(content, isUser = false, isToolCall = false) {
                const container = document.getElementById('chatContainer');
                const div = document.createElement('div');
                div.className = `message ${isUser ? 'user' : (isToolCall ? 'tool-call' : 'assistant')}`;
                div.innerHTML = content.replace(/\\n/g, '<br>');
                container.appendChild(div);
                container.scrollTop = container.scrollHeight;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                addMessage(message, true);
                input.value = '';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            message: message, 
                            session_id: sessionId,
                            restaurant_id: 'a499f8ac-6307-4a84-ab2c-41ab36361b4c'
                        })
                    });
                    
                    const data = await response.json();
                    sessionId = data.session_id;
                    
                    // Show tool calls
                    if (data.tool_calls && data.tool_calls.length > 0) {
                        for (const toolCall of data.tool_calls) {
                            addMessage(`🔧 Calling tool: ${toolCall.name}`, false, true);
                        }
                    }
                    
                    // Show tool responses
                    if (data.tool_responses && data.tool_responses.length > 0) {
                        for (const toolResponse of data.tool_responses) {
                            const status = toolResponse.success ? '✅' : '❌';
                            addMessage(`${status} Tool result: ${JSON.stringify(toolResponse.result, null, 2)}`, false, true);
                        }
                    }
                    
                    // Show assistant response
                    addMessage(data.response);
                    
                } catch (error) {
                    addMessage(`Error: ${error.message}`, false);
                }
            }
            
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=Config.MCP_SERVER_HOST,
        port=Config.MCP_SERVER_PORT,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    )