import os
import gc
import sqlite3
import logging
from datetime import timedelta
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from utils.gemini_model import analyze_image_with_gemini

# 1. Initialize App & Logging
app = Flask(__name__)
app.secret_key = "visionverse_2026"
app.permanent_session_lifetime = timedelta(days=30) 
logging.basicConfig(level=logging.INFO)

# 2. Database Initialization
def init_db():
    with sqlite3.connect("users.db") as conn:
        # Schema: id, name, email, phone (UNIQUE), password
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            email TEXT, 
            phone TEXT UNIQUE, 
            password TEXT)''')
        conn.commit()

init_db()

# 3. System Configurations
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 4. Global Headers
@app.after_request
def apply_strict_cache_invalidation(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# 5. Auth Routes
@app.route('/auth')
def auth_page():
    if 'user' in session: return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    try:
        hashed = generate_password_hash(data['password'])
        with sqlite3.connect("users.db") as conn:
            conn.execute("INSERT INTO users (name, email, phone, password) VALUES (?,?,?,?)", 
                         (data['name'], data['email'], data['phone'], hashed))
            conn.commit()
        return jsonify({"success": "Account created!"})
    except Exception as e:
        logging.error(f"Signup error: {e}")
        return jsonify({"error": "Phone number already exists"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    with sqlite3.connect("users.db") as conn:
        # Check using phone number
        user = conn.execute("SELECT * FROM users WHERE phone = ?", (data['phone'],)).fetchone()
    
    # user[4] is password index (0:id, 1:name, 2:email, 3:phone, 4:password)
    if user and check_password_hash(user[4], data['password']):
        session.permanent = True
        session['user'] = data['phone'] 
        return jsonify({"success": "Logged in"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_page'))

@app.route('/get_profile')
def get_profile():
    if 'user' not in session: return jsonify({"error": "Not logged in"}), 401
    with sqlite3.connect("users.db") as conn:
        user = conn.execute("SELECT name, email, phone FROM users WHERE phone = ?", (session['user'],)).fetchone()
    if user:
        return jsonify({"name": user[0], "email": user[1], "phone": user[2]})
    return jsonify({"error": "User not found"}), 404

# 6. Main App Routes
@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('auth_page'))
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def handle_analysis_request():
    if 'image' not in request.files: return jsonify({"error": "No image"}), 400
    file = request.files['image']
    try:
        image_bytes = file.read()
        analysis_data = analyze_image_with_gemini(image_bytes)
        return jsonify(analysis_data), 200
    except Exception as e:
        logging.error(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        gc.collect()

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)