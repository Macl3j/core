"""Calendar export functionality for leave requests."""
from datetime import datetime, timedelta
from typing import List
from icalendar import Calendar, Event, vText
from .models import LeaveRequest, LeaveType, User


def get_leave_type_display(leave_type: LeaveType) -> str:
    """Get display name for leave type."""
    type_names = {
        LeaveType.ANNUAL: "Urlop wypoczynkowy",
        LeaveType.SICK: "Zwolnienie lekarskie",
        LeaveType.UNPAID: "Urlop bezpłatny",
        LeaveType.MATERNITY: "Urlop macierzyński",
        LeaveType.PATERNITY: "Urlop ojcowski",
        LeaveType.COMPASSIONATE: "Urlop okolicznościowy",
        LeaveType.OTHER: "Inny urlop",
    }
    return type_names.get(leave_type, str(leave_type.value))


def create_leave_calendar_event(leave_request: LeaveRequest) -> Event:
    """
    Create an iCalendar event from a leave request.

    Args:
        leave_request: LeaveRequest object

    Returns:
        icalendar.Event object
    """
    event = Event()

    # Basic event info
    leave_type_name = get_leave_type_display(leave_request.leave_type)
    event.add('summary', f"{leave_type_name}")
    event.add('dtstart', leave_request.start_date.date())
    event.add('dtend', (leave_request.end_date + timedelta(days=1)).date())  # End date is exclusive in iCal

    # Description
    description_parts = [
        f"Typ: {leave_type_name}",
        f"Status: {leave_request.status.value}",
        f"Liczba dni: {leave_request.days_count}",
    ]

    if leave_request.reason:
        description_parts.append(f"Powód: {leave_request.reason}")

    if leave_request.approved_by and leave_request.approver:
        description_parts.append(f"Zatwierdził: {leave_request.approver.full_name}")

    event.add('description', '\n'.join(description_parts))

    # Additional properties
    event.add('uid', f"leave-{leave_request.id}@leavemanagement.local")
    event.add('dtstamp', datetime.utcnow())
    event.add('created', leave_request.created_at)
    event.add('last-modified', leave_request.updated_at)

    # Status mapping
    status_map = {
        'pending': 'TENTATIVE',
        'approved': 'CONFIRMED',
        'rejected': 'CANCELLED',
        'cancelled': 'CANCELLED',
    }
    event.add('status', status_map.get(leave_request.status.value, 'TENTATIVE'))

    # Categories and classification
    event.add('categories', [leave_type_name, 'Urlop'])
    event.add('class', 'PRIVATE')

    # Organizer (the employee who requested)
    if leave_request.user:
        organizer = vText(leave_request.user.full_name)
        event.add('organizer', organizer)

    return event


def generate_leave_calendar(leave_requests: List[LeaveRequest], calendar_name: str = "Urlopy") -> str:
    """
    Generate an iCalendar file from a list of leave requests.

    Args:
        leave_requests: List of LeaveRequest objects
        calendar_name: Name of the calendar

    Returns:
        iCalendar data as string
    """
    cal = Calendar()

    # Calendar properties
    cal.add('prodid', '-//Leave Management System//leavemanagement.local//')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', calendar_name)
    cal.add('x-wr-timezone', 'Europe/Warsaw')
    cal.add('x-wr-caldesc', 'Kalendarz urlopów z systemu zarządzania urlopami')

    # Add events for each leave request
    for leave_request in leave_requests:
        event = create_leave_calendar_event(leave_request)
        cal.add_component(event)

    return cal.to_ical().decode('utf-8')


def generate_single_leave_calendar(leave_request: LeaveRequest) -> str:
    """
    Generate an iCalendar file for a single leave request.

    Args:
        leave_request: LeaveRequest object

    Returns:
        iCalendar data as string
    """
    return generate_leave_calendar([leave_request], f"Urlop - {leave_request.user.full_name}")
