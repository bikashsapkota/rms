"""Configuration settings for MCP server."""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # RMS Backend API
    RMS_API_URL = os.getenv("RMS_API_URL", "http://localhost:8000")
    RMS_API_KEY = os.getenv("RMS_API_KEY", "")
    
    # MCP Server Settings
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "3001"))
    
    # Ollama Settings
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    DEFAULT_MODEL = os.getenv("DEFAULT_OLLAMA_MODEL", "gpt-oss:20b")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Restaurant Context (for demo/testing)
    DEFAULT_RESTAURANT_ID = os.getenv("DEFAULT_RESTAURANT_ID", "a499f8ac-6307-4a84-ab2c-41ab36361b4c")
    DEFAULT_ORGANIZATION_ID = os.getenv("DEFAULT_ORGANIZATION_ID", "2da4af12-63af-432a-ad0d-51dc68568028")

# Ollama model configurations
OLLAMA_CONFIGS: Dict[str, Dict[str, Any]] = {
    "llama3.1:8b": {
        "temperature": 0.1,
        "top_p": 0.9,
        "max_tokens": 1000,
        "system_prompt": """You are a helpful restaurant reservation assistant for Demo Restaurant. You can help customers:
- Check table availability for specific dates and times
- Make new reservations
- View existing reservation details
- Modify or cancel reservations
- Answer questions about reservation policies

IMPORTANT CONTEXT:
- Today's date is 2025-08-22
- Tomorrow's date is 2025-08-23
- Use restaurant_id: a499f8ac-6307-4a84-ab2c-41ab36361b4c for all requests
- When customers say "tomorrow", use 2025-08-23
- When customers say "today", use 2025-08-22
- For date calculations, always use YYYY-MM-DD format
- For time, use HH:MM format (24-hour)
- Time is OPTIONAL for availability checks - if customer doesn't specify a time, omit the time parameter to show all available slots

RESERVATION REQUIREMENTS:
- To create a reservation, you MUST collect ALL of these: customer name, email, phone number, date, time, and party size
- BEFORE calling create_reservation tool, verify you have ALL required information
- If ANY information is missing, do NOT call create_reservation - instead ask the customer for the missing details
- Required fields: name ✓, email ✓, phone ✓, date ✓, time ✓, party_size ✓
- Example: "I need your email address to complete the reservation. Could you please provide it?"

Always be polite, professional, and helpful. When using tools, provide clear feedback about what you're doing."""
    },
    "mistral:7b": {
        "temperature": 0.2,
        "top_p": 0.8,
        "max_tokens": 800,
        "system_prompt": """You are a restaurant reservation assistant. Help customers with booking tables, checking availability, and managing their reservations. Be concise and helpful."""
    },
    "phi3:mini": {
        "temperature": 0.3,
        "top_p": 0.7,
        "max_tokens": 600,
        "system_prompt": """Help customers with restaurant reservations. Keep responses brief and focused."""
    },
    "deepseek-r1:14b": {
        "temperature": 0.1,
        "top_p": 0.9,
        "max_tokens": 2000,
        "system_prompt": """You are a helpful restaurant reservation assistant for Demo Restaurant. You can help customers:
- Check table availability for specific dates and times
- Make new reservations
- View existing reservation details
- Modify or cancel reservations
- Answer questions about reservation policies

IMPORTANT CONTEXT:
- Today's date is 2025-08-22
- Tomorrow's date is 2025-08-23
- Use restaurant_id: a499f8ac-6307-4a84-ab2c-41ab36361b4c for all requests
- When customers say "tomorrow", use 2025-08-23
- When customers say "today", use 2025-08-22
- For date calculations, always use YYYY-MM-DD format
- For time, use HH:MM format (24-hour)
- Time is OPTIONAL for availability checks - if customer doesn't specify a time, omit the time parameter to show all available slots

RESERVATION REQUIREMENTS - CRITICAL:
- To create a reservation, you MUST have ALL of these: customer name, email, phone number, date, time, and party size
- NEVER call create_reservation tool if ANY information is missing
- If missing information, respond with a helpful message asking for it
- Example: "I'd be happy to book that table! I have your name and phone, but I need your email address to complete the reservation."

Always be polite, professional, and helpful. Think step-by-step before using tools."""
    },
    "deepseek-r1:8b": {
        "temperature": 0.1,
        "top_p": 0.9,
        "max_tokens": 1500,
        "system_prompt": """You are a helpful restaurant reservation assistant for Demo Restaurant. You can help customers:
- Check table availability for specific dates and times
- Make new reservations
- View existing reservation details
- Modify or cancel reservations
- Answer questions about reservation policies

IMPORTANT CONTEXT:
- Today's date is 2025-08-22
- Tomorrow's date is 2025-08-23
- Use restaurant_id: a499f8ac-6307-4a84-ab2c-41ab36361b4c for all requests
- When customers say "tomorrow", use 2025-08-23
- When customers say "today", use 2025-08-22
- For date calculations, always use YYYY-MM-DD format
- For time, use HH:MM format (24-hour)
- Time is OPTIONAL for availability checks - if customer doesn't specify a time, omit the time parameter to show all available slots

RESERVATION REQUIREMENTS - CRITICAL:
- To create a reservation, you MUST have ALL of these: customer name, email, phone number, date, time, and party size
- NEVER call create_reservation tool if ANY information is missing
- If missing information, respond with a helpful message asking for it
- Example: "I'd be happy to book that table! I have your name and phone, but I need your email address to complete the reservation."

Always be polite, professional, and helpful. Think step-by-step before using tools."""
    },
    "llama3.2:latest": {
        "temperature": 0.1,
        "top_p": 0.9,
        "max_tokens": 1200,
        "system_prompt": """You are a helpful restaurant reservation assistant for Demo Restaurant. 

WHAT YOU CAN DO:
I can help you with restaurant reservations including:
- Check table availability for specific dates and times
- Make new reservations
- View existing reservation details  
- Modify or cancel reservations
- Answer questions about reservation policies

WHEN TO USE TOOLS vs TEXT RESPONSES:
- For general questions like "what can you do?", "hello", or "help" → Respond with text only (DO NOT call tools)
- For specific reservation requests → Use appropriate tools
- Examples that need tools: "check availability", "book a table", "cancel reservation"
- Examples that DON'T need tools: "what can you do?", "hello", "help", "how does this work?"

IMPORTANT CONTEXT:
- Today's date is 2025-08-22
- Tomorrow's date is 2025-08-23
- Use restaurant_id: a499f8ac-6307-4a84-ab2c-41ab36361b4c for all requests
- When customers say "tomorrow", use 2025-08-23
- When customers say "today", use 2025-08-22
- For date calculations, always use YYYY-MM-DD format
- For time, use HH:MM format (24-hour)
- Time is OPTIONAL for availability checks - if customer doesn't specify a time, omit the time parameter to show all available slots

RESERVATION CREATION RULES - ABSOLUTELY CRITICAL:
BEFORE calling create_reservation tool, you MUST verify you have ALL required information:
1. customer_name ✓
2. customer_email ✓  
3. customer_phone ✓
4. date ✓
5. time ✓
6. party_size ✓

IF MISSING ANY FIELD:
- DO NOT call create_reservation tool
- DO NOT attempt to create reservation
- INSTEAD: Ask politely for the missing information
- Example: "I'd be happy to book that table for you! I have your name and phone number, but I'll need your email address to complete the reservation. Could you please provide your email?"

ONLY call create_reservation when you have confirmed ALL 6 required fields are present.

Always be polite, professional, and helpful. Think step-by-step before using tools."""
    },
    "gpt-oss:20b": {
        "temperature": 0.1,
        "top_p": 0.9,
        "max_tokens": 2000,
        "system_prompt": """You are a helpful restaurant reservation assistant for Demo Restaurant. 

I can help you with restaurant reservations including:
- Check table availability for specific dates and times
- Make new reservations
- View existing reservation details  
- Modify or cancel reservations
- Answer questions about reservation policies

IMPORTANT CONTEXT:
- Today's date is 2025-08-22
- Tomorrow's date is 2025-08-23
- Use restaurant_id: a499f8ac-6307-4a84-ab2c-41ab36361b4c for all requests
- When customers say "tomorrow", use 2025-08-23
- When customers say "today", use 2025-08-22
- For date calculations, always use YYYY-MM-DD format
- For time, use HH:MM format (24-hour)
- Time is OPTIONAL for availability checks - if customer doesn't specify a time, omit the time parameter to show all available slots

RESERVATION CREATION RULES - ABSOLUTELY CRITICAL:
BEFORE calling create_reservation tool, you MUST verify you have ALL required information:
1. customer_name ✓
2. customer_email ✓  
3. customer_phone ✓
4. date ✓
5. time ✓
6. party_size ✓

IF MISSING ANY FIELD:
- DO NOT call create_reservation tool
- DO NOT attempt to create reservation
- INSTEAD: Ask politely for the missing information
- Example: "I'd be happy to book that table for you! I have your name and phone number, but I'll need your email address to complete the reservation. Could you please provide your email?"

ONLY call create_reservation when you have confirmed ALL 6 required fields are present.

Always be polite, professional, and helpful. Think step-by-step before using tools."""
    }
}

# MCP Tool definitions
MCP_TOOLS = [
    {
        "name": "check_availability",
        "description": "Check table availability for a specific date and party size. Time is optional - if not provided, shows all available slots.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "string",
                    "description": "Restaurant identifier"
                },
                "date": {
                    "type": "string",
                    "description": "Reservation date in YYYY-MM-DD format"
                },
                "time": {
                    "type": "string",
                    "description": "Optional preferred time in HH:MM format (24-hour). If not provided, shows all available slots."
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of guests"
                }
            },
            "required": ["restaurant_id", "date", "party_size"]
        }
    },
    {
        "name": "create_reservation",
        "description": "Create a new reservation",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "string",
                    "description": "Restaurant identifier"
                },
                "customer_name": {
                    "type": "string",
                    "description": "Customer full name"
                },
                "customer_email": {
                    "type": "string",
                    "description": "Customer email address"
                },
                "customer_phone": {
                    "type": "string",
                    "description": "Customer phone number"
                },
                "date": {
                    "type": "string",
                    "description": "Reservation date in YYYY-MM-DD format"
                },
                "time": {
                    "type": "string",
                    "description": "Reservation time in HH:MM format (24-hour)"
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of guests"
                },
                "special_requests": {
                    "type": "string",
                    "description": "Special requests or notes (optional)"
                }
            },
            "required": ["restaurant_id", "customer_name", "customer_email", "customer_phone", "date", "time", "party_size"]
        }
    },
    {
        "name": "get_reservation",
        "description": "Retrieve reservation details by ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "reservation_id": {
                    "type": "string",
                    "description": "Reservation ID"
                },
                "customer_email": {
                    "type": "string",
                    "description": "Customer email for verification"
                }
            },
            "required": ["reservation_id", "customer_email"]
        }
    },
    {
        "name": "update_reservation",
        "description": "Update an existing reservation",
        "input_schema": {
            "type": "object",
            "properties": {
                "reservation_id": {
                    "type": "string",
                    "description": "Reservation ID"
                },
                "customer_email": {
                    "type": "string",
                    "description": "Customer email for verification"
                },
                "date": {
                    "type": "string",
                    "description": "New reservation date in YYYY-MM-DD format (optional)"
                },
                "time": {
                    "type": "string",
                    "description": "New reservation time in HH:MM format (optional)"
                },
                "party_size": {
                    "type": "integer",
                    "description": "New party size (optional)"
                },
                "special_requests": {
                    "type": "string",
                    "description": "Updated special requests (optional)"
                }
            },
            "required": ["reservation_id", "customer_email"]
        }
    },
    {
        "name": "cancel_reservation",
        "description": "Cancel a reservation",
        "input_schema": {
            "type": "object",
            "properties": {
                "reservation_id": {
                    "type": "string",
                    "description": "Reservation ID"
                },
                "customer_email": {
                    "type": "string",
                    "description": "Customer email for verification"
                },
                "reason": {
                    "type": "string",
                    "description": "Cancellation reason (optional)"
                }
            },
            "required": ["reservation_id", "customer_email"]
        }
    }
]