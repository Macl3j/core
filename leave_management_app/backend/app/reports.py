"""Reports generation module for leave management system."""
from datetime import datetime
from typing import List
from io import BytesIO, StringIO
import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import LeaveRequest, User


def get_leave_type_display(leave_type: str) -> str:
    """Get display name for leave type."""
    type_names = {
        "annual": "Wypoczynkowy",
        "sick": "Zwolnienie",
        "unpaid": "Bezpłatny",
        "maternity": "Macierzyński",
        "paternity": "Ojcowski",
        "compassionate": "Okolicznościowy",
        "other": "Inny",
    }
    return type_names.get(leave_type, leave_type)


def get_status_display(status: str) -> str:
    """Get display name for status."""
    status_names = {
        "pending": "Oczekujące",
        "approved": "Zatwierdzone",
        "rejected": "Odrzucone",
        "cancelled": "Anulowane",
    }
    return status_names.get(status, status)


def generate_csv_report(leave_requests: List[LeaveRequest]) -> str:
    """
    Generate CSV report from leave requests.

    Args:
        leave_requests: List of LeaveRequest objects

    Returns:
        CSV data as string with UTF-8 BOM
    """
    # Create StringIO buffer
    output = StringIO()

    # Define CSV headers
    headers = [
        'ID', 'Pracownik', 'Email', 'Dział', 'Typ urlopu',
        'Data rozpoczęcia', 'Data zakończenia', 'Liczba dni',
        'Status', 'Powód', 'Zatwierdzający', 'Data zatwierdzenia', 'Data utworzenia'
    ]

    # Create CSV writer with UTF-8 encoding
    writer = csv.DictWriter(output, fieldnames=headers, quoting=csv.QUOTE_MINIMAL)

    # Write header
    writer.writeheader()

    # Write data rows
    for req in leave_requests:
        writer.writerow({
            'ID': req.id,
            'Pracownik': req.user.full_name if req.user else 'N/A',
            'Email': req.user.email if req.user else 'N/A',
            'Dział': req.user.department if req.user and req.user.department else 'N/A',
            'Typ urlopu': get_leave_type_display(req.leave_type.value),
            'Data rozpoczęcia': req.start_date.strftime('%Y-%m-%d'),
            'Data zakończenia': req.end_date.strftime('%Y-%m-%d'),
            'Liczba dni': req.days_count,
            'Status': get_status_display(req.status.value),
            'Powód': req.reason if req.reason else '',
            'Zatwierdzający': req.approver.full_name if req.approver else '',
            'Data zatwierdzenia': req.approved_at.strftime('%Y-%m-%d %H:%M') if req.approved_at else '',
            'Data utworzenia': req.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    # Add UTF-8 BOM for Excel compatibility
    csv_content = '\ufeff' + output.getvalue()

    return csv_content


def generate_excel_report(leave_requests: List[LeaveRequest]) -> BytesIO:
    """
    Generate Excel report from leave requests with formatting.

    Args:
        leave_requests: List of LeaveRequest objects

    Returns:
        BytesIO object containing Excel file
    """
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Raporty urlopów"

    # Define styles
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")

    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Headers
    headers = [
        'ID', 'Pracownik', 'Email', 'Dział', 'Typ urlopu',
        'Data rozpoczęcia', 'Data zakończenia', 'Liczba dni',
        'Status', 'Powód', 'Zatwierdzający', 'Data zatwierdzenia', 'Data utworzenia'
    ]

    # Write headers
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border

    # Write data
    for row, req in enumerate(leave_requests, start=2):
        ws.cell(row=row, column=1, value=req.id).border = border
        ws.cell(row=row, column=2, value=req.user.full_name if req.user else 'N/A').border = border
        ws.cell(row=row, column=3, value=req.user.email if req.user else 'N/A').border = border
        ws.cell(row=row, column=4, value=req.user.department if req.user and req.user.department else 'N/A').border = border
        ws.cell(row=row, column=5, value=get_leave_type_display(req.leave_type.value)).border = border
        ws.cell(row=row, column=6, value=req.start_date.strftime('%Y-%m-%d')).border = border
        ws.cell(row=row, column=7, value=req.end_date.strftime('%Y-%m-%d')).border = border
        ws.cell(row=row, column=8, value=req.days_count).border = border

        # Status with color
        status_cell = ws.cell(row=row, column=9, value=get_status_display(req.status.value))
        status_cell.border = border
        if req.status.value == 'approved':
            status_cell.fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
        elif req.status.value == 'rejected':
            status_cell.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        elif req.status.value == 'pending':
            status_cell.fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")

        ws.cell(row=row, column=10, value=req.reason if req.reason else '').border = border
        ws.cell(row=row, column=11, value=req.approver.full_name if req.approver else '').border = border
        ws.cell(row=row, column=12, value=req.approved_at.strftime('%Y-%m-%d %H:%M') if req.approved_at else '').border = border
        ws.cell(row=row, column=13, value=req.created_at.strftime('%Y-%m-%d %H:%M')).border = border

    # Adjust column widths
    column_widths = [5, 20, 25, 15, 15, 15, 15, 10, 15, 30, 20, 18, 18]
    for col, width in enumerate(column_widths, start=1):
        ws.column_dimensions[chr(64 + col)].width = width

    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output


def generate_pdf_report(leave_requests: List[LeaveRequest], report_title: str = "Raport urlopów") -> BytesIO:
    """
    Generate PDF report from leave requests.

    Args:
        leave_requests: List of LeaveRequest objects
        report_title: Title of the report

    Returns:
        BytesIO object containing PDF file
    """
    buffer = BytesIO()

    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    # Container for elements
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=30,
        alignment=1  # Center
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=1  # Center
    )

    # Title
    title = Paragraph(report_title, title_style)
    elements.append(title)

    # Subtitle with date
    subtitle = Paragraph(
        f"Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        subtitle_style
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 12))

    # Summary statistics
    total_requests = len(leave_requests)
    approved_count = sum(1 for req in leave_requests if req.status.value == 'approved')
    pending_count = sum(1 for req in leave_requests if req.status.value == 'pending')
    rejected_count = sum(1 for req in leave_requests if req.status.value == 'rejected')
    total_days = sum(req.days_count for req in leave_requests if req.status.value == 'approved')

    summary_data = [
        ['Podsumowanie', ''],
        ['Wszystkie wnioski', str(total_requests)],
        ['Zatwierdzone', str(approved_count)],
        ['Oczekujące', str(pending_count)],
        ['Odrzucone', str(rejected_count)],
        ['Łącznie dni (zatwierdzone)', f"{total_days:.1f}"],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Leave requests table
    if leave_requests:
        # Table header
        table_data = [[
            'Pracownik',
            'Typ',
            'Od',
            'Do',
            'Dni',
            'Status',
        ]]

        # Table data
        for req in leave_requests:
            table_data.append([
                req.user.full_name if req.user else 'N/A',
                get_leave_type_display(req.leave_type.value),
                req.start_date.strftime('%Y-%m-%d'),
                req.end_date.strftime('%Y-%m-%d'),
                str(req.days_count),
                get_status_display(req.status.value),
            ])

        # Create table
        leave_table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 1*inch, 0.6*inch, 1*inch])

        # Style table
        leave_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))

        elements.append(leave_table)

    # Build PDF
    doc.build(elements)

    buffer.seek(0)
    return buffer


def generate_user_summary_report(user: User, leave_requests: List[LeaveRequest], year: int) -> BytesIO:
    """
    Generate a personalized summary report for a user.

    Args:
        user: User object
        leave_requests: List of user's leave requests for the year
        year: Year for the report

    Returns:
        BytesIO object containing PDF file
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=10,
        alignment=1
    )

    title = Paragraph(f"Podsumowanie urlopów {year}", title_style)
    elements.append(title)

    subtitle = Paragraph(f"{user.full_name}", styles['Heading2'])
    elements.append(subtitle)
    elements.append(Spacer(1, 20))

    # User info
    user_info_data = [
        ['Informacje o pracowniku', ''],
        ['Imię i nazwisko', user.full_name],
        ['Email', user.email],
        ['Dział', user.department if user.department else 'N/A'],
        ['Limit urlopu wypoczynkowego', f"{user.annual_leave_days:.1f} dni"],
        ['Limit zwolnień lekarskich', f"{user.sick_leave_days:.1f} dni"],
    ]

    user_table = Table(user_info_data, colWidths=[3*inch, 3*inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    elements.append(user_table)
    elements.append(Spacer(1, 20))

    # Calculate statistics
    approved_requests = [req for req in leave_requests if req.status.value == 'approved']
    annual_used = sum(req.days_count for req in approved_requests if req.leave_type.value == 'annual')
    sick_used = sum(req.days_count for req in approved_requests if req.leave_type.value == 'sick')

    # Leave balance
    balance_data = [
        ['Bilans urlopów', 'Limit', 'Wykorzystane', 'Pozostało'],
        ['Urlop wypoczynkowy', f"{user.annual_leave_days:.1f}", f"{annual_used:.1f}", f"{user.annual_leave_days - annual_used:.1f}"],
        ['Zwolnienia lekarskie', f"{user.sick_leave_days:.1f}", f"{sick_used:.1f}", f"{user.sick_leave_days - sick_used:.1f}"],
    ]

    balance_table = Table(balance_data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.3*inch])
    balance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
    ]))

    elements.append(balance_table)
    elements.append(Spacer(1, 20))

    # Leave requests list
    if leave_requests:
        requests_data = [['Data', 'Typ', 'Dni', 'Status']]

        for req in leave_requests:
            requests_data.append([
                f"{req.start_date.strftime('%Y-%m-%d')} - {req.end_date.strftime('%Y-%m-%d')}",
                get_leave_type_display(req.leave_type.value),
                str(req.days_count),
                get_status_display(req.status.value),
            ])

        requests_table = Table(requests_data, colWidths=[2.5*inch, 1.5*inch, 0.8*inch, 1.2*inch])
        requests_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))

        elements.append(Paragraph("Historia urlopów", styles['Heading3']))
        elements.append(Spacer(1, 10))
        elements.append(requests_table)

    # Build PDF
    doc.build(elements)

    buffer.seek(0)
    return buffer
