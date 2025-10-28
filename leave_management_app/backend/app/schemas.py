"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from .models import LeaveStatus, LeaveType, UserRole


# User schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    department: Optional[str] = None
    role: UserRole = UserRole.EMPLOYEE


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=6)
    manager_id: Optional[int] = None
    annual_leave_days: float = 20.0
    sick_leave_days: float = 10.0


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[UserRole] = None
    manager_id: Optional[int] = None
    annual_leave_days: Optional[float] = None
    sick_leave_days: Optional[float] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    manager_id: Optional[int]
    annual_leave_days: float
    sick_leave_days: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[int] = None
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


# Leave request schemas
class LeaveRequestBase(BaseModel):
    """Base leave request schema."""
    leave_type: LeaveType
    start_date: datetime
    end_date: datetime
    reason: Optional[str] = None


class LeaveRequestCreate(LeaveRequestBase):
    """Schema for creating a leave request."""
    pass


class LeaveRequestUpdate(BaseModel):
    """Schema for updating a leave request."""
    leave_type: Optional[LeaveType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    reason: Optional[str] = None


class LeaveRequestResponse(LeaveRequestBase):
    """Schema for leave request response."""
    id: int
    user_id: int
    days_count: float
    status: LeaveStatus
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Nested user information
    user: Optional[UserResponse] = None
    approver: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class LeaveRequestApprove(BaseModel):
    """Schema for approving a leave request."""
    approved: bool
    rejection_reason: Optional[str] = None


# Leave balance schemas
class LeaveBalanceResponse(BaseModel):
    """Schema for leave balance response."""
    id: int
    user_id: int
    year: int
    leave_type: LeaveType
    total_days: float
    used_days: float
    remaining_days: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dashboard schemas
class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""
    total_employees: int
    pending_requests: int
    approved_requests: int
    rejected_requests: int


class UserLeaveStats(BaseModel):
    """Schema for user leave statistics."""
    user_id: int
    annual_leave_remaining: float
    sick_leave_remaining: float
    pending_requests: int
    approved_leaves_this_year: int
    upcoming_leaves: int
