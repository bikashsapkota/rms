# MCP (Model Context Protocol) Integration Plans

## Overview
Create an MCP server that allows AI assistants (ChatGPT, Claude, etc.) to interact with the Restaurant Management System for reservations and ordering functionality.

## Phase 1: Foundation & Reservation Management

### 1. MCP Server Setup
- **File Structure:**
  ```
  mcp/
  ├── server.py                 # Main MCP server entry point
  ├── config.py                 # Configuration and environment variables
  ├── tools/                    # MCP tool implementations
  │   ├── __init__.py
  │   ├── reservations.py       # Reservation management tools
  │   └── base.py              # Base tool classes and utilities
  ├── models/                   # Data models for MCP responses
  │   ├── __init__.py
  │   ├── reservation.py        # Reservation data models
  │   └── common.py            # Common response models
  ├── clients/                  # API clients for backend communication
  │   ├── __init__.py
  │   └── rms_client.py        # RMS API client
  └── requirements.txt          # Python dependencies
  ```

### 2. Core MCP Tools for Reservations

#### Tool 1: `check_availability`
- **Purpose:** Check table availability for specific date/time/party size
- **Parameters:**
  - `restaurant_id` (string): Restaurant identifier
  - `date` (string): Reservation date (YYYY-MM-DD)
  - `time` (string): Preferred time (HH:MM)
  - `party_size` (integer): Number of guests
- **Returns:** Available time slots and table options

#### Tool 2: `create_reservation`
- **Purpose:** Make a new reservation
- **Parameters:**
  - `restaurant_id` (string): Restaurant identifier
  - `customer_name` (string): Customer full name
  - `customer_email` (string): Customer email
  - `customer_phone` (string): Customer phone number
  - `date` (string): Reservation date
  - `time` (string): Reservation time
  - `party_size` (integer): Number of guests
  - `special_requests` (string, optional): Special requests or notes
- **Returns:** Reservation confirmation with ID and details

#### Tool 3: `get_reservation`
- **Purpose:** Retrieve reservation details
- **Parameters:**
  - `reservation_id` (string): Reservation ID
  - `customer_email` (string, optional): Customer email for verification
- **Returns:** Full reservation details

#### Tool 4: `update_reservation`
- **Purpose:** Modify existing reservation
- **Parameters:**
  - `reservation_id` (string): Reservation ID
  - `customer_email` (string): Customer email for verification
  - `date` (string, optional): New date
  - `time` (string, optional): New time
  - `party_size` (integer, optional): New party size
  - `special_requests` (string, optional): Updated special requests
- **Returns:** Updated reservation details

#### Tool 5: `cancel_reservation`
- **Purpose:** Cancel a reservation
- **Parameters:**
  - `reservation_id` (string): Reservation ID
  - `customer_email` (string): Customer email for verification
  - `reason` (string, optional): Cancellation reason
- **Returns:** Cancellation confirmation

### 3. Authentication & Security

#### Multi-Tenant Support
- **Restaurant Context:** Each MCP request must include restaurant identification
- **Rate Limiting:** Implement per-restaurant rate limiting
- **Validation:** Input validation and sanitization for all parameters

#### Security Measures
- **API Key Authentication:** Secure communication with RMS backend
- **Customer Verification:** Email-based verification for reservation operations
- **Data Privacy:** Minimal data exposure, secure data handling

### 4. Integration with RMS Backend

#### API Client Implementation
- **Base Client:** HTTP client with authentication and error handling
- **Endpoint Mapping:**
  - `GET /api/v1/public/reservations/{restaurant_id}/availability`
  - `POST /api/v1/public/reservations/{restaurant_id}/book`
  - `GET /api/v1/public/reservations/{restaurant_id}/{reservation_id}`
  - `PUT /api/v1/public/reservations/{restaurant_id}/{reservation_id}`
  - `DELETE /api/v1/public/reservations/{restaurant_id}/{reservation_id}`

#### Error Handling
- **API Errors:** Graceful handling of backend API errors
- **Network Issues:** Retry logic and timeout handling
- **Validation Errors:** Clear error messages for invalid inputs

### 5. MCP Server Configuration

#### Environment Variables
```env
RMS_API_URL=http://localhost:8000
RMS_API_KEY=your-api-key
MCP_SERVER_PORT=3001
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
```

#### Deployment Options
- **Docker Container:** Containerized MCP server
- **Standalone Service:** Direct Python execution
- **Cloud Deployment:** AWS/GCP/Azure compatible

### 6. Testing Strategy

#### Unit Tests
- **Tool Functionality:** Test each MCP tool independently
- **API Client:** Test backend API communication
- **Validation Logic:** Test input validation and error handling

#### Integration Tests
- **End-to-End Flows:** Complete reservation workflows
- **Error Scenarios:** Network failures, invalid data, rate limiting
- **Multi-Restaurant:** Test tenant isolation

#### AI Assistant Testing
- **ChatGPT Integration:** Test with OpenAI's function calling
- **Claude Integration:** Test with Anthropic's tool use
- **Ollama Integration:** Test with local Ollama models (Llama, Mistral, etc.)
- **Conversation Flows:** Natural language reservation scenarios

### 7. Documentation & Examples

#### MCP Tool Documentation
- **Tool Schemas:** JSON schemas for all tools and parameters
- **Usage Examples:** Sample requests and responses
- **Error Codes:** Comprehensive error documentation

#### AI Assistant Prompts
- **System Prompts:** Recommended prompts for reservation assistance
- **Conversation Examples:** Sample dialogues for different scenarios
- **Ollama Model Configs:** Specific configurations for local models
- **Best Practices:** Guidelines for natural interaction

### 8. Phase 1 Deliverables

#### Core Implementation
- [ ] MCP server with reservation tools
- [ ] RMS API client integration
- [ ] Authentication and security layer
- [ ] Input validation and error handling

#### Testing & Documentation
- [ ] Comprehensive test suite
- [ ] API documentation
- [ ] Deployment guide
- [ ] AI assistant integration examples

#### Demo Scenarios
- [ ] "Book a table for 4 people tomorrow at 7 PM"
- [ ] "Check availability for Friday evening"
- [ ] "Modify my reservation to 6 people"
- [ ] "Cancel my reservation for Saturday"

## Ollama Integration Details

### Why Ollama Integration?
- **Privacy:** Keep customer data and conversations completely local
- **Cost-Effective:** No API costs for AI inference
- **Customization:** Fine-tune models specifically for restaurant domain
- **Offline Capability:** Works without internet connection
- **Performance:** Low latency for real-time conversations

### Recommended Ollama Models

#### For Reservations & General Assistance
- **Llama 3.1 (8B/70B):** Excellent function calling and reasoning
- **Mistral 7B:** Fast and efficient for basic tasks
- **CodeLlama:** Good for structured data handling
- **Phi-3:** Lightweight option for resource-constrained environments

#### Model-Specific Configurations
```json
{
  "ollama_configs": {
    "llama3.1:8b": {
      "temperature": 0.1,
      "top_p": 0.9,
      "max_tokens": 1000,
      "system_prompt": "You are a helpful restaurant reservation assistant..."
    },
    "mistral:7b": {
      "temperature": 0.2,
      "top_p": 0.8,
      "max_tokens": 800,
      "system_prompt": "Help customers with restaurant reservations..."
    }
  }
}
```

### Implementation Approach

#### MCP Client for Ollama
```python
# ollama_client.py
import ollama
from typing import Dict, Any, List

class OllamaMCPClient:
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.mcp_tools = self._load_mcp_tools()
    
    async def chat_with_tools(self, message: str, conversation_history: List[Dict]):
        """Chat with Ollama model using MCP tools"""
        response = ollama.chat(
            model=self.model_name,
            messages=conversation_history + [{"role": "user", "content": message}],
            tools=self.mcp_tools,
            options={
                "temperature": 0.1,
                "top_p": 0.9
            }
        )
        return response
```

#### Integration Architecture
```
Customer Chat Interface
        ↓
Ollama Model (Local)
        ↓
MCP Server (Restaurant Tools)
        ↓
RMS Backend API
        ↓
Database
```

### Ollama-Specific Features

#### 1. Local Model Management
- **Model Selection:** Dynamic model switching based on task complexity
- **Resource Optimization:** Automatic model loading/unloading
- **Performance Monitoring:** Track inference times and accuracy

#### 2. Custom Fine-Tuning
- **Restaurant Vocabulary:** Train on restaurant-specific terminology
- **Conversation Patterns:** Optimize for reservation workflows
- **Multi-Language Support:** Support for local languages

#### 3. Offline Operation
- **Local Processing:** Complete functionality without internet
- **Data Privacy:** All conversations stay on-premises
- **Sync Capability:** Batch sync when connectivity returns

### Deployment Options with Ollama

#### Option 1: Restaurant Kiosk
- **Hardware:** Local machine with GPU for faster inference
- **Interface:** Touch screen for customer interaction
- **Integration:** Direct connection to restaurant's RMS system

#### Option 2: Staff Assistant
- **Purpose:** Help staff manage reservations via natural language
- **Interface:** Web-based chat or voice interface
- **Capabilities:** Complex queries, reporting, schedule management

#### Option 3: Customer Mobile App
- **Deployment:** Ollama running on restaurant's server
- **Access:** Mobile app connects to local Ollama instance
- **Features:** Voice reservations, menu questions, order status

### Performance Considerations

#### Hardware Requirements
- **Minimum:** 8GB RAM, CPU-only (Mistral 7B)
- **Recommended:** 16GB RAM, RTX 3060+ GPU (Llama 3.1 8B)
- **Optimal:** 32GB RAM, RTX 4090 GPU (Llama 3.1 70B)

#### Response Time Targets
- **Simple Queries:** <1 second (availability check)
- **Complex Reservations:** <3 seconds (multi-step booking)
- **Conversation Context:** <500ms (follow-up questions)

### Ollama Integration Roadmap

#### Phase 1A: Basic Integration (2 weeks)
- [ ] MCP client for Ollama
- [ ] Basic reservation tools integration
- [ ] Simple conversation flows
- [ ] Performance benchmarking

#### Phase 1B: Enhanced Features (2 weeks)
- [ ] Multi-model support
- [ ] Conversation memory
- [ ] Error handling and fallbacks
- [ ] Voice interface support

#### Phase 1C: Production Ready (1 week)
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Monitoring and logging
- [ ] Deployment documentation

## Next Phases (Future Planning)

### Phase 2: Menu & Ordering System
- Menu browsing tools
- Order creation and management
- Payment processing integration
- Order status tracking

### Phase 3: Enhanced Features
- Customer preferences and history
- Loyalty program integration
- Special events and promotions
- Waitlist management

### Phase 4: Advanced AI Capabilities
- Natural language menu recommendations
- Dietary restriction handling
- Automated scheduling optimization
- Predictive availability suggestions

## Success Metrics
- **Functional:** 100% of reservation workflows supported
- **Performance:** <2 second response times for all operations
- **Reliability:** 99.9% uptime and error-free operation
- **Usability:** Natural conversation flows with AI assistants
- **Security:** Zero data breaches or unauthorized access

## Timeline Estimate
- **Setup & Planning:** 1 week
- **Core Development:** 3 weeks
- **Testing & Integration:** 2 weeks
- **Documentation & Deployment:** 1 week
- **Total Phase 1 Duration:** 7 weeks