"""Email notification service for leave management system."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from jinja2 import Template

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@leavemanagement.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Leave Management System")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send an email.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content (optional)

    Returns:
        True if email was sent successfully, False otherwise
    """
    if not EMAIL_ENABLED:
        print(f"[EMAIL DISABLED] Would send email to {to_email}: {subject}")
        return True

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("[EMAIL ERROR] SMTP credentials not configured")
        return False

    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = to_email

        # Attach plain text version
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)

        # Attach HTML version
        part2 = MIMEText(html_content, "html")
        message.attach(part2)

        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)

        print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
        return True

    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {str(e)}")
        return False


# Email templates
def get_leave_request_template() -> str:
    """Get template for new leave request notification."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #4f46e5; color: white; padding: 20px; text-align: center; }
            .content { background-color: #f9fafb; padding: 20px; margin-top: 20px; }
            .details { background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4f46e5; }
            .button { display: inline-block; padding: 12px 24px; background-color: #4f46e5; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
            .footer { text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Nowy wniosek urlopowy</h1>
            </div>
            <div class="content">
                <p>Witaj {{ manager_name }},</p>
                <p>Pracownik <strong>{{ employee_name }}</strong> złożył nowy wniosek urlopowy oczekujący na zatwierdzenie.</p>

                <div class="details">
                    <h3>Szczegóły wniosku:</h3>
                    <p><strong>Typ urlopu:</strong> {{ leave_type }}</p>
                    <p><strong>Data rozpoczęcia:</strong> {{ start_date }}</p>
                    <p><strong>Data zakończenia:</strong> {{ end_date }}</p>
                    <p><strong>Liczba dni:</strong> {{ days_count }}</p>
                    {% if reason %}
                    <p><strong>Powód:</strong> {{ reason }}</p>
                    {% endif %}
                    <p><strong>Data złożenia:</strong> {{ created_at }}</p>
                </div>

                <p style="text-align: center;">
                    <a href="{{ dashboard_url }}" class="button">Przejdź do systemu</a>
                </p>
            </div>
            <div class="footer">
                <p>To jest automatyczna wiadomość z systemu zarządzania urlopami.</p>
                <p>Nie odpowiadaj na tę wiadomość.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_leave_approved_template() -> str:
    """Get template for leave approved notification."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #10b981; color: white; padding: 20px; text-align: center; }
            .content { background-color: #f9fafb; padding: 20px; margin-top: 20px; }
            .details { background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #10b981; }
            .button { display: inline-block; padding: 12px 24px; background-color: #10b981; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
            .footer { text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Wniosek zatwierdzony</h1>
            </div>
            <div class="content">
                <p>Witaj {{ employee_name }},</p>
                <p>Twój wniosek urlopowy został <strong style="color: #10b981;">zatwierdzony</strong> przez {{ approver_name }}.</p>

                <div class="details">
                    <h3>Szczegóły zatwierdzonego urlopu:</h3>
                    <p><strong>Typ urlopu:</strong> {{ leave_type }}</p>
                    <p><strong>Data rozpoczęcia:</strong> {{ start_date }}</p>
                    <p><strong>Data zakończenia:</strong> {{ end_date }}</p>
                    <p><strong>Liczba dni:</strong> {{ days_count }}</p>
                    <p><strong>Zatwierdzony dnia:</strong> {{ approved_at }}</p>
                </div>

                <p style="text-align: center;">
                    <a href="{{ dashboard_url }}" class="button">Zobacz w systemie</a>
                    <a href="{{ calendar_url }}" class="button">Dodaj do kalendarza</a>
                </p>
            </div>
            <div class="footer">
                <p>To jest automatyczna wiadomość z systemu zarządzania urlopami.</p>
                <p>Nie odpowiadaj na tę wiadomość.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_leave_rejected_template() -> str:
    """Get template for leave rejected notification."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #ef4444; color: white; padding: 20px; text-align: center; }
            .content { background-color: #f9fafb; padding: 20px; margin-top: 20px; }
            .details { background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #ef4444; }
            .button { display: inline-block; padding: 12px 24px; background-color: #ef4444; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
            .footer { text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>❌ Wniosek odrzucony</h1>
            </div>
            <div class="content">
                <p>Witaj {{ employee_name }},</p>
                <p>Niestety, Twój wniosek urlopowy został <strong style="color: #ef4444;">odrzucony</strong> przez {{ approver_name }}.</p>

                <div class="details">
                    <h3>Szczegóły wniosku:</h3>
                    <p><strong>Typ urlopu:</strong> {{ leave_type }}</p>
                    <p><strong>Data rozpoczęcia:</strong> {{ start_date }}</p>
                    <p><strong>Data zakończenia:</strong> {{ end_date }}</p>
                    <p><strong>Liczba dni:</strong> {{ days_count }}</p>
                    {% if rejection_reason %}
                    <p><strong>Powód odrzucenia:</strong> {{ rejection_reason }}</p>
                    {% endif %}
                </div>

                <p>Jeśli masz pytania, skontaktuj się ze swoim przełożonym.</p>

                <p style="text-align: center;">
                    <a href="{{ dashboard_url }}" class="button">Przejdź do systemu</a>
                </p>
            </div>
            <div class="footer">
                <p>To jest automatyczna wiadomość z systemu zarządzania urlopami.</p>
                <p>Nie odpowiadaj na tę wiadomość.</p>
            </div>
        </div>
    </body>
    </html>
    """


def send_leave_request_notification(
    manager_email: str,
    manager_name: str,
    employee_name: str,
    leave_type: str,
    start_date: datetime,
    end_date: datetime,
    days_count: float,
    reason: Optional[str],
    created_at: datetime,
    dashboard_url: str = "http://localhost:8000/dashboard"
) -> bool:
    """Send notification to manager about new leave request."""
    template = Template(get_leave_request_template())

    html_content = template.render(
        manager_name=manager_name,
        employee_name=employee_name,
        leave_type=leave_type,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        days_count=days_count,
        reason=reason,
        created_at=created_at.strftime("%Y-%m-%d %H:%M"),
        dashboard_url=dashboard_url
    )

    subject = f"Nowy wniosek urlopowy od {employee_name}"

    return send_email(manager_email, subject, html_content)


def send_leave_approved_notification(
    employee_email: str,
    employee_name: str,
    approver_name: str,
    leave_type: str,
    start_date: datetime,
    end_date: datetime,
    days_count: float,
    approved_at: datetime,
    request_id: int,
    dashboard_url: str = "http://localhost:8000/dashboard"
) -> bool:
    """Send notification to employee about approved leave."""
    template = Template(get_leave_approved_template())

    calendar_url = f"{dashboard_url.replace('/dashboard', '')}/api/leaves/{request_id}/calendar"

    html_content = template.render(
        employee_name=employee_name,
        approver_name=approver_name,
        leave_type=leave_type,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        days_count=days_count,
        approved_at=approved_at.strftime("%Y-%m-%d %H:%M"),
        dashboard_url=dashboard_url,
        calendar_url=calendar_url
    )

    subject = f"✅ Twój wniosek urlopowy został zatwierdzony"

    return send_email(employee_email, subject, html_content)


def send_leave_rejected_notification(
    employee_email: str,
    employee_name: str,
    approver_name: str,
    leave_type: str,
    start_date: datetime,
    end_date: datetime,
    days_count: float,
    rejection_reason: Optional[str],
    dashboard_url: str = "http://localhost:8000/dashboard"
) -> bool:
    """Send notification to employee about rejected leave."""
    template = Template(get_leave_rejected_template())

    html_content = template.render(
        employee_name=employee_name,
        approver_name=approver_name,
        leave_type=leave_type,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        days_count=days_count,
        rejection_reason=rejection_reason,
        dashboard_url=dashboard_url
    )

    subject = f"❌ Twój wniosek urlopowy został odrzucony"

    return send_email(employee_email, subject, html_content)
