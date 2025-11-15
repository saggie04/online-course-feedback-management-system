# app.py (Render-ready)
import os
import logging
from datetime import datetime
from bson.objectid import ObjectId

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# Load .env locally (ignored in production; keep .env in .gitignore)
load_dotenv()

# --- Configuration ---
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "coursefeedback")
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-me")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() in ("1", "true", "yes")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("course-feedback")

# --- App setup ---
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = SESSION_SECRET
CORS(app, supports_credentials=True)

# Session cookie security (adjust for local dev if needed)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=COOKIE_SECURE,  # True in production with HTTPS
    SESSION_COOKIE_SAMESITE="Lax"
)

# --- Mongo client (persistent, created at startup) ---
if not MONGO_URI:
    logger.error("MONGO_URI environment variable is not set. Exiting.")
    raise RuntimeError("MONGO_URI environment variable is required")

try:
    # default serverSelectionTimeoutMS is okay for Render; adjust if you want
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    logger.info("Connected to MongoDB database: %s", DB_NAME)
except Exception as e:
    logger.exception("Failed to create MongoClient: %s", e)
    raise

# Ensure indexes (safe to call multiple times)
def ensure_indexes():
    try:
        db.users.create_index([("email", ASCENDING)], unique=True)
        db.feedback.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
        logger.info("Ensured MongoDB indexes.")
    except Exception as e:
        logger.warning("Could not ensure indexes: %s", e)

ensure_indexes()

# --- Helpers ---
def current_user_objid():
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        return ObjectId(user_id)
    except Exception:
        return None

# --- Routes ---
@app.route("/")
def index():
    return app.send_static_file("login.html")

@app.route("/healthz", methods=["GET"])
def healthz():
    try:
        # quick ping to Mongo to verify connectivity
        mongo_client.admin.command("ping")
        return jsonify({"ok": True})
    except Exception as e:
        logger.exception("Health check failed: %s", e)
        return jsonify({"ok": False, "error": str(e)}), 500

# Auth
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    users = db.users
    user = users.find_one({"email": email})

    if not user:
        password_hash = generate_password_hash(password)
        try:
            res = users.insert_one({
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.utcnow()
            })
        except Exception as e:
            logger.exception("User creation failed: %s", e)
            return jsonify({"error": "Failed to create user"}), 500

        session["user_id"] = str(res.inserted_id)
        session["email"] = email
        return jsonify({"success": True, "email": email})

    if check_password_hash(user.get("password_hash", ""), password):
        session["user_id"] = str(user["_id"])
        session["email"] = user["email"]
        return jsonify({"success": True, "email": user["email"]})
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route("/api/check-auth", methods=["GET"])
def check_auth():
    if "user_id" in session:
        return jsonify({"authenticated": True, "email": session.get("email")})
    return jsonify({"authenticated": False})

# Feedback
@app.route("/api/feedback", methods=["GET"])
def get_feedback():
    user_objid = current_user_objid()
    if not user_objid:
        return jsonify({"error": "Not authenticated"}), 401

    feedback_docs = db.feedback.find({"user_id": user_objid}).sort("created_at", -1)
    feedbacks = []
    for f in feedback_docs:
        feedbacks.append({
            "id": str(f.get("_id")),
            "courseName": f.get("course_name"),
            "rating": f.get("rating"),
            "comments": f.get("comments"),
            "date": f.get("created_at").strftime("%Y-%m-%d %H:%M:%S") if f.get("created_at") else None
        })
    return jsonify(feedbacks)

@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    user_objid = current_user_objid()
    if not user_objid:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    course_name = data.get("courseName")
    rating = data.get("rating")
    comments = data.get("comments")

    if not course_name or rating is None or not comments:
        return jsonify({"error": "All fields are required"}), 400

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid rating"}), 400

    doc = {
        "user_id": user_objid,
        "course_name": course_name,
        "rating": rating,
        "comments": comments,
        "created_at": datetime.utcnow()
    }

    try:
        res = db.feedback.insert_one(doc)
    except Exception as e:
        logger.exception("Failed to save feedback: %s", e)
        return jsonify({"error": "Failed to save feedback"}), 500

    return jsonify({
        "success": True,
        "feedback": {
            "id": str(res.inserted_id),
            "courseName": course_name,
            "rating": rating,
            "comments": comments,
            "date": doc["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        }
    })

@app.route("/api/feedback/clear", methods=["DELETE"])
def clear_feedback():
    user_objid = current_user_objid()
    if not user_objid:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        db.feedback.delete_many({"user_id": user_objid})
    except Exception as e:
        logger.exception("Failed to clear feedback: %s", e)
        return jsonify({"error": "Failed to clear feedback"}), 500

    return jsonify({"success": True})

# --- Local run (for development)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting local server on port %s", port)
    app.run(host="0.0.0.0", port=port, debug=False)
