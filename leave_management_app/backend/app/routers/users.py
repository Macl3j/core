"""Users router for user management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserRole
from ..schemas import UserResponse, UserUpdate, UserLeaveStats, LeaveBalanceResponse
from ..auth import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))
):
    """Get all users (managers and admins only)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return current_user


@router.get("/me/stats", response_model=UserLeaveStats)
def get_current_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's leave statistics."""
    from datetime import datetime
    from ..models import LeaveRequest, LeaveStatus

    current_year = datetime.now().year

    # Count pending requests
    pending_count = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == current_user.id,
        LeaveRequest.status == LeaveStatus.PENDING
    ).count()

    # Count approved leaves this year
    approved_this_year = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == current_user.id,
        LeaveRequest.status == LeaveStatus.APPROVED,
        LeaveRequest.start_date >= datetime(current_year, 1, 1)
    ).count()

    # Count upcoming approved leaves
    upcoming_leaves = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == current_user.id,
        LeaveRequest.status == LeaveStatus.APPROVED,
        LeaveRequest.start_date >= datetime.now()
    ).count()

    # Calculate used days for annual leave
    used_annual_days = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == current_user.id,
        LeaveRequest.status == LeaveStatus.APPROVED,
        LeaveRequest.leave_type == "annual",
        LeaveRequest.start_date >= datetime(current_year, 1, 1)
    ).with_entities(LeaveRequest.days_count).all()

    total_used_annual = sum([days[0] for days in used_annual_days]) if used_annual_days else 0

    # Calculate used days for sick leave
    used_sick_days = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == current_user.id,
        LeaveRequest.status == LeaveStatus.APPROVED,
        LeaveRequest.leave_type == "sick",
        LeaveRequest.start_date >= datetime(current_year, 1, 1)
    ).with_entities(LeaveRequest.days_count).all()

    total_used_sick = sum([days[0] for days in used_sick_days]) if used_sick_days else 0

    return UserLeaveStats(
        user_id=current_user.id,
        annual_leave_remaining=current_user.annual_leave_days - total_used_annual,
        sick_leave_remaining=current_user.sick_leave_days - total_used_sick,
        pending_requests=pending_count,
        approved_leaves_this_year=approved_this_year,
        upcoming_leaves=upcoming_leaves
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user by ID."""
    # Users can view their own profile, managers and admins can view anyone
    if current_user.id != user_id and current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a user's information."""
    # Users can update their own non-privileged fields, admins can update anyone
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions
    is_self_update = current_user.id == user_id
    is_admin = current_user.role == UserRole.ADMIN

    if not is_self_update and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    # Update fields
    update_data = user_update.dict(exclude_unset=True)

    # Only admins can change role, leave days, and active status
    if not is_admin:
        restricted_fields = ["role", "annual_leave_days", "sick_leave_days", "is_active", "manager_id"]
        for field in restricted_fields:
            if field in update_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not authorized to update {field}"
                )

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Delete a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    db.delete(user)
    db.commit()

    return None


@router.get("/{user_id}/subordinates", response_model=List[UserResponse])
def get_subordinates(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all subordinates of a user (for managers)."""
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view subordinates"
        )

    subordinates = db.query(User).filter(User.manager_id == user_id).all()
    return subordinates
