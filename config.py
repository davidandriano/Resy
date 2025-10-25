"""
Configuration management for Resy Bot
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional, List
from datetime import date, time
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Resy credentials
    resy_email: str = Field(..., description="Resy account email")
    resy_password: str = Field(..., description="Resy account password")
    resy_payment_method_id: Optional[str] = Field(None, description="Payment method ID")

    # Notification settings
    notification_email: Optional[str] = Field(None, description="Email for notifications")
    smtp_server: Optional[str] = Field(None, description="SMTP server")
    smtp_port: int = Field(587, description="SMTP port")
    smtp_username: Optional[str] = Field(None, description="SMTP username")
    smtp_password: Optional[str] = Field(None, description="SMTP password")


class ReservationConfig:
    """Configuration for a specific reservation attempt"""

    def __init__(
        self,
        restaurant_name: str,
        party_size: int,
        reservation_date: date,
        preferred_times: List[str],
        location: str = "ny",
        start_monitoring_at: Optional[str] = None,
        auto_accept_any_time: bool = False
    ):
        """
        Initialize reservation configuration

        Args:
            restaurant_name: Name of the restaurant to search for
            party_size: Number of people (1-20)
            reservation_date: Date for the reservation
            preferred_times: List of preferred times in HH:MM format (e.g., ["19:00", "19:30"])
            location: Location code (default: "ny")
            start_monitoring_at: When to start checking (format: "HH:MM" in 24-hour)
            auto_accept_any_time: Accept any available time if preferred times unavailable
        """
        self.restaurant_name = restaurant_name
        self.party_size = party_size
        self.reservation_date = reservation_date
        self.preferred_times = preferred_times
        self.location = location
        self.start_monitoring_at = start_monitoring_at
        self.auto_accept_any_time = auto_accept_any_time
        self.venue_id: Optional[int] = None

    def __str__(self) -> str:
        return (
            f"Reservation for {self.party_size} at {self.restaurant_name} "
            f"on {self.reservation_date} (preferred times: {', '.join(self.preferred_times)})"
        )


def load_settings() -> Settings:
    """
    Load settings from environment

    Returns:
        Settings object

    Raises:
        ValueError: If required settings are missing
    """
    try:
        return Settings()
    except Exception as e:
        raise ValueError(f"Failed to load settings. Make sure .env file is configured: {e}")
