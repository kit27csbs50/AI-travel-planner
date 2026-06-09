"""
Configuration settings for the AI Travel Planner Flask application.
Contains database, mail, security, and session settings.
"""

import os

# Base directory for resolving relative paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class with default settings."""

    # --- Security ---
    # Secret key for session management and CSRF protection.
    # In production, set this via the environment variable SECRET_KEY.
    SECRET_KEY = os.environ.get("SECRET_KEY", "atp-dev-secret-key-change-in-production")

    # --- Database ---
    # SQLite database stored alongside the application files.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Suppress deprecation warning

    # --- Flask-Mail ---
    # Configure these via environment variables for production SMTP.
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", None)
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", None)
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@wanderlust-ai.com")

    # --- Session ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
