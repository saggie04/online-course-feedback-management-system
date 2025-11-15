# app.py — MongoDB version
import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# load .env with MONGO_URI and DB_NAME
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "coursefeedback")

# connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ensure useful indexes (email unique, feedback by user)
db.users.create_index([("email", ASCENDING)], unique=True)
db.feedback.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])

print("✅ Connected to MongoDB:", DB_NAME)

# Flask app setup
app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
CORS(app, supports_credentials=True)


@app.route('/')
def index():
    return app.send_static_file('login.html')


# helper: get current user id as ObjectId (returns None if not logged in)
def current_user_objid():
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        return ObjectId(user_id)
    except Exception:
        return None


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    email = (data.get('email') or "").strip().lower()
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    users_col = db.users
    user = users_col.find_one({"email": email})

    # If user doesn't exist, create (same behaviour as original)
    if not user:
        password_hash = generate_password_hash(password)
        try:
            res = users_col.insert_one({
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.utcnow()
            })
        except Exception as e:
            # if insertion fails e.g. duplicate, return error
            return jsonify({'error': 'Failed to create user', 'detail': str(e)}), 500

        session['user_id'] = str(res.inserted_id)
        session['email'] = email
        return jsonify({'success': True, 'email': email})

    # existing user -> verify password
    if check_password_hash(user.get("password_hash", ""), password):
        session['user_id'] = str(user["_id"])
        session['email'] = user["email"]
        return jsonify({'success': True, 'email': user["email"]})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'email': session.get('email')})
    return jsonify({'authenticated': False})


@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    user_objid = current_user_objid()
    if not user_objid:
        return jsonify({'error': 'Not authenticated'}), 401

    feedback_docs = db.feedback.find({"user_id": user_objid}).sort("created_at", -1)
    feedbacks = []
    for f in feedback_docs:
        feedbacks.append({
            'id': str(f.get('_id')),
            'courseName': f.get('course_name'),
            'rating': f.get('rating'),
            'comments': f.get('comments'),
            'date': f.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if f.get('created_at') else None
        })
    return jsonify(feedbacks)


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    user_objid = current_user_objid()
    if not user_objid:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    course_name = data.get('courseName')
    rating = data.get('rating')
    comments = data.get('comments')

    if not course_name or rating is None or not comments:
        return jsonify({'error': 'All fields are required'}), 400

    # validate rating
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid rating'}), 400

    now = datetime.utcnow()
    new_doc = {
        "user_id": user_objid,
        "course_name": course_name,
        "rating": rating,
        "comments": comments,
        "created_at": now
    }

    res = db.feedback.insert_one(new_doc)
    if not res.inserted_id:
        return jsonify({'error': 'Failed to save feedback'}), 500

    return jsonify({
        'success': True,
        'feedback': {
            'id': str(res.inserted_id),
            'courseName': course_name,
            'rating': rating,
            'comments': comments,
            'date': now.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


@app.route('/api/feedback/clear', methods=['DELETE'])
def clear_feedback():
    user_objid = current_user_objid()
    if not user_objid:
        return jsonify({'error': 'Not authenticated'}), 401

    db.feedback.delete_many({"user_id": user_objid})
    return jsonify({'success': True})


if __name__ == '__main__':
    # no SQL init required for MongoDB
    app.run(host='0.0.0.0', port=5000, debug=True)
