from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

# Core imports
from core import settings, pos_engine, admin_engine, AppBase, AdminBase, setup_logging
from middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler
)

# API route imports
from app.user_login import router as user_login_router
from app.user_crud import router as user_crud_router
from app.clients import router as client_router
from app.tickets import router as tickets_router
from app.packages import router as packages_router

# Setup logging
setup_logging()

# Initialize database tables
AppBase.metadata.create_all(bind=pos_engine)
AdminBase.metadata.create_all(bind=admin_engine)

# Create FastAPI app with enhanced OpenAPI documentation
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Admin Server API
    
    Administrative server API for managing users, clients, tickets, packages, and subscriptions.
    
    ### Features
    - **User Management**: Admin user authentication, creation, updates, and management
    - **Client Management**: Customer information, subscriptions, and settings
    - **Ticket System**: Support ticket creation, tracking, and updates
    - **Package Management**: Subscription package management
    - **Update Tracking**: Tracking and sending updates to client devices
    
    ### Authentication
    All endpoints (except login) require:
    - **Bearer Token**: In the Authorization header (`Authorization: Bearer <token>`)
    - **User ID**: Via `X-User-Id` header (recommended) or `user_id` query parameter
    
    To get credentials, use the login endpoint: `/admin-api/login/admin_login`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    tags_metadata=[
        {
            "name": "Admin User Account",
            "description": "User authentication and login"
        },
        {
            "name": "User CRUD Account",
            "description": "User management operations"
        },
        {
            "name": "Account",
            "description": "Client/customer management"
        },
        {
            "name": "Ticket CRUD Operations",
            "description": "Support ticket management"
        },
        {
            "name": "Package",
            "description": "Subscription package management"
        },
    ]
)

# Configure OpenAPI security scheme for Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Ensure components section exists
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    # Initialize securitySchemes - merge with any existing ones from FastAPI auto-detection
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}
    
    # Add/update Bearer token security scheme
    # This will be used by Swagger UI for the "Authorize" button
    # The name "Bearer" must match what we use in operation["security"]
    openapi_schema["components"]["securitySchemes"]["Bearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "token",
        "description": "Enter your bearer token (without 'Bearer' prefix). Get token from /admin-api/login/admin_login"
    }
    
    # Remove any auto-detected APIKeyHeader schemes that might have been created
    # We'll add our own UserId scheme manually to avoid duplicates
    schemes_to_remove = []
    for scheme_name, scheme_def in openapi_schema["components"]["securitySchemes"].items():
        if (scheme_def.get("type") == "apiKey" and 
            scheme_def.get("in") == "header" and 
            scheme_def.get("name") == "X-User-Id" and
            scheme_name != "UserId"):
            schemes_to_remove.append(scheme_name)
        # Remove OAuth2PasswordBearer schemes
        elif scheme_def.get("type") == "oauth2":
            schemes_to_remove.append(scheme_name)
    
    for scheme_name in schemes_to_remove:
        del openapi_schema["components"]["securitySchemes"][scheme_name]
    
    # Add UserId security scheme manually (to avoid duplicates from auto-detection)
    openapi_schema["components"]["securitySchemes"]["UserId"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-User-Id",
        "description": "User ID for authentication. Enter your user ID (integer). Get this from /admin-api/login/admin_login"
    }
    
    # Add security to all endpoints except login and root
    # This will make the "Authorize" button appear in Swagger UI
    excluded_paths = ["/admin-api/login/admin_login", "/", "/health"]
    
    for path, path_item in openapi_schema.get("paths", {}).items():
        # Skip excluded paths
        if any(path.startswith(excluded) for excluded in excluded_paths):
            continue
            
        for method, operation in path_item.items():
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                # Add security requirement to all endpoints (except excluded ones)
                # This ensures Swagger UI shows the lock icon and allows authorization
                # Include both Bearer token and UserId in the same security requirement
                # This makes both appear together in the Authorize dialog
                operation["security"] = [{"Bearer": [], "UserId": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/", tags=["Root"])
def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }

# CORS middleware with configuration from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

#-------------------------------------- Routes ---------------------------------------------

app.include_router(user_login_router)
app.include_router(user_crud_router)
app.include_router(client_router)
app.include_router(tickets_router)
app.include_router(packages_router)
