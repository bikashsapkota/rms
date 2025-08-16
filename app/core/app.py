from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.modules.auth.routes import router as auth_router, users_router
from app.modules.menu.routes.categories import router as categories_router
from app.modules.menu.routes.items import router as items_router, public_router
from app.modules.setup.routes import router as setup_router


def create_application() -> FastAPI:
    """Create FastAPI application."""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files
    if settings.upload_path.exists():
        app.mount("/uploads", StaticFiles(directory=str(settings.upload_path)), name="uploads")
    
    # Include routers
    app.include_router(setup_router, tags=["Setup"])  # No prefix for setup routes
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(users_router, prefix=settings.API_V1_STR)
    app.include_router(categories_router, prefix=settings.API_V1_STR)
    app.include_router(items_router, prefix=settings.API_V1_STR)
    app.include_router(public_router, prefix=settings.API_V1_STR)
    
    
    return app