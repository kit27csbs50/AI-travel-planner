"""
AI Travel Planner – Flask Application Entry Point.

This is the main application file that:
  1. Creates and configures the Flask app
  2. Initializes extensions (SQLAlchemy, Flask-Login, Flask-Mail)
  3. Registers the API blueprint
  4. Serves the existing frontend (HTML/CSS/JS) from the parent directory
  5. Creates database tables on first run

Run with:
    python app.py
"""

import os
from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS

from config import Config
from models import db, User
from routes import api, init_mail

# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------

def create_app():
    """Build and configure the Flask application."""

    app = Flask(
        __name__,
        static_folder=None,  # We serve static files manually from the parent dir
    )
    app.config.from_object(Config)

    # --- Enable CORS for frontend development (same-origin in production) ---
    CORS(app, supports_credentials=True)

    # --- Database ---
    db.init_app(app)

    # --- Flask-Login ---
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """Callback used by Flask-Login to reload a user from the session."""
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        """Return a JSON 401 instead of redirecting to a login page."""
        from flask import jsonify
        return jsonify({
            "success": False,
            "message": "Authentication required. Please log in."
        }), 401

    # --- Flask-Mail ---
    mail = Mail(app)
    init_mail(mail)  # Share mail instance with routes module

    # --- Register API Blueprint ---
    app.register_blueprint(api)

    # --- Serve Frontend Static Files ---
    # The HTML/CSS/JS frontend lives one directory above /backend.
    FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    @app.route("/")
    def serve_index():
        """Serve the main index.html from the frontend directory."""
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:filename>")
    def serve_static(filename):
        """
        Serve any static file (CSS, JS, images) from the frontend directory.
        Falls back to 404 if the file doesn't exist.
        """
        return send_from_directory(FRONTEND_DIR, filename)

    # --- Create Database Tables ---
    with app.app_context():
        db.create_all()
        print("[INFO] Database tables created / verified.")

    return app


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = create_app()

    print("\n" + "=" * 60)
    print("  ✈️  WanderLust AI – Travel Planner Backend")
    print("  🌐  Running at http://127.0.0.1:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, host="0.0.0.0", port=5000)
