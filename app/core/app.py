from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.shared.cache import cache_service
from app.modules.auth.routes import router as auth_router, users_router
from app.modules.menu.routes.categories import router as categories_router
from app.modules.menu.routes.items import router as items_router, public_router as menu_public_router
from app.modules.menu.routes.modifiers import router as modifiers_router
from app.modules.platform.routes.applications import router as platform_router
from app.modules.setup.routes import router as setup_router
from app.modules.tables.routes.tables import router as tables_router
from app.modules.tables.routes.reservations import router as reservations_router
from app.modules.tables.routes.availability import router as availability_router
from app.modules.tables.routes.waitlist import router as waitlist_router
from app.modules.tables.routes.public import router as reservations_public_router
# Phase 3 orders module (now enabled for testing)
from app.modules.orders.routes.orders import router as orders_router
from app.modules.orders.routes.kitchen import router as kitchen_router
from app.modules.orders.routes.payments import router as payments_router
from app.modules.orders.routes.qr_orders import router as qr_orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    await cache_service.initialize()
    yield
    # Shutdown
    await cache_service.close()


def create_application() -> FastAPI:
    """Create FastAPI application."""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )
    
    # Add CORS middleware with explicit origins to allow credentials
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8080", 
            "http://localhost:5173"
        ],
        allow_credentials=True,  # Allow cookies/auth headers
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
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
    app.include_router(modifiers_router, prefix=settings.API_V1_STR)
    app.include_router(menu_public_router, prefix=settings.API_V1_STR)
    app.include_router(platform_router, prefix=settings.API_V1_STR)
    
    # Phase 2: Table and Reservation Management
    app.include_router(tables_router, prefix=settings.API_V1_STR)
    app.include_router(reservations_router, prefix=settings.API_V1_STR)
    app.include_router(availability_router, prefix=settings.API_V1_STR)
    app.include_router(waitlist_router, prefix=settings.API_V1_STR)
    app.include_router(reservations_public_router, prefix=settings.API_V1_STR)
    
    # Phase 3: Order Management & Kitchen Operations (now enabled)
    app.include_router(orders_router, prefix=settings.API_V1_STR)
    app.include_router(kitchen_router, prefix=settings.API_V1_STR)
    app.include_router(payments_router, prefix=settings.API_V1_STR)
    app.include_router(qr_orders_router, prefix=settings.API_V1_STR)
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "Restaurant Management System"}
    
    # Cache lifecycle is now handled by lifespan context manager
    
    return app


# Create the app instance
app = create_application()