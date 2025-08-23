# RMS MCP Server - Ollama Integration

A Model Context Protocol (MCP) server that integrates Ollama with the Restaurant Management System, enabling AI assistants to handle restaurant reservations through natural language conversations.

## Features

🤖 **Ollama Integration**: Local AI models (Llama, Mistral, etc.) for privacy and cost-effectiveness  
🍽️ **Reservation Management**: Complete reservation lifecycle through natural language  
🔧 **MCP Tools**: Check availability, create, update, and cancel reservations  
💬 **Real-time Chat**: WebSocket support for streaming conversations  
🎯 **Multi-tenant**: Support for multiple restaurants and organizations  
📊 **Tool Execution**: Direct tool execution with detailed responses  

## Quick Start

### Prerequisites

1. **Ollama** installed and running:
   ```bash
   # Install Ollama (macOS)
   brew install ollama
   
   # Start Ollama service
   ollama serve
   
   # Pull a model (choose one)
   ollama pull llama3.1:8b    # Recommended
   ollama pull mistral:7b     # Lighter alternative
   ollama pull phi3:mini      # Fastest option
   ```

2. **RMS Backend** running on `localhost:8000`
3. **Python 3.8+** with pip

### Installation

1. **Install dependencies**:
   ```bash
   cd mcp
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the MCP server**:
   ```bash
   python -m uvicorn server:app --host localhost --port 3001 --reload
   ```

### Verify Installation

1. **Check server health**:
   ```bash
   curl http://localhost:3001/health
   ```

2. **View available tools**:
   ```bash
   curl http://localhost:3001/tools
   ```

3. **Open demo page**:
   Open http://localhost:3001/demo in your browser

## Usage Examples

### Chat API

Send natural language messages to make reservations:

```bash
curl -X POST http://localhost:3001/chat \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "Check availability for 4 people tomorrow at 7 PM",
    "restaurant_id": "a499f8ac-6307-4a84-ab2c-41ab36361b4c"
  }'
```

### Direct Tool Execution

Execute specific tools directly:

```bash
curl -X POST http://localhost:3001/execute-tool \\
  -H "Content-Type: application/json" \\
  -d '{
    "tool_name": "check_availability",
    "arguments": {
      "restaurant_id": "a499f8ac-6307-4a84-ab2c-41ab36361b4c",
      "date": "2025-08-25",
      "time": "19:00",
      "party_size": 4
    }
  }'
```

### Python Client Example

```python
import asyncio
from examples.chat_example import MCPChatClient

async def main():
    async with MCPChatClient() as client:
        response = await client.chat("Book a table for 2 people tonight at 8 PM")
        print(response["response"])

asyncio.run(main())
```

## Conversation Examples

Try these natural language requests:

- **Check Availability**: "Do you have a table for 4 people tomorrow at 7 PM?"
- **Make Reservation**: "Book a table for 2 on Friday at 8 PM. My name is John Smith, email john@example.com"
- **View Reservation**: "Show me my reservation details for ID RES-123"
- **Modify Reservation**: "Change my reservation to 6 people instead of 4"
- **Cancel Reservation**: "Cancel my reservation for Saturday"

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server information |
| `/health` | GET | Health check for all services |
| `/tools` | GET | Available MCP tools |
| `/chat` | POST | Chat with Ollama using tools |
| `/execute-tool` | POST | Execute specific tool |
| `/demo` | GET | Interactive demo page |
| `/ws/chat` | WebSocket | Real-time chat streaming |

## Available Tools

### 1. Check Availability
Check table availability for specific date/time/party size.

**Parameters**:
- `restaurant_id`: Restaurant identifier
- `date`: Date in YYYY-MM-DD format
- `time`: Time in HH:MM format (24-hour)
- `party_size`: Number of guests

### 2. Create Reservation
Make a new reservation.

**Parameters**:
- `restaurant_id`: Restaurant identifier
- `customer_name`: Customer full name
- `customer_email`: Customer email
- `customer_phone`: Customer phone
- `date`: Reservation date
- `time`: Reservation time
- `party_size`: Number of guests
- `special_requests` (optional): Special requests

### 3. Get Reservation
Retrieve reservation details by ID.

**Parameters**:
- `reservation_id`: Reservation ID
- `customer_email`: Email for verification

### 4. Update Reservation
Modify existing reservation.

**Parameters**:
- `reservation_id`: Reservation ID
- `customer_email`: Email for verification
- `date` (optional): New date
- `time` (optional): New time
- `party_size` (optional): New party size
- `special_requests` (optional): Updated requests

### 5. Cancel Reservation
Cancel a reservation.

**Parameters**:
- `reservation_id`: Reservation ID
- `customer_email`: Email for verification
- `reason` (optional): Cancellation reason

## Configuration

### Environment Variables

```bash
# RMS Backend
RMS_API_URL=http://localhost:8000
RMS_API_KEY=                    # Optional API key

# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=3001

# Ollama
OLLAMA_HOST=http://localhost:11434
DEFAULT_OLLAMA_MODEL=llama3.1:8b

# Other
RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO
DEFAULT_RESTAURANT_ID=a499f8ac-6307-4a84-ab2c-41ab36361b4c
DEFAULT_ORGANIZATION_ID=2da4af12-63af-432a-ad0d-51dc68568028
```

### Ollama Model Options

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `llama3.1:8b` | ~4.7GB | Medium | High | Recommended for production |
| `llama3.1:70b` | ~40GB | Slow | Highest | Best quality (requires GPU) |
| `mistral:7b` | ~4.1GB | Fast | Good | Resource-constrained environments |
| `phi3:mini` | ~2.3GB | Fastest | Fair | Quick responses, basic tasks |

## Development

### Project Structure

```
mcp/
├── server.py              # Main MCP server
├── config.py             # Configuration settings
├── requirements.txt       # Python dependencies
├── clients/              # API clients
│   ├── rms_client.py     # RMS backend client
│   └── ollama_client.py  # Ollama integration
├── tools/               # MCP tools
│   ├── base.py          # Base tool classes
│   └── reservations.py  # Reservation tools
├── models/              # Data models
│   ├── common.py        # Common models
│   └── reservation.py   # Reservation models
└── examples/            # Usage examples
    └── chat_example.py  # Python client example
```

### Adding New Tools

1. Create tool class inheriting from `BaseTool`:
   ```python
   from tools.base import BaseTool
   from models.common import ToolResponse
   
   class MyTool(BaseTool):
       def __init__(self, rms_client):
           super().__init__("my_tool", "Description of my tool")
           self.rms_client = rms_client
       
       async def execute(self, arguments):
           # Implementation
           return ToolResponse(...)
   ```

2. Register tool in `server.py`:
   ```python
   tool_registry.register(MyTool(rms_client))
   ```

3. Add tool schema to `config.py` in `MCP_TOOLS` list.

### Testing

Run the example client:
```bash
python examples/chat_example.py
```

### Logging

Logs are output to console with configurable level:
```bash
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## Troubleshooting

### Common Issues

1. **Ollama model not found**:
   ```bash
   ollama pull llama3.1:8b
   ```

2. **RMS API connection failed**:
   - Verify RMS backend is running on localhost:8000
   - Check `/health` endpoint

3. **Tool execution errors**:
   - Check restaurant_id and organization_id in environment
   - Verify date/time formats (YYYY-MM-DD, HH:MM)

4. **Import errors**:
   ```bash
   pip install -r requirements.txt
   ```

### Performance Tips

1. **Use appropriate model size** for your hardware
2. **Enable GPU acceleration** for Ollama if available
3. **Adjust conversation history length** for memory efficiency
4. **Use WebSocket streaming** for real-time interactions

## License

This project is part of the Restaurant Management System and follows the same licensing terms.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

For questions or support, please create an issue in the main RMS repository.