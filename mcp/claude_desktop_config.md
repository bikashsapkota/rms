# Claude Desktop MCP Integration Guide

## Overview
This guide shows how to integrate your Restaurant Management System MCP server with Claude Desktop.

## Prerequisites
1. Claude Desktop installed on your machine
2. MCP server running on localhost:3001
3. RMS backend running on localhost:8000
4. Ollama with gpt-oss:20b model installed

## Configuration Steps

### 1. Locate Claude Desktop Configuration
Claude Desktop uses a configuration file located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 2. Create/Update Configuration File
Add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "restaurant-reservations": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/Users/bi_sapkota/personal_projects/rms/mcp/server.py"
      ],
      "cwd": "/Users/bi_sapkota/personal_projects/rms/mcp",
      "env": {
        "RMS_API_URL": "http://localhost:8000",
        "DEFAULT_OLLAMA_MODEL": "gpt-oss:20b",
        "DEFAULT_RESTAURANT_ID": "a499f8ac-6307-4a84-ab2c-41ab36361b4c",
        "DEFAULT_ORGANIZATION_ID": "2da4af12-63af-432a-ad0d-51dc68568028"
      }
    }
  }
}
```

### 3. Alternative: Direct Python Execution
If you prefer direct Python execution:

```json
{
  "mcpServers": {
    "restaurant-reservations": {
      "command": "python",
      "args": [
        "/Users/bi_sapkota/personal_projects/rms/mcp/server.py"
      ],
      "cwd": "/Users/bi_sapkota/personal_projects/rms/mcp",
      "env": {
        "RMS_API_URL": "http://localhost:8000",
        "DEFAULT_OLLAMA_MODEL": "gpt-oss:20b",
        "DEFAULT_RESTAURANT_ID": "a499f8ac-6307-4a84-ab2c-41ab36361b4c",
        "DEFAULT_ORGANIZATION_ID": "2da4af12-63af-432a-ad0d-51dc68568028"
      }
    }
  }
}
```

### 4. Verify Prerequisites
Before starting Claude Desktop, ensure:

```bash
# Check if RMS backend is running
curl http://localhost:8000/health

# Check if Ollama is running
curl http://localhost:11434/api/tags

# Verify gpt-oss:20b model is available
ollama list | grep gpt-oss
```

### 5. Start Claude Desktop
1. Close Claude Desktop if it's running
2. Restart Claude Desktop
3. The MCP server should automatically connect

## Available Tools
Once configured, Claude Desktop will have access to these restaurant reservation tools:

1. **check_availability** - Check table availability for specific dates and party sizes
2. **create_reservation** - Create new reservations with customer details
3. **get_reservation** - Retrieve reservation details by ID
4. **update_reservation** - Modify existing reservations
5. **cancel_reservation** - Cancel reservations

## Testing the Integration

### Test Availability Check
```
"Check availability for 2 people tomorrow at 7 PM"
```

### Test Reservation Creation
```
"Book a table for 2 people tomorrow at 7 PM for John Smith, email john@example.com, phone 555-1234"
```

### Test General Query
```
"What can you help me with?"
```

## Troubleshooting

### Common Issues

1. **MCP Server Won't Start**
   - Ensure RMS backend is running on port 8000
   - Check that Ollama is running and gpt-oss:20b model is available
   - Verify file paths in configuration are correct

2. **Tools Not Available**
   - Check Claude Desktop logs for MCP connection errors
   - Ensure the MCP server process is running
   - Verify configuration file syntax is valid JSON

3. **API Errors**
   - Confirm RMS backend health endpoint returns 200
   - Check that database services are running
   - Verify restaurant and organization IDs exist

### Logs and Debugging
- Claude Desktop logs: Check application logs for MCP connection status
- MCP server logs: Monitor console output for API calls and errors
- RMS backend logs: Check FastAPI server logs for request processing

## Environment Variables
The following environment variables can be customized:

- `RMS_API_URL`: RMS backend URL (default: http://localhost:8000)
- `DEFAULT_OLLAMA_MODEL`: Ollama model to use (default: gpt-oss:20b)
- `DEFAULT_RESTAURANT_ID`: Restaurant context for requests
- `DEFAULT_ORGANIZATION_ID`: Organization context for requests
- `MCP_SERVER_PORT`: MCP server port (default: 3001)

## Security Notes
- This configuration is for development/demo purposes
- For production, use proper authentication and HTTPS
- Consider rate limiting and input validation
- Store sensitive configuration in environment variables