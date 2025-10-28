"""Reports router for generating various reports."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import LeaveRequest, LeaveStatus, User, UserRole
from ..auth import get_current_user, require_role
from ..reports import (
    generate_csv_report,
    generate_excel_report,
    generate_pdf_report,
    generate_user_summary_report,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/leaves/csv")
def export_leaves_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status_filter: Optional[LeaveStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))
):
    """Export leave requests to CSV format (managers and admins only)."""
    query = db.query(LeaveRequest)

    # Apply role-based filtering
    if current_user.role == UserRole.MANAGER:
        # Managers see their subordinates' requests
        subordinate_ids = [sub.id for sub in current_user.subordinates]
        subordinate_ids.append(current_user.id)
        query = query.filter(LeaveRequest.user_id.in_(subordinate_ids))
    # Admins see all requests

    # Apply date filters
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(LeaveRequest.start_date >= start_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)"
            )

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(LeaveRequest.end_date <= end_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)"
            )

    # Apply status filter
    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)

    requests = query.order_by(LeaveRequest.created_at.desc()).all()

    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No leave requests found"
        )

    # Generate CSV
    csv_content = generate_csv_report(requests)

    # Return as downloadable file
    filename = f"raport_urlopy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_content.encode('utf-8-sig'),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/leaves/excel")
def export_leaves_excel(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status_filter: Optional[LeaveStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))
):
    """Export leave requests to Excel format (managers and admins only)."""
    query = db.query(LeaveRequest)

    # Apply role-based filtering
    if current_user.role == UserRole.MANAGER:
        subordinate_ids = [sub.id for sub in current_user.subordinates]
        subordinate_ids.append(current_user.id)
        query = query.filter(LeaveRequest.user_id.in_(subordinate_ids))

    # Apply date filters
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(LeaveRequest.start_date >= start_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format"
            )

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(LeaveRequest.end_date <= end_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format"
            )

    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)

    requests = query.order_by(LeaveRequest.created_at.desc()).all()

    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No leave requests found"
        )

    # Generate Excel
    excel_buffer = generate_excel_report(requests)

    # Return as downloadable file
    filename = f"raport_urlopy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/leaves/pdf")
def export_leaves_pdf(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status_filter: Optional[LeaveStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))
):
    """Export leave requests to PDF format (managers and admins only)."""
    query = db.query(LeaveRequest)

    # Apply role-based filtering
    if current_user.role == UserRole.MANAGER:
        subordinate_ids = [sub.id for sub in current_user.subordinates]
        subordinate_ids.append(current_user.id)
        query = query.filter(LeaveRequest.user_id.in_(subordinate_ids))

    # Apply date filters
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(LeaveRequest.start_date >= start_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format"
            )

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(LeaveRequest.end_date <= end_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format"
            )

    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)

    requests = query.order_by(LeaveRequest.created_at.desc()).all()

    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No leave requests found"
        )

    # Generate PDF
    report_title = "Raport urlopów"
    if current_user.role == UserRole.MANAGER:
        report_title += f" - Zespół {current_user.full_name}"
    elif current_user.role == UserRole.ADMIN:
        report_title += " - Cała organizacja"

    pdf_buffer = generate_pdf_report(requests, report_title)

    # Return as downloadable file
    filename = f"raport_urlopy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/my-summary/pdf")
def export_my_summary(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export personal leave summary to PDF format."""
    if year is None:
        year = datetime.now().year

    # Validate year
    if year < 2000 or year > 2100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid year"
        )

    # Get user's leave requests for the year
    start_of_year = datetime(year, 1, 1)
    end_of_year = datetime(year, 12, 31, 23, 59, 59)

    requests = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == current_user.id,
        LeaveRequest.start_date >= start_of_year,
        LeaveRequest.start_date <= end_of_year
    ).order_by(LeaveRequest.start_date).all()

    # Generate PDF
    pdf_buffer = generate_user_summary_report(current_user, requests, year)

    # Return as downloadable file
    filename = f"podsumowanie_urlopy_{current_user.username}_{year}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/user-summary/pdf/{user_id}")
def export_user_summary(
    user_id: int,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))
):
    """Export user's leave summary to PDF format (managers and admins only)."""
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions for managers
    if current_user.role == UserRole.MANAGER:
        subordinate_ids = [sub.id for sub in current_user.subordinates]
        if user_id not in subordinate_ids and user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this user's summary"
            )

    if year is None:
        year = datetime.now().year

    if year < 2000 or year > 2100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid year"
        )

    # Get user's leave requests for the year
    start_of_year = datetime(year, 1, 1)
    end_of_year = datetime(year, 12, 31, 23, 59, 59)

    requests = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == user_id,
        LeaveRequest.start_date >= start_of_year,
        LeaveRequest.start_date <= end_of_year
    ).order_by(LeaveRequest.start_date).all()

    # Generate PDF
    pdf_buffer = generate_user_summary_report(user, requests, year)

    # Return as downloadable file
    filename = f"podsumowanie_urlopy_{user.username}_{year}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
