"""
Restaurant Management System - Phase 1
Main application entry point.
"""

from app.core.app import create_application

# Create FastAPI application
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )