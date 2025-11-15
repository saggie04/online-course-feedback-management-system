from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
CORS(app, supports_credentials=True)

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError(
            'DATABASE_URL not set. Please:\n'
            '1. Click the PostgreSQL icon in the Tools pane\n'
            '2. Ensure the database is created\n'
            '3. Restart the server'
        )
    return psycopg2.connect(database_url)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            course_name VARCHAR(255) NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comments TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    return app.send_static_file('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT id, email, password_hash FROM users WHERE email = %s', (email,))
    user = cur.fetchone()
    
    if not user:
        password_hash = generate_password_hash(password)
        cur.execute('INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, email', (email, password_hash))
        user_result = cur.fetchone()
        conn.commit()
        
        if user_result:
            session['user_id'] = user_result[0]
            session['email'] = user_result[1]
            
            cur.close()
            conn.close()
            
            return jsonify({'success': True, 'email': user_result[1]})
    else:
        if check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['email'] = user[1]
            
            cur.close()
            conn.close()
            
            return jsonify({'success': True, 'email': user[1]})
        else:
            cur.close()
            conn.close()
            return jsonify({'error': 'Invalid email or password'}), 401
    
    cur.close()
    conn.close()
    return jsonify({'error': 'Login failed'}), 500

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
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT id, course_name, rating, comments, created_at 
        FROM feedback 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    ''', (user_id,))
    
    feedbacks = []
    for row in cur.fetchall():
        feedbacks.append({
            'id': row[0],
            'courseName': row[1],
            'rating': row[2],
            'comments': row[3],
            'date': row[4].strftime('%Y-%m-%d %H:%M:%S')
        })
    
    cur.close()
    conn.close()
    
    return jsonify(feedbacks)

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    course_name = data.get('courseName')
    rating = data.get('rating')
    comments = data.get('comments')
    
    if not course_name or not rating or not comments:
        return jsonify({'error': 'All fields are required'}), 400
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rating'}), 400
    
    user_id = session['user_id']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO feedback (user_id, course_name, rating, comments) 
        VALUES (%s, %s, %s, %s)
        RETURNING id, created_at
    ''', (user_id, course_name, rating, comments))
    
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    if not result:
        return jsonify({'error': 'Failed to save feedback'}), 500
    
    return jsonify({
        'success': True,
        'feedback': {
            'id': result[0],
            'courseName': course_name,
            'rating': rating,
            'comments': comments,
            'date': result[1].strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@app.route('/api/feedback/clear', methods=['DELETE'])
def clear_feedback():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('DELETE FROM feedback WHERE user_id = %s', (user_id,))
    conn.commit()
    
    cur.close()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
