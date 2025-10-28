"""Leave requests router for managing leave requests."""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from ..database import get_db
from ..models import LeaveRequest, LeaveStatus, LeaveType, User, UserRole
from ..schemas import (
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveRequestUpdate,
    LeaveRequestApprove,
    DashboardStats,
)
from ..auth import get_current_user, require_role

router = APIRouter(prefix="/leaves", tags=["Leave Requests"])


def calculate_days(start_date: datetime, end_date: datetime) -> float:
    """Calculate number of working days between two dates."""
    if start_date > end_date:
        raise ValueError("Start date must be before end date")

    # Simple calculation: count all days (including weekends)
    # In production, you'd want to exclude weekends and holidays
    delta = end_date - start_date
    days = delta.days + 1  # +1 to include both start and end date

    return float(days)


@router.post("/", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
def create_leave_request(
    leave_data: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new leave request."""
    # Validate dates
    if leave_data.start_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot request leave in the past"
        )

    if leave_data.start_date > leave_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before or equal to end date"
        )

    # Calculate days
    try:
        days_count = calculate_days(leave_data.start_date, leave_data.end_date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Check for overlapping leave requests
    overlapping = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == current_user.id,
        LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
        or_(
            and_(
                LeaveRequest.start_date <= leave_data.start_date,
                LeaveRequest.end_date >= leave_data.start_date
            ),
            and_(
                LeaveRequest.start_date <= leave_data.end_date,
                LeaveRequest.end_date >= leave_data.end_date
            ),
            and_(
                LeaveRequest.start_date >= leave_data.start_date,
                LeaveRequest.end_date <= leave_data.end_date
            )
        )
    ).first()

    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a leave request for overlapping dates"
        )

    # Check leave balance for annual and sick leave
    current_year = datetime.now().year
    if leave_data.leave_type in [LeaveType.ANNUAL, LeaveType.SICK]:
        used_days = db.query(LeaveRequest).filter(
            LeaveRequest.user_id == current_user.id,
            LeaveRequest.status == LeaveStatus.APPROVED,
            LeaveRequest.leave_type == leave_data.leave_type,
            LeaveRequest.start_date >= datetime(current_year, 1, 1)
        ).all()

        total_used = sum([req.days_count for req in used_days])

        if leave_data.leave_type == LeaveType.ANNUAL:
            available = current_user.annual_leave_days - total_used
        else:  # SICK
            available = current_user.sick_leave_days - total_used

        if days_count > available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient leave balance. Available: {available} days, Requested: {days_count} days"
            )

    # Create leave request
    new_request = LeaveRequest(
        user_id=current_user.id,
        leave_type=leave_data.leave_type,
        start_date=leave_data.start_date,
        end_date=leave_data.end_date,
        days_count=days_count,
        reason=leave_data.reason,
        status=LeaveStatus.PENDING
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


@router.get("/", response_model=List[LeaveRequestResponse])
def get_leave_requests(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[LeaveStatus] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get leave requests. Regular users see their own, managers see their team's, admins see all."""
    query = db.query(LeaveRequest)

    # Apply role-based filtering
    if current_user.role == UserRole.EMPLOYEE:
        # Employees can only see their own requests
        query = query.filter(LeaveRequest.user_id == current_user.id)
    elif current_user.role == UserRole.MANAGER:
        # Managers see their subordinates' requests and their own
        subordinate_ids = [sub.id for sub in current_user.subordinates]
        subordinate_ids.append(current_user.id)
        query = query.filter(LeaveRequest.user_id.in_(subordinate_ids))
    # Admins see all requests (no filter)

    # Apply optional filters
    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)

    if user_id:
        # Check if current user has permission to view this user's requests
        if current_user.role == UserRole.EMPLOYEE and user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view other users' requests"
            )
        query = query.filter(LeaveRequest.user_id == user_id)

    requests = query.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit).all()

    return requests


@router.get("/my", response_model=List[LeaveRequestResponse])
def get_my_leave_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's leave requests."""
    requests = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == current_user.id
    ).order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit).all()

    return requests


@router.get("/pending", response_model=List[LeaveRequestResponse])
def get_pending_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))
):
    """Get pending leave requests for approval (managers and admins only)."""
    query = db.query(LeaveRequest).filter(LeaveRequest.status == LeaveStatus.PENDING)

    # Managers only see their subordinates' requests
    if current_user.role == UserRole.MANAGER:
        subordinate_ids = [sub.id for sub in current_user.subordinates]
        query = query.filter(LeaveRequest.user_id.in_(subordinate_ids))

    requests = query.order_by(LeaveRequest.created_at.asc()).offset(skip).limit(limit).all()

    return requests


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))
):
    """Get dashboard statistics (managers and admins only)."""
    # For managers, filter by their subordinates
    if current_user.role == UserRole.MANAGER:
        subordinate_ids = [sub.id for sub in current_user.subordinates]
        total_employees = len(subordinate_ids)

        pending = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.PENDING,
            LeaveRequest.user_id.in_(subordinate_ids)
        ).count()

        approved = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.APPROVED,
            LeaveRequest.user_id.in_(subordinate_ids)
        ).count()

        rejected = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.REJECTED,
            LeaveRequest.user_id.in_(subordinate_ids)
        ).count()
    else:
        # Admin sees all
        total_employees = db.query(User).count()
        pending = db.query(LeaveRequest).filter(LeaveRequest.status == LeaveStatus.PENDING).count()
        approved = db.query(LeaveRequest).filter(LeaveRequest.status == LeaveStatus.APPROVED).count()
        rejected = db.query(LeaveRequest).filter(LeaveRequest.status == LeaveStatus.REJECTED).count()

    return DashboardStats(
        total_employees=total_employees,
        pending_requests=pending,
        approved_requests=approved,
        rejected_requests=rejected
    )


@router.get("/{request_id}", response_model=LeaveRequestResponse)
def get_leave_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific leave request."""
    request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Check permissions
    is_owner = request.user_id == current_user.id
    is_manager_of_requester = current_user.role == UserRole.MANAGER and request.user.manager_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if not (is_owner or is_manager_of_requester or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this request"
        )

    return request


@router.put("/{request_id}", response_model=LeaveRequestResponse)
def update_leave_request(
    request_id: int,
    update_data: LeaveRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a leave request (only pending requests can be updated by the owner)."""
    request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Only the owner can update their request
    if request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this request"
        )

    # Can only update pending requests
    if request.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update pending requests"
        )

    # Update fields
    update_dict = update_data.dict(exclude_unset=True)

    # Recalculate days if dates changed
    if "start_date" in update_dict or "end_date" in update_dict:
        start = update_dict.get("start_date", request.start_date)
        end = update_dict.get("end_date", request.end_date)
        update_dict["days_count"] = calculate_days(start, end)

    for key, value in update_dict.items():
        setattr(request, key, value)

    db.commit()
    db.refresh(request)

    return request


@router.post("/{request_id}/approve", response_model=LeaveRequestResponse)
def approve_leave_request(
    request_id: int,
    approval_data: LeaveRequestApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))
):
    """Approve or reject a leave request (managers and admins only)."""
    request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Can only approve/reject pending requests
    if request.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only approve/reject pending requests"
        )

    # Check if manager is authorized (must be the requester's manager)
    if current_user.role == UserRole.MANAGER:
        if request.user.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to approve this request"
            )

    # Update request
    if approval_data.approved:
        request.status = LeaveStatus.APPROVED
        request.approved_by = current_user.id
        request.approved_at = datetime.utcnow()
    else:
        request.status = LeaveStatus.REJECTED
        request.approved_by = current_user.id
        request.approved_at = datetime.utcnow()
        request.rejection_reason = approval_data.rejection_reason

    db.commit()
    db.refresh(request)

    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_leave_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a leave request (owner can cancel their own pending requests)."""
    request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Only owner or admin can cancel
    if request.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this request"
        )

    # Can only cancel pending requests
    if request.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel pending requests"
        )

    request.status = LeaveStatus.CANCELLED
    db.commit()

    return None
