# app.py
import os
import logging
from datetime import datetime
from bson.objectid import ObjectId

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# --- configuration & logging ---
load_dotenv()  # load .env in development

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "coursefeedback")
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-me")

# set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("course-feedback")

# --- serverless-safe Mongo connection (lazy + cached) ---
_mongo_client = None

def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        if not MONGO_URI:
            raise RuntimeError("MONGO_URI not set in environment")
        # small timeout so serverless fails fast if cannot reach DB
        _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _mongo_client

def get_db():
    client = get_mongo_client()
    return client[DB_NAME]

# ensure index creation is safe (call once per warm instance)
def ensure_indexes():
    try:
        db = get_db()
        db.users.create_index([("email", ASCENDING)], unique=True)
        db.feedback.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
    except Exception as e:
        logger.warning("Could not ensure indexes: %s", e)

# --- Flask app setup ---
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = SESSION_SECRET
CORS(app, supports_credentials=True)

# run index
@app.route("/")
def index():
    # serve login.html by default (exists in static folder)
    return app.send_static_file("login.html")

def current_user_objid():
    """Return ObjectId of current user (or None)"""
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        return ObjectId(user_id)
    except Exception:
        return None

# --- AUTH / USER ROUTES ---
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db = get_db()
    users = db.users

    user = users.find_one({"email": email})
    if not user:
        # create user
        password_hash = generate_password_hash(password)
        try:
            res = users.insert_one({
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.utcnow()
            })
        except Exception as e:
            logger.exception("Failed to create user: %s", e)
            return jsonify({"error": "Failed to create user"}), 500

        session["user_id"] = str(res.inserted_id)
        session["email"] = email
        return jsonify({"success": True, "email": email})

    # check password
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

# --- FEEDBACK ROUTES ---
@app.route("/api/feedback", methods=["GET"])
def get_feedback():
    user_objid = current_user_objid()
    if not user_objid:
        return jsonify({"error": "Not authenticated"}), 401

    db = get_db()
    feedback_cursor = db.feedback.find({"user_id": user_objid}).sort("created_at", -1)
    feedbacks = []
    for f in feedback_cursor:
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

    new_doc = {
        "user_id": user_objid,
        "course_name": course_name,
        "rating": rating,
        "comments": comments,
        "created_at": datetime.utcnow()
    }

    db = get_db()
    res = db.feedback.insert_one(new_doc)
    if not res.inserted_id:
        return jsonify({"error": "Failed to save feedback"}), 500

    return jsonify({
        "success": True,
        "feedback": {
            "id": str(res.inserted_id),
            "courseName": course_name,
            "rating": rating,
            "comments": comments,
            "date": new_doc["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        }
    })

@app.route("/api/feedback/clear", methods=["DELETE"])
def clear_feedback():
    user_objid = current_user_objid()
    if not user_objid:
        return jsonify({"error": "Not authenticated"}), 401

    db = get_db()
    db.feedback.delete_many({"user_id": user_objid})
    return jsonify({"success": True})

# --- health endpoint for deployment checks ---
@app.route("/healthz", methods=["GET"])
def healthz():
    try:
        # quick DB ping (serverSelectionTimeoutMS ensures this returns fast if unreachable)
        client = get_mongo_client()
        client.admin.command("ping")
        return jsonify({"ok": True})
    except Exception as e:
        logger.exception("Health check failed: %s", e)
        return jsonify({"ok": False, "error": str(e)}), 500

# ensure indexes on warm start
try:
    ensure_indexes()
except Exception:
    # index creation non-fatal; log and continue
    logger.exception("Index creation attempt failed on startup")

# --- run server (development) ---
if __name__ == "__main__":
    # In production, run with gunicorn or on a platform (Render, Railway etc.)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
