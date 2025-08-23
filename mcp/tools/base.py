"""Base classes for MCP tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import logging

from models.common import ToolResponse

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for MCP tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute the tool with given arguments."""
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any], required_fields: list) -> bool:
        """Validate that required arguments are present."""
        for field in required_fields:
            if field not in arguments or arguments[field] is None:
                return False
        return True
    
    async def safe_execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute tool with error handling and timing."""
        start_time = time.time()
        
        try:
            logger.info(f"Executing tool {self.name} with arguments: {arguments}")
            result = await self.execute(arguments)
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            logger.info(f"Tool {self.name} completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tool {self.name} failed after {execution_time:.2f}s: {e}")
            
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time
            )


class ReservationTool(BaseTool):
    """Base class for reservation-related tools."""
    
    def __init__(self, name: str, description: str, rms_client):
        super().__init__(name, description)
        self.rms_client = rms_client
    
    def format_error_message(self, error: str) -> str:
        """Format error message for user-friendly display."""
        if "404" in error:
            return "Reservation not found. Please check the reservation ID."
        elif "401" in error or "403" in error:
            return "Access denied. Please verify your email address."
        elif "400" in error:
            return "Invalid request. Please check your input."
        elif "500" in error:
            return "Server error. Please try again later."
        else:
            return f"An error occurred: {error}"
    
    def format_success_message(self, action: str, details: str = "") -> str:
        """Format success message for user-friendly display."""
        messages = {
            "check_availability": f"Availability checked successfully. {details}",
            "create_reservation": f"Reservation created successfully! {details}",
            "get_reservation": f"Reservation details retrieved. {details}",
            "update_reservation": f"Reservation updated successfully. {details}",
            "cancel_reservation": f"Reservation cancelled successfully. {details}"
        }
        return messages.get(action, f"Operation completed successfully. {details}")


class ToolRegistry:
    """Registry for managing MCP tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def get_tool_schemas(self) -> list:
        """Get tool schemas for MCP/function calling."""
        from config import MCP_TOOLS
        return MCP_TOOLS
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        
        if not tool:
            return ToolResponse(
                tool_name=name,
                success=False,
                result=None,
                error=f"Tool '{name}' not found"
            )
        
        return await tool.safe_execute(arguments)