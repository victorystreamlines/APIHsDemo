"""Main FastAPI application."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from user_management.api.auth import router as auth_router
from user_management.api.users import router as users_router
from user_management.core.config import settings
from user_management.database.base import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("🚀 User Management System started successfully!")
    
    yield
    
    # Shutdown
    print("👋 User Management System shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="""
    # 🧬 User Management System API
    
    A modern, production-ready user management system built with:
    
    * **FastAPI** - High performance, easy to learn, fast to code, ready for production
    * **SQLAlchemy** - The Database Toolkit for Python
    * **SQLite** - Lightweight, reliable SQL database
    * **JWT Authentication** - Secure token-based authentication
    * **Pagination & Search** - Efficient data retrieval with full-text search
    * **Comprehensive Testing** - 85%+ test coverage
    * **Modern Python** - Type hints, async/await, Pydantic models
    
    ## 🔐 Authentication
    
    Most endpoints require authentication. Use the `/auth/login` endpoint to get a JWT token.
    
    **Demo Credentials:**
    - Username: `admin`, Password: `admin123`
    - Username: `demo`, Password: `demo123`  
    - Username: `user`, Password: `user123`
    
    ## 📊 Features
    
    * **CRUD Operations** - Create, Read, Update, Delete users
    * **Search & Filter** - Case-insensitive search across name, email, and phone
    * **Pagination** - Efficient handling of large datasets
    * **Sorting** - Sort by any field in ascending or descending order
    * **Validation** - Comprehensive input validation with detailed error messages
    * **Statistics** - User count and activity metrics
    
    ## 🛡️ Security
    
    * JWT token-based authentication
    * Password hashing with bcrypt
    * Input validation and sanitization
    * CORS protection
    * Rate limiting ready
    
    ---
    
    **Created by Genetic Invent** 🧬
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom middleware for request timing and logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header and basic request logging."""
    start_time = time.time()
    
    # Log request
    print(f"📥 {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Calculate and add processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:.4f}")
    
    # Log response
    print(f"📤 {request.method} {request.url.path} - {response.status_code} ({process_time:.4f}s)")
    
    return response


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Endpoint not found",
            "detail": f"The endpoint {request.url.path} was not found",
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
        "timestamp": time.time(),
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_name} API!",
        "version": settings.version,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/health",
        "authentication": {
            "login_endpoint": "/api/v1/auth/login",
            "demo_users_endpoint": "/api/v1/auth/demo-users",
        },
        "users_endpoint": "/api/v1/users",
    }


# Include routers
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(users_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "user_management.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )