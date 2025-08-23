"""Ollama client for MCP integration."""

import ollama
import json
import asyncio
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from config import Config, OLLAMA_CONFIGS, MCP_TOOLS
from models.common import ConversationMessage, ToolCall, ToolResponse

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama models."""
    
    def __init__(self, model_name: str = None, host: str = None):
        self.model_name = model_name or Config.DEFAULT_MODEL
        self.host = host or Config.OLLAMA_HOST
        self.model_config = OLLAMA_CONFIGS.get(self.model_name, OLLAMA_CONFIGS["llama3.1:8b"])
        
        # Initialize Ollama client
        self.client = ollama.AsyncClient(host=self.host)
        
        logger.info(f"Initialized Ollama client with model: {self.model_name}")
    
    async def check_model_availability(self) -> bool:
        """Check if the specified model is available."""
        try:
            models = await self.client.list()
            available_models = [model.get('name', '') for model in models.get('models', [])]
            
            if self.model_name in available_models:
                return True
            
            logger.warning(f"Model {self.model_name} not found. Available models: {available_models}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    async def pull_model_if_needed(self) -> bool:
        """Pull the model if it's not available locally."""
        try:
            if await self.check_model_availability():
                return True
            
            logger.info(f"Pulling model {self.model_name}...")
            await self.client.pull(self.model_name)
            logger.info(f"Successfully pulled model {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error pulling model {self.model_name}: {e}")
            return False
    
    def _prepare_messages(self, conversation_history: List[ConversationMessage]) -> List[Dict[str, str]]:
        """Convert conversation history to Ollama message format."""
        messages = []
        
        # Add system message
        system_prompt = self.model_config.get("system_prompt", "You are a helpful assistant.")
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return messages
    
    def _prepare_tools(self) -> List[Dict[str, Any]]:
        """Prepare MCP tools for Ollama function calling."""
        tools = []
        
        for tool in MCP_TOOLS:
            # Convert MCP tool format to Ollama function calling format
            ollama_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            }
            tools.append(ollama_tool)
        
        return tools
    
    async def chat_with_tools(
        self, 
        message: str, 
        conversation_history: List[ConversationMessage] = None,
        tools_available: bool = True
    ) -> Dict[str, Any]:
        """Chat with Ollama model using MCP tools."""
        try:
            conversation_history = conversation_history or []
            
            # Add user message to history
            user_message = ConversationMessage(
                role="user",
                content=message,
                timestamp=datetime.now()
            )
            conversation_history.append(user_message)
            
            # Prepare messages and tools
            messages = self._prepare_messages(conversation_history)
            tools = self._prepare_tools() if tools_available else None
            
            # Chat options from model config
            options = {
                "temperature": self.model_config.get("temperature", 0.1),
                "top_p": self.model_config.get("top_p", 0.9),
                "num_predict": self.model_config.get("max_tokens", 1000)
            }
            
            # Make request to Ollama
            if tools:
                response = await self.client.chat(
                    model=self.model_name,
                    messages=messages,
                    tools=tools,
                    options=options,
                    stream=False
                )
            else:
                response = await self.client.chat(
                    model=self.model_name,
                    messages=messages,
                    options=options,
                    stream=False
                )
            
            # Process response
            assistant_message = response.get("message", {})
            content = assistant_message.get("content", "")
            tool_calls = assistant_message.get("tool_calls", [])
            
            # Convert tool calls to our format
            converted_tool_calls = []
            if tool_calls:
                for tool_call in tool_calls:
                    function = tool_call.get("function", {})
                    converted_tool_calls.append(ToolCall(
                        name=function.get("name", ""),
                        arguments=function.get("arguments", {})
                    ))
            
            return {
                "success": True,
                "content": content,
                "tool_calls": converted_tool_calls,
                "model": self.model_name,
                "usage": {
                    "prompt_tokens": response.get("prompt_eval_count", 0),
                    "completion_tokens": response.get("eval_count", 0),
                    "total_tokens": response.get("prompt_eval_count", 0) + response.get("eval_count", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in chat_with_tools: {e}")
            return {
                "success": False,
                "content": f"I apologize, but I encountered an error: {str(e)}",
                "tool_calls": [],
                "error": str(e)
            }
    
    async def generate_response(self, prompt: str, max_tokens: int = None) -> str:
        """Generate a simple text response without tools."""
        try:
            options = {
                "temperature": self.model_config.get("temperature", 0.1),
                "top_p": self.model_config.get("top_p", 0.9),
                "num_predict": max_tokens or self.model_config.get("max_tokens", 1000)
            }
            
            response = await self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options=options,
                stream=False
            )
            
            return response.get("response", "")
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def stream_chat(
        self, 
        message: str, 
        conversation_history: List[ConversationMessage] = None
    ):
        """Stream chat response for real-time interaction."""
        try:
            conversation_history = conversation_history or []
            
            # Add user message
            user_message = ConversationMessage(
                role="user",
                content=message,
                timestamp=datetime.now()
            )
            conversation_history.append(user_message)
            
            messages = self._prepare_messages(conversation_history)
            
            options = {
                "temperature": self.model_config.get("temperature", 0.1),
                "top_p": self.model_config.get("top_p", 0.9),
                "num_predict": self.model_config.get("max_tokens", 1000)
            }
            
            # Stream response
            async for part in await self.client.chat(
                model=self.model_name,
                messages=messages,
                options=options,
                stream=True
            ):
                if "message" in part:
                    content = part["message"].get("content", "")
                    if content:
                        yield content
                        
        except Exception as e:
            logger.error(f"Error in stream_chat: {e}")
            yield f"Error: {str(e)}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "model_name": self.model_name,
            "host": self.host,
            "config": self.model_config,
            "tools_available": len(MCP_TOOLS)
        }