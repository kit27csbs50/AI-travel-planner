"""
Database models for the AI Travel Planner application.
Defines Users, Bookings, and TripHistory tables using SQLAlchemy ORM.
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Shared SQLAlchemy instance — imported by app.py and routes.py
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    Represents a registered user.
    Implements Flask-Login's UserMixin for session integration.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationship: one user → many bookings
    bookings = db.relationship("Booking", backref="user", lazy=True)

    def set_password(self, password):
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serialize user data (excludes password hash)."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.email}>"


class Booking(db.Model):
    """
    Represents a trip booking made by a user.
    Auto-generates a unique booking ID in the format ATP1001, ATP1002, etc.
    """

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    source = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    travel_date = db.Column(db.String(50), nullable=False)
    passengers = db.Column(db.Integer, default=1)
    budget = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Confirmed")

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationship: one booking → many history entries
    history = db.relationship("TripHistory", backref="booking", lazy=True)

    @staticmethod
    def generate_booking_id():
        """
        Generate a unique sequential booking ID.
        Pattern: ATP1001, ATP1002, ATP1003, ...
        """
        last_booking = (
            Booking.query.order_by(Booking.id.desc()).first()
        )
        if last_booking:
            # Extract the numeric suffix and increment
            last_number = int(last_booking.booking_id.replace("ATP", ""))
            return f"ATP{last_number + 1}"
        return "ATP1001"

    def to_dict(self):
        """Serialize booking data to a dictionary."""
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "source": self.source,
            "destination": self.destination,
            "travel_date": self.travel_date,
            "passengers": self.passengers,
            "budget": self.budget,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Booking {self.booking_id}>"


class TripHistory(db.Model):
    """
    Audit log for booking lifecycle events.
    Records actions like 'Booking Created', 'Booking Cancelled', etc.
    """

    __tablename__ = "trip_history"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.String(20),
        db.ForeignKey("bookings.booking_id"),
        nullable=False,
        index=True,
    )
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Serialize history entry."""
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "action": self.action,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    def __repr__(self):
        return f"<TripHistory {self.booking_id} – {self.action}>"
