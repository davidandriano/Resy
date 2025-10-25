"""
Notification and logging utilities for Resy Bot
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from config import Settings
import sys
from datetime import datetime
import os


def setup_logging(log_level: int = logging.INFO, log_file: Optional[str] = None):
    """
    Setup logging configuration

    Args:
        log_level: Logging level (default: INFO)
        log_file: Optional log file path
    """
    # Create logs directory if needed
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Setup handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )

    # Reduce noise from requests library
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def send_notification(settings: Settings, subject: str, message: str) -> bool:
    """
    Send email notification

    Args:
        settings: Application settings
        subject: Email subject
        message: Email message body

    Returns:
        True if sent successfully
    """
    # Check if email notifications are configured
    if not all([
        settings.notification_email,
        settings.smtp_server,
        settings.smtp_username,
        settings.smtp_password
    ]):
        logging.debug("Email notifications not configured, skipping")
        return False

    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_username
        msg["To"] = settings.notification_email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        # Send email
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)

        logging.info(f"Notification sent to {settings.notification_email}")
        return True

    except Exception as e:
        logging.error(f"Failed to send notification: {e}")
        return False


def log_reservation_attempt(
    restaurant_name: str,
    party_size: int,
    reservation_date: str,
    status: str,
    details: Optional[str] = None
):
    """
    Log a reservation attempt to a file

    Args:
        restaurant_name: Restaurant name
        party_size: Party size
        reservation_date: Reservation date
        status: Status (e.g., "success", "failed", "no_availability")
        details: Optional additional details
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "reservation_history.log")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"{timestamp} | {restaurant_name} | Party: {party_size} | "
        f"Date: {reservation_date} | Status: {status}"
    )

    if details:
        log_entry += f" | {details}"

    with open(log_file, "a") as f:
        f.write(log_entry + "\n")
