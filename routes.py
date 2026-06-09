"""
REST API route definitions for the AI Travel Planner application.

Endpoints:
    POST /register          – Create a new user account
    POST /login             – Authenticate and start a session
    POST /logout            – End the current session
    POST /book-trip         – Create a new trip booking
    GET  /booking-history   – List all bookings for the logged-in user
    GET  /booking/<id>      – Get details of a specific booking
    GET  /ticket/<id>       – Generate a digital ticket for a booking
"""

import re
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

from models import db, User, Booking, TripHistory

# Blueprint keeps routes modular and separate from the app factory
api = Blueprint("api", __name__)

# Mail instance will be injected by app.py after creation
mail = None


def init_mail(mail_instance):
    """Called from app.py to share the Flask-Mail instance with routes."""
    global mail
    mail = mail_instance


# ---------------------------------------------------------------------------
# Helper Utilities
# ---------------------------------------------------------------------------

def validate_email(email):
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def error_response(message, status_code=400):
    """Convenience wrapper for consistent error JSON responses."""
    return jsonify({"success": False, "message": message}), status_code


def success_response(message, data=None, status_code=200):
    """Convenience wrapper for consistent success JSON responses."""
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


# ---------------------------------------------------------------------------
# Authentication Endpoints
# ---------------------------------------------------------------------------

@api.route("/register", methods=["POST"])
def register():
    """
    Register a new user account.

    Expected JSON body:
        { "full_name": str, "email": str, "password": str }

    Returns:
        201 on success, 400 on validation error, 409 on duplicate email.
    """
    data = request.get_json(silent=True)

    # --- Input validation ---
    if not data:
        return error_response("Request body must be valid JSON.")

    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not full_name:
        return error_response("Full name is required.")
    if not email or not validate_email(email):
        return error_response("A valid email address is required.")
    if len(password) < 6:
        return error_response("Password must be at least 6 characters long.")

    # --- Duplicate check ---
    if User.query.filter_by(email=email).first():
        return error_response("An account with this email already exists.", 409)

    # --- Create user ---
    user = User(full_name=full_name, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return success_response(
        "Registration successful.",
        data=user.to_dict(),
        status_code=201,
    )


@api.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and start a session.

    Expected JSON body:
        { "email": str, "password": str }

    Returns:
        200 on success, 401 on invalid credentials.
    """
    data = request.get_json(silent=True)

    if not data:
        return error_response("Request body must be valid JSON.")

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return error_response("Email and password are required.")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return error_response("Invalid email or password.", 401)

    # Log the user in (creates a session cookie)
    login_user(user, remember=True)

    return success_response("Login successful.", data=user.to_dict())


@api.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    End the current user's session.

    Returns:
        200 on success.
    """
    logout_user()
    return success_response("Logged out successfully.")


# ---------------------------------------------------------------------------
# Booking Endpoints
# ---------------------------------------------------------------------------

@api.route("/book-trip", methods=["POST"])
@login_required
def book_trip():
    """
    Create a new trip booking for the logged-in user.

    Expected JSON body:
        {
            "source": str,
            "destination": str,
            "travel_date": str,
            "passengers": int (optional, default 1),
            "budget": float
        }

    On success:
        - Generates a unique booking ID (ATP1001, ATP1002, …)
        - Sets status to "Confirmed"
        - Records a TripHistory entry
        - Sends a confirmation email (if mail is configured)

    Returns:
        201 on success, 400 on validation error.
    """
    data = request.get_json(silent=True)

    if not data:
        return error_response("Request body must be valid JSON.")

    # --- Validate required fields ---
    source = (data.get("source") or "").strip()
    destination = (data.get("destination") or "").strip()
    travel_date = (data.get("travel_date") or "").strip()
    budget = data.get("budget")
    passengers = data.get("passengers", 1)

    if not source:
        return error_response("Source location is required.")
    if not destination:
        return error_response("Destination is required.")
    if not travel_date:
        return error_response("Travel date is required.")
    if budget is None:
        return error_response("Budget is required.")

    try:
        budget = float(budget)
        if budget <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return error_response("Budget must be a positive number.")

    try:
        passengers = int(passengers)
        if passengers < 1:
            raise ValueError
    except (ValueError, TypeError):
        return error_response("Passengers must be a positive integer.")

    # --- Create booking ---
    booking = Booking(
        booking_id=Booking.generate_booking_id(),
        user_id=current_user.id,
        source=source,
        destination=destination,
        travel_date=travel_date,
        passengers=passengers,
        budget=budget,
        status="Confirmed",
    )
    db.session.add(booking)

    # --- Record history ---
    history_entry = TripHistory(
        booking_id=booking.booking_id,
        action="Booking Created – Status: Confirmed",
    )
    db.session.add(history_entry)

    db.session.commit()

    # --- Send confirmation email (best-effort) ---
    _send_confirmation_email(booking, current_user)

    return success_response(
        "Trip booked successfully!",
        data=booking.to_dict(),
        status_code=201,
    )


@api.route("/booking-history", methods=["GET"])
@login_required
def booking_history():
    """
    Fetch all bookings for the logged-in user, sorted newest-first.

    Returns:
        200 with list of booking objects.
    """
    bookings = (
        Booking.query
        .filter_by(user_id=current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    return success_response(
        "Booking history retrieved.",
        data=[b.to_dict() for b in bookings],
    )


@api.route("/booking/<booking_id>", methods=["GET"])
@login_required
def get_booking(booking_id):
    """
    Retrieve full details of a specific booking by its booking ID.
    The booking must belong to the logged-in user.

    Returns:
        200 with booking data, or 404 if not found.
    """
    booking = Booking.query.filter_by(
        booking_id=booking_id,
        user_id=current_user.id,
    ).first()

    if not booking:
        return error_response("Booking not found.", 404)

    # Include history entries alongside the booking details
    history = TripHistory.query.filter_by(booking_id=booking_id).order_by(
        TripHistory.timestamp.desc()
    ).all()

    booking_data = booking.to_dict()
    booking_data["history"] = [h.to_dict() for h in history]

    return success_response("Booking details retrieved.", data=booking_data)


# ---------------------------------------------------------------------------
# Ticket Endpoint
# ---------------------------------------------------------------------------

@api.route("/ticket/<booking_id>", methods=["GET"])
@login_required
def get_ticket(booking_id):
    """
    Generate a digital ticket for a confirmed booking.

    Returns:
        200 with ticket JSON, or 404 if the booking is not found.
    """
    booking = Booking.query.filter_by(
        booking_id=booking_id,
        user_id=current_user.id,
    ).first()

    if not booking:
        return error_response("Booking not found.", 404)

    ticket = {
        "booking_id": booking.booking_id,
        "passenger_name": current_user.full_name,
        "source": booking.source,
        "destination": booking.destination,
        "travel_date": booking.travel_date,
        "passengers": booking.passengers,
        "budget": booking.budget,
        "booking_status": booking.status,
        "issued_at": booking.created_at.isoformat() if booking.created_at else None,
    }

    return success_response("Ticket generated.", data=ticket)


# ---------------------------------------------------------------------------
# Email Helper
# ---------------------------------------------------------------------------

def _send_confirmation_email(booking, user):
    """
    Send a booking confirmation email to the user.
    Fails silently if Flask-Mail is not configured (no MAIL_USERNAME set).
    """
    if mail is None:
        return

    # Skip if no SMTP credentials are configured
    from flask import current_app
    if not current_app.config.get("MAIL_USERNAME"):
        print("[INFO] Mail not configured – skipping confirmation email.")
        return

    try:
        subject = f"Booking Confirmed – {booking.booking_id}"
        body = (
            f"Hello {user.full_name},\n\n"
            f"Your trip has been booked successfully! Here are your details:\n\n"
            f"  Booking ID   : {booking.booking_id}\n"
            f"  From         : {booking.source}\n"
            f"  To           : {booking.destination}\n"
            f"  Travel Date  : {booking.travel_date}\n"
            f"  Passengers   : {booking.passengers}\n"
            f"  Budget       : ₹{booking.budget:,.2f}\n"
            f"  Status       : {booking.status}\n\n"
            f"Thank you for choosing WanderLust AI.\n"
            f"Have a wonderful trip! ✈️\n"
        )

        msg = Message(subject=subject, recipients=[user.email], body=body)
        mail.send(msg)
        print(f"[INFO] Confirmation email sent to {user.email}")
    except Exception as e:
        # Log but don't crash the booking flow
        print(f"[WARNING] Failed to send confirmation email: {e}")
