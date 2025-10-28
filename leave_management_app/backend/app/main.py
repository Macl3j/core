"""Main FastAPI application for Leave Management System."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from .database import init_db, engine, get_db
from .routers import auth, users, leaves
from .models import User, UserRole
from .auth import get_password_hash
from sqlalchemy.orm import Session

# Create FastAPI application
app = FastAPI(
    title="Leave Management System",
    description="A comprehensive leave management system for organizations",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(leaves.router, prefix="/api")


@app.on_event("startup")
def startup_event():
    """Initialize database and create default admin user on startup."""
    # Create database tables
    init_db()

    # Create default admin user if no users exist
    db = next(get_db())
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            print("Creating default admin user...")
            admin_user = User(
                email="admin@example.com",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                annual_leave_days=25.0,
                sick_leave_days=10.0,
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created:")
            print("  Username: admin")
            print("  Password: admin123")
            print("  Please change the password after first login!")
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Leave Management System is running"}


@app.get("/api")
def root():
    """Root API endpoint."""
    return {
        "message": "Welcome to Leave Management System API",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    def serve_frontend():
        """Serve the frontend index.html."""
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not found. Please check frontend directory."}

    @app.get("/login")
    def serve_login():
        """Serve the login page."""
        login_path = os.path.join(frontend_path, "login.html")
        if os.path.exists(login_path):
            return FileResponse(login_path)
        return {"message": "Login page not found"}

    @app.get("/dashboard")
    def serve_dashboard():
        """Serve the dashboard page."""
        dashboard_path = os.path.join(frontend_path, "dashboard.html")
        if os.path.exists(dashboard_path):
            return FileResponse(dashboard_path)
        return {"message": "Dashboard page not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
