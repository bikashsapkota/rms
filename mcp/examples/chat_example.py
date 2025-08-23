"""Example of using the MCP server with Ollama for restaurant reservations."""

import asyncio
import httpx
from datetime import datetime, date, time
import json


class MCPChatClient:
    """Simple client for testing MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.session_id = None
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def chat(self, message: str, restaurant_id: str = None) -> dict:
        """Send a chat message to the MCP server."""
        payload = {
            "message": message,
            "session_id": self.session_id,
            "restaurant_id": restaurant_id
        }
        
        response = await self.client.post(f"{self.base_url}/chat", json=payload)
        response.raise_for_status()
        
        data = response.json()
        self.session_id = data["session_id"]
        
        return data
    
    async def health_check(self) -> dict:
        """Check server health."""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    async def get_tools(self) -> dict:
        """Get available tools."""
        response = await self.client.get(f"{self.base_url}/tools")
        response.raise_for_status()
        return response.json()


async def run_conversation_examples():
    """Run example conversations with the MCP server."""
    
    async with MCPChatClient() as client:
        print("🚀 Starting MCP Chat Examples")
        print("=" * 50)
        
        # Check server health
        try:
            health = await client.health_check()
            print(f"✅ Server Health: {health}")
        except Exception as e:
            print(f"❌ Server health check failed: {e}")
            return
        
        # Get available tools
        try:
            tools = await client.get_tools()
            print(f"🔧 Available Tools: {tools['count']}")
            for tool in tools['tools']:
                print(f"  - {tool['name']}: {tool['description']}")
        except Exception as e:
            print(f"❌ Failed to get tools: {e}")
        
        print("\n" + "=" * 50)
        
        # Example conversations
        examples = [
            "Hello! I'd like to make a reservation.",
            "Check availability for 4 people tomorrow at 7 PM",
            "Book a table for 2 people on 2025-08-25 at 19:00. My name is John Doe, email john@example.com, phone 555-1234",
            "What are your hours?",
            "Can I modify my reservation?"
        ]
        
        for i, message in enumerate(examples, 1):
            print(f"\n🗣️  Example {i}: {message}")
            print("-" * 30)
            
            try:
                response = await client.chat(message)
                
                # Show tool calls if any
                if response.get("tool_calls"):
                    print("🔧 Tool Calls:")
                    for tool_call in response["tool_calls"]:
                        print(f"  - {tool_call['name']}: {tool_call['arguments']}")
                
                # Show tool responses if any
                if response.get("tool_responses"):
                    print("📊 Tool Results:")
                    for tool_response in response["tool_responses"]:
                        if tool_response["success"]:
                            print(f"  ✅ {tool_response['tool_name']}: {tool_response.get('result', {}).get('message', 'Success')}")
                        else:
                            print(f"  ❌ {tool_response['tool_name']}: {tool_response.get('error', 'Failed')}")
                
                # Show assistant response
                print(f"🤖 Assistant: {response['response']}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Small delay between examples
            await asyncio.sleep(1)
        
        print("\n" + "=" * 50)
        print("✅ Conversation examples completed!")


async def test_tool_execution():
    """Test direct tool execution."""
    
    print("\n🔧 Testing Direct Tool Execution")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test availability check
        tool_request = {
            "tool_name": "check_availability",
            "arguments": {
                "restaurant_id": "a499f8ac-6307-4a84-ab2c-41ab36361b4c",
                "date": "2025-08-25",
                "time": "19:00",
                "party_size": 4
            }
        }
        
        try:
            response = await client.post("http://localhost:3001/execute-tool", json=tool_request)
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Tool Execution Result:")
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"❌ Tool execution failed: {e}")


if __name__ == "__main__":
    print("🎯 RMS MCP Server Test Client")
    print("Make sure the MCP server is running on localhost:3001")
    print("Make sure Ollama is running with llama3.1:8b model")
    print("Make sure RMS backend is running on localhost:8000")
    print()
    
    # Run examples
    asyncio.run(run_conversation_examples())
    asyncio.run(test_tool_execution())