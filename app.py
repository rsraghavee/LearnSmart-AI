"""
LearnSmart AI - Main Flask Application
=======================================

COMPLETE SYSTEM OVERVIEW:
=========================
LearnSmart AI is a comprehensive intelligent learning management system that helps
students optimize their study habits through data analytics, machine learning,
and natural language processing.

MAIN MODULES:
=============

1. AUTHENTICATION MODULE
   - Secure user registration (name, email, username, password)
   - bcrypt password hashing (12 rounds, automatic salt generation)
   - Session-based authentication with secure cookies
   - Protected routes with authentication decorators
   - Client and server-side form validation

2. STUDY PATTERN ANALYZER MODULE
   - Daily study data collection (study hours, sleep, breaks, screen time, mood)
   - MySQL database storage with user linking
   - One entry per day (auto-updates existing entries)
   - Recent history display

3. PRODUCTIVITY SCORE CALCULATOR MODULE
   - Rule-based scoring algorithm (0-100 scale)
   - Component weights: Study (30%), Sleep (30%), Break (20%), Screen (20%)
   - Optimal range-based scoring
   - Configurable weights and ranges
   - Clear formula documentation

4. BURNOUT RISK PREDICTION MODULE (Machine Learning)
   - Decision Tree Classifier (default) or Logistic Regression
   - Features: study_hours, sleep_hours, break_time, screen_time, mood_score
   - Output: Low/Medium/High burnout risk with confidence
   - Model accuracy: ~85-90% (Decision Tree), ~80-85% (Logistic Regression)
   - Automatic prediction on study data submission

5. AI CHATBOT MODULE (Google Gemini)
   - PDF and text file upload support with document processing
   - Text extraction using PyPDF2
   - Integration with Google Gemini API
   - Document-based context for intelligent responses
   - Stores conversation history
   - Unified interface for upload and chat

6. STUDY SUGGESTIONS MODULE
   - Rule-based recommendation engine
   - Analyzes: sleep, study hours, breaks, screen time, mood, productivity, burnout risk
   - Priority-based suggestions (High/Medium/Low)
   - Non-medical, student-friendly language
   - Personalized to each user's patterns

8. STUDENT DASHBOARD MODULE
   - Productivity score display with breakdown
   - Burnout risk visualization
   - Interactive charts (Chart.js):
     * Weekly study hours (bar chart)
     * Sleep vs productivity correlation (dual-axis line chart)
   - Recent study history
   - Personalized suggestions display

9. HISTORY MANAGEMENT MODULE
   - Study pattern history (all entries)
   - Burnout prediction history (all ML predictions)
   - Generated questions history (all NLP questions)
   - Tabbed interface for easy navigation
   - Tabular display format
   - Proper database relationships maintained

TECHNOLOGY STACK:
=================
- Backend: Flask 3.0.0 (Python web framework)
- Database: MySQL (Flask-MySQLdb connector)
- ML: scikit-learn 1.3.2 (Decision Tree, Logistic Regression)
- NLP: Custom algorithms (keyword frequency, sentence scoring)
- PDF: PyPDF2 3.0.1
- Security: bcrypt 4.1.2 (password hashing)
- Frontend: HTML5, CSS3, JavaScript (ES6+), Chart.js 4.4.0

DATABASE ARCHITECTURE:
======================
- users (parent table)
  ├── study_patterns (child, FK: user_id)
  ├── burnout_predictions (child, FK: user_id)
  └── generated_questions (child, FK: user_id)
- courses (independent)
- user_progress (junction table)

All foreign keys use CASCADE DELETE for data integrity.

SECURITY FEATURES:
==================
- bcrypt password hashing (12 rounds)
- Session-based authentication
- SQL injection prevention (parameterized queries)
- Input validation (client and server-side)
- User data isolation (user_id filtering)
- Secure file upload handling
- Session security (HttpOnly, SameSite flags)

FOR VIVA PRESENTATION:
======================
This application demonstrates:
- Full-stack web development
- Database design and relationships
- Machine learning integration
- Natural language processing
- Data visualization
- Security best practices
- RESTful API design

All code is well-commented and explainable for academic presentations.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_mysqldb import MySQL
import os
import re
import bcrypt
from datetime import timedelta, date
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
import joblib
import numpy as np
from werkzeug.utils import secure_filename
import PyPDF2
import io
from collections import Counter
import string
import unicodedata

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configure secret key for sessions (used to sign session cookies)
# IMPORTANT: Change this to a random string in production
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure session settings for security
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Session expires after 24 hours
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# MySQL Database Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'learnsmart_ai')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_CHARSET'] = 'utf8mb4'

# Initialize MySQL
mysql = MySQL(app)

# File upload configuration for AI Chatbot
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def init_database():
    """
    Initialize the database and create necessary tables if they don't exist.
    This function should be called once to set up the database schema.
    
    DATABASE SCHEMA:
    - users table: Stores student registration data
      * id: Primary key (auto-increment)
      * name: Student's full name
      * username: Unique username for login
      * email: Unique email address (also used for login)
      * password: Hashed password (bcrypt hash, 60 characters)
      * created_at: Registration timestamp
    """
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Create users table with name field and increased password length for bcrypt hash
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                instructor VARCHAR(100),
                duration INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create user_progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                course_id INT,
                progress_percentage INT DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)
        
        # Create study_patterns table for Study Pattern Analyzer
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_patterns (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                study_date DATE NOT NULL,
                study_hours DECIMAL(4,2) NOT NULL,
                sleep_hours DECIMAL(4,2) NOT NULL,
                break_time DECIMAL(4,2) NOT NULL,
                screen_time DECIMAL(4,2) NOT NULL,
                mood_level ENUM('Low', 'Medium', 'High') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_date (user_id, study_date)
            )
        """)
        
        # Create burnout_predictions table for storing ML predictions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS burnout_predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                study_date DATE NOT NULL,
                study_hours DECIMAL(4,2) NOT NULL,
                sleep_hours DECIMAL(4,2) NOT NULL,
                break_time DECIMAL(4,2) NOT NULL,
                screen_time DECIMAL(4,2) NOT NULL,
                mood_score INT NOT NULL,
                predicted_risk ENUM('Low', 'Medium', 'High') NOT NULL,
                confidence DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_date_prediction (user_id, study_date)
            )
        """)
        
        # Create user_documents table to store uploaded documents and extracted text for AI chatbot
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_type ENUM('PDF', 'TEXT') NOT NULL,
                extracted_text LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create chat_conversations table for AI Chatbot
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                document_id INT,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (document_id) REFERENCES user_documents(id) ON DELETE SET NULL,
                INDEX idx_user_id (user_id),
                INDEX idx_document_id (document_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Create academic_performance table for Academic Performance Tracker
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS academic_performance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                class_semester VARCHAR(100) NOT NULL,
                exam_name VARCHAR(100) NOT NULL,
                subject_name VARCHAR(100) NOT NULL,
                marks_scored DECIMAL(6,2) NOT NULL,
                total_marks DECIMAL(6,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_class_semester (user_id, class_semester)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        cursor.close()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")


# ============================================================================
# AUTHENTICATION HELPER FUNCTIONS
# ============================================================================

def hash_password(password):
    """
    Hash a password using bcrypt algorithm.
    
    HOW IT WORKS:
    1. Generates a random salt (unique for each password)
    2. Combines salt with password
    3. Hashes using bcrypt (adaptive hashing algorithm)
    4. Returns a string containing salt + hash (60 characters)
    
    SECURITY FEATURES:
    - Salt prevents rainbow table attacks
    - bcrypt is computationally expensive (slows brute force attacks)
    - Each password gets unique salt (even same passwords have different hashes)
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password (bcrypt hash)
    """
    # Generate salt and hash password
    # bcrypt automatically generates a random salt
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds = good balance of security and performance
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password, hashed_password):
    """
    Verify a password against its hash.
    
    HOW IT WORKS:
    1. Extracts salt from stored hash
    2. Hashes the provided password with the same salt
    3. Compares the two hashes
    4. Returns True if they match, False otherwise
    
    Args:
        password (str): Plain text password to verify
        hashed_password (str): Stored bcrypt hash
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def validate_registration_data(name, username, email, password):
    """
    Validate registration form data (server-side validation).
    
    VALIDATION RULES:
    - Name: 2-100 characters, letters and spaces only
    - Username: 3-50 characters, alphanumeric and underscore only
    - Email: Valid email format
    - Password: Minimum 8 characters, at least one letter and one number
    
    Args:
        name (str): Student's full name
        username (str): Desired username
        email (str): Email address
        password (str): Password
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    errors = []
    
    # Validate name
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters long")
    elif len(name) > 100:
        errors.append("Name must be less than 100 characters")
    elif not re.match(r'^[a-zA-Z\s]+$', name):
        errors.append("Name can only contain letters and spaces")
    
    # Validate username
    if not username or len(username) < 3:
        errors.append("Username must be at least 3 characters long")
    elif len(username) > 50:
        errors.append("Username must be less than 50 characters")
    elif not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors.append("Username can only contain letters, numbers, and underscores")
    
    # Validate email
    try:
        validate_email(email)
    except EmailNotValidError:
        errors.append("Invalid email address format")
    
    # Validate password
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    elif not re.search(r'[a-zA-Z]', password):
        errors.append("Password must contain at least one letter")
    elif not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    
    if errors:
        return False, "; ".join(errors)
    return True, ""


def is_authenticated():
    """
    Check if user is currently authenticated (has valid session).
    
    SESSION MANAGEMENT:
    - Session stores user_id and username after successful login
    - Session expires after 24 hours (configured in app.config)
    - Session is stored in encrypted cookie (signed with secret_key)
    
    Returns:
        bool: True if user is authenticated, False otherwise
    """
    return 'user_id' in session and 'username' in session


def require_auth(f):
    """
    Decorator to protect routes that require authentication.
    Redirects to login if user is not authenticated.
    
    Usage:
        @app.route('/dashboard')
        @require_auth
        def dashboard():
            ...
    """
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """
    Home page route - renders the main landing page.
    If user is already logged in, redirect to dashboard.
    """
    # Check if user is already logged in
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route - handles user authentication.
    
    AUTHENTICATION FLOW:
    ====================
    1. GET Request: Display login form
    2. POST Request: Process login credentials
       a. Get username/email and password from form
       b. Query database for user by username OR email
       c. If user found, verify password using bcrypt
       d. If password matches, create session
       e. Redirect to dashboard
       f. If invalid, return error message
    
    SECURITY FEATURES:
    - Passwords are never stored in plain text
    - Uses bcrypt for password verification
    - Parameterized queries prevent SQL injection
    - Session-based authentication (no tokens in URL)
    - Generic error messages (don't reveal if user exists)
    
    GET: Displays login page (redirects to dashboard if already logged in)
    POST: Processes login credentials and creates session
    """
    # If already logged in, redirect to dashboard
    if is_authenticated():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get form data
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Basic validation
        if not username_or_email or not password:
            return jsonify({'success': False, 'message': 'Username/Email and password are required'})
        
        try:
            conn = mysql.connect
            cursor = conn.cursor()
            
            # Query user by username OR email (allows login with either)
            # Using parameterized query to prevent SQL injection
            cursor.execute(
                "SELECT id, username, email, name, password FROM users WHERE username = %s OR email = %s",
                (username_or_email, username_or_email)
            )
            user = cursor.fetchone()
            
            cursor.close()
            
            if user:
                # Verify password using bcrypt
                # This compares the provided password with the stored hash
                if verify_password(password, user['password']):
                    # Password is correct - create session
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['name'] = user['name']
                    session['email'] = user['email']
                    
                    # Make session permanent (respects PERMANENT_SESSION_LIFETIME)
                    session.permanent = True
                    
                    return jsonify({
                        'success': True, 
                        'message': 'Login successful! Redirecting...',
                        'redirect': url_for('dashboard')
                    })
                else:
                    # Password is incorrect
                    # Generic message (don't reveal if user exists)
                    return jsonify({'success': False, 'message': 'Invalid username/email or password'})
            else:
                # User not found
                # Generic message (don't reveal if user exists)
                return jsonify({'success': False, 'message': 'Invalid username/email or password'})
                
        except Exception as e:
            print(f"Login error: {str(e)}")  # Log error for debugging
            return jsonify({'success': False, 'message': 'An error occurred. Please try again.'})
    
    # GET request - show login page
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration route - handles new student registration.
    
    REGISTRATION FLOW:
    ==================
    1. GET Request: Display registration form
    2. POST Request: Process registration
       a. Get name, username, email, password from form
       b. Validate all fields (server-side validation)
       c. Check if username or email already exists
       d. Hash password using bcrypt
       e. Insert new user into database
       f. Return success message
    
    SECURITY FEATURES:
    - Password hashing with bcrypt before storage
    - Server-side validation (can't be bypassed)
    - Parameterized queries prevent SQL injection
    - Email format validation
    - Password strength requirements
    
    DATABASE OPERATIONS:
    - Stores: name, username, email, hashed_password
    - Enforces uniqueness on username and email
    - Auto-generates id and created_at timestamp
    
    GET: Displays registration page (redirects to dashboard if already logged in)
    POST: Processes registration data and creates new user account
    """
    # If already logged in, redirect to dashboard
    if is_authenticated():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get form data and strip whitespace
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()  # Normalize email to lowercase
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Server-side validation
        is_valid, error_message = validate_registration_data(name, username, email, password)
        
        if not is_valid:
            return jsonify({'success': False, 'message': error_message})
        
        # Check password confirmation matches
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'})
        
        try:
            conn = mysql.connect
            cursor = conn.cursor()
            
            # Check if username or email already exists
            # This prevents duplicate accounts
            cursor.execute(
                "SELECT id, username, email FROM users WHERE username = %s OR email = %s",
                (username, email)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.close()
                if existing_user['username'] == username:
                    return jsonify({'success': False, 'message': 'Username already exists'})
                else:
                    return jsonify({'success': False, 'message': 'Email already registered'})
            
            # Hash password before storing
            # NEVER store plain text passwords!
            hashed_password = hash_password(password)
            
            # Insert new user into database
            # Using parameterized query to prevent SQL injection
            cursor.execute(
                "INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)",
                (name, username, email, hashed_password)
            )
            conn.commit()
            cursor.close()
            
            return jsonify({
                'success': True, 
                'message': 'Registration successful! Redirecting to login...',
                'redirect': url_for('login')
            })
            
        except Exception as e:
            print(f"Registration error: {str(e)}")  # Log error for debugging
            return jsonify({'success': False, 'message': 'An error occurred. Please try again.'})
    
    # GET request - show registration page
    return render_template('register.html')


# ============================================================================
# PRODUCTIVITY SCORE CALCULATION MODULE
# ============================================================================

def calculate_productivity_score(study_hours, sleep_hours, break_time, screen_time):
    """
    Calculate Productivity Score out of 100 based on study patterns.
    
    FORMULA EXPLANATION:
    ====================
    The productivity score is calculated using a weighted formula where each
    component (Study Hours, Sleep Hours, Break Time, Screen Time) contributes
    a portion to the total score of 100.
    
    SCORING COMPONENTS:
    -------------------
    1. STUDY HOURS (Weight: 30 points)
       - Optimal: 6-8 hours per day
       - Score decreases if too low (< 4 hours) or too high (> 10 hours)
       - Formula: Linear scoring based on optimal range
    
    2. SLEEP HOURS (Weight: 30 points)
       - Optimal: 7-9 hours (recommended for students)
       - Score decreases if too little (< 6 hours) or too much (> 10 hours)
       - Formula: Bell curve centered at 8 hours
    
    3. BREAK TIME (Weight: 20 points)
       - Optimal: 1-3 hours per day
       - Too little (< 0.5h) or too much (> 5h) reduces score
       - Formula: Optimal range scoring
    
    4. SCREEN TIME (Weight: 20 points)
       - Less is better, but some is necessary
       - Optimal: 4-6 hours (reasonable for study/work)
       - Score decreases significantly if > 10 hours
       - Formula: Inverse scoring (less = better, with minimum threshold)
    
    TOTAL SCORE = Study Score + Sleep Score + Break Score + Screen Score
    (Maximum: 100 points)
    
    Args:
        study_hours (float): Hours spent studying
        sleep_hours (float): Hours of sleep
        break_time (float): Hours of break/rest
        screen_time (float): Total screen time
    
    Returns:
        dict: Contains total_score (0-100) and component scores
    """
    
    # ========================================================================
    # CONFIGURABLE WEIGHTS - Easy to modify for different scoring systems
    # ========================================================================
    WEIGHT_STUDY = 30    # Weight for study hours (out of 100)
    WEIGHT_SLEEP = 30     # Weight for sleep hours (out of 100)
    WEIGHT_BREAK = 20     # Weight for break time (out of 100)
    WEIGHT_SCREEN = 20    # Weight for screen time (out of 100)
    
    # Optimal ranges for each component
    STUDY_OPTIMAL_MIN = 4.0   # Minimum good study hours
    STUDY_OPTIMAL_MAX = 8.0   # Maximum good study hours
    STUDY_PEAK = 6.0          # Peak study hours (best score)
    
    SLEEP_OPTIMAL_MIN = 7.0   # Minimum good sleep hours
    SLEEP_OPTIMAL_MAX = 9.0   # Maximum good sleep hours
    SLEEP_PEAK = 8.0          # Peak sleep hours (best score)
    
    BREAK_OPTIMAL_MIN = 1.0   # Minimum good break time
    BREAK_OPTIMAL_MAX = 3.0   # Maximum good break time
    BREAK_PEAK = 2.0          # Peak break time (best score)
    
    SCREEN_OPTIMAL_MAX = 6.0  # Maximum good screen time
    SCREEN_PENALTY_START = 8.0  # Start penalizing after this
    
    # ========================================================================
    # 1. STUDY HOURS SCORE (0 to WEIGHT_STUDY points)
    # ========================================================================
    if study_hours < STUDY_OPTIMAL_MIN:
        # Too little study: Linear decrease from 0 hours
        study_score = (study_hours / STUDY_OPTIMAL_MIN) * WEIGHT_STUDY * 0.5
    elif study_hours <= STUDY_OPTIMAL_MAX:
        # Optimal range: Peak at STUDY_PEAK, linear interpolation
        if study_hours <= STUDY_PEAK:
            # Increasing to peak
            study_score = WEIGHT_STUDY * (study_hours / STUDY_PEAK)
        else:
            # Decreasing from peak
            study_score = WEIGHT_STUDY * (1 - (study_hours - STUDY_PEAK) / (STUDY_OPTIMAL_MAX - STUDY_PEAK))
    else:
        # Too much study: Penalty for over-studying
        excess = study_hours - STUDY_OPTIMAL_MAX
        penalty = min(excess * 5, WEIGHT_STUDY * 0.5)  # Max 50% penalty
        study_score = max(WEIGHT_STUDY * 0.5 - penalty, 0)
    
    study_score = max(0, min(WEIGHT_STUDY, study_score))  # Clamp 0-WEIGHT_STUDY
    
    # ========================================================================
    # 2. SLEEP HOURS SCORE (0 to WEIGHT_SLEEP points)
    # ========================================================================
    if sleep_hours < SLEEP_OPTIMAL_MIN:
        # Too little sleep: Linear decrease
        sleep_score = (sleep_hours / SLEEP_OPTIMAL_MIN) * WEIGHT_SLEEP * 0.7
    elif sleep_hours <= SLEEP_OPTIMAL_MAX:
        # Optimal range: Peak at SLEEP_PEAK
        if sleep_hours <= SLEEP_PEAK:
            sleep_score = WEIGHT_SLEEP * (0.7 + 0.3 * (sleep_hours / SLEEP_PEAK))
        else:
            sleep_score = WEIGHT_SLEEP * (1 - 0.3 * (sleep_hours - SLEEP_PEAK) / (SLEEP_OPTIMAL_MAX - SLEEP_PEAK))
    else:
        # Too much sleep: Penalty
        excess = sleep_hours - SLEEP_OPTIMAL_MAX
        penalty = min(excess * 3, WEIGHT_SLEEP * 0.4)
        sleep_score = max(WEIGHT_SLEEP * 0.6 - penalty, 0)
    
    sleep_score = max(0, min(WEIGHT_SLEEP, sleep_score))  # Clamp 0-WEIGHT_SLEEP
    
    # ========================================================================
    # 3. BREAK TIME SCORE (0 to WEIGHT_BREAK points)
    # ========================================================================
    if break_time < BREAK_OPTIMAL_MIN:
        # Too little break: Linear increase
        break_score = (break_time / BREAK_OPTIMAL_MIN) * WEIGHT_BREAK * 0.6
    elif break_time <= BREAK_OPTIMAL_MAX:
        # Optimal range: Peak at BREAK_PEAK
        if break_time <= BREAK_PEAK:
            break_score = WEIGHT_BREAK * (0.6 + 0.4 * (break_time / BREAK_PEAK))
        else:
            break_score = WEIGHT_BREAK * (1 - 0.4 * (break_time - BREAK_PEAK) / (BREAK_OPTIMAL_MAX - BREAK_PEAK))
    else:
        # Too much break: Penalty
        excess = break_time - BREAK_OPTIMAL_MAX
        penalty = min(excess * 4, WEIGHT_BREAK * 0.5)
        break_score = max(WEIGHT_BREAK * 0.5 - penalty, 0)
    
    break_score = max(0, min(WEIGHT_BREAK, break_score))  # Clamp 0-WEIGHT_BREAK
    
    # ========================================================================
    # 4. SCREEN TIME SCORE (0 to WEIGHT_SCREEN points)
    # ========================================================================
    # Less screen time is better, but some is necessary
    if screen_time <= SCREEN_OPTIMAL_MAX:
        # Good range: Full points, slight decrease as it approaches max
        screen_score = WEIGHT_SCREEN * (1 - (screen_time / SCREEN_OPTIMAL_MAX) * 0.2)
    elif screen_time <= SCREEN_PENALTY_START:
        # Moderate: Linear decrease
        excess = screen_time - SCREEN_OPTIMAL_MAX
        penalty = (excess / (SCREEN_PENALTY_START - SCREEN_OPTIMAL_MAX)) * WEIGHT_SCREEN * 0.5
        screen_score = WEIGHT_SCREEN * 0.8 - penalty
    else:
        # Too much: Heavy penalty
        excess = screen_time - SCREEN_PENALTY_START
        penalty = min(excess * 2, WEIGHT_SCREEN * 0.7)
        screen_score = max(WEIGHT_SCREEN * 0.3 - penalty, 0)
    
    screen_score = max(0, min(WEIGHT_SCREEN, screen_score))  # Clamp 0-WEIGHT_SCREEN
    
    # ========================================================================
    # CALCULATE TOTAL SCORE
    # ========================================================================
    total_score = study_score + sleep_score + break_score + screen_score
    
    # Round to 1 decimal place for display
    total_score = round(total_score, 1)
    study_score = round(study_score, 1)
    sleep_score = round(sleep_score, 1)
    break_score = round(break_score, 1)
    screen_score = round(screen_score, 1)
    
    return {
        'total_score': total_score,
        'study_score': study_score,
        'sleep_score': sleep_score,
        'break_score': break_score,
        'screen_score': screen_score,
        'study_hours': study_hours,
        'sleep_hours': sleep_hours,
        'break_time': break_time,
        'screen_time': screen_time
    }


# ============================================================================
# SUGGESTIONS AND INSIGHTS MODULE (Rule-Based Logic)
# ============================================================================

def generate_study_suggestions(study_hours, sleep_hours, break_time, screen_time, mood_level, productivity_score=None, burnout_risk=None):
    """
    Generate personalized study improvement suggestions using rule-based logic.
    
    SUGGESTION GENERATION LOGIC:
    ============================
    This function analyzes study patterns and generates actionable, student-friendly
    suggestions based on specific conditions. The logic is rule-based, meaning it
    uses if-then conditions to identify areas for improvement.
    
    RULE CATEGORIES:
    1. Sleep-related suggestions (based on sleep hours)
    2. Study hours suggestions (based on study duration)
    3. Break time suggestions (based on rest periods)
    4. Screen time suggestions (based on digital usage)
    5. Overall balance suggestions (based on multiple factors)
    
    IMPORTANT NOTES:
    - All suggestions are educational and non-medical
    - Suggestions are student-friendly and actionable
    - Based on research-backed optimal ranges
    - Prioritized by impact on productivity and well-being
    
    Args:
        study_hours (float): Hours spent studying
        sleep_hours (float): Hours of sleep
        break_time (float): Hours of break/rest
        screen_time (float): Total screen time
        mood_level (str): 'Low', 'Medium', or 'High'
        productivity_score (dict, optional): Productivity score data
        burnout_risk (str, optional): 'Low', 'Medium', or 'High'
    
    Returns:
        list: List of suggestion dictionaries with title, description, priority, and category
    """
    suggestions = []
    
    # Priority levels: 'high', 'medium', 'low'
    # Categories: 'sleep', 'study', 'break', 'screen', 'balance', 'mood'
    
    # ========================================================================
    # SLEEP-RELATED SUGGESTIONS
    # ========================================================================
    
    if sleep_hours < 6:
        suggestions.append({
            'title': '⚠️ Increase Sleep Hours',
            'description': f'You\'re getting {sleep_hours:.1f} hours of sleep, which is below the recommended 7-9 hours. Adequate sleep improves memory consolidation, focus, and overall academic performance. Try to gradually increase your sleep to at least 7 hours.',
            'priority': 'high',
            'category': 'sleep',
            'icon': '😴'
        })
    elif sleep_hours < 7:
        suggestions.append({
            'title': '💤 Aim for More Sleep',
            'description': f'You\'re getting {sleep_hours:.1f} hours of sleep. While close to optimal, aiming for 7-9 hours can significantly boost your productivity and cognitive function. Consider going to bed 30-60 minutes earlier.',
            'priority': 'medium',
            'category': 'sleep',
            'icon': '💤'
        })
    elif sleep_hours > 10:
        suggestions.append({
            'title': '⏰ Review Sleep Schedule',
            'description': f'You\'re sleeping {sleep_hours:.1f} hours, which is above the typical 7-9 hour range. While rest is important, excessive sleep might indicate fatigue or poor sleep quality. Consider establishing a more consistent sleep schedule.',
            'priority': 'low',
            'category': 'sleep',
            'icon': '⏰'
        })
    
    # ========================================================================
    # STUDY HOURS SUGGESTIONS
    # ========================================================================
    
    if study_hours > 10:
        suggestions.append({
            'title': '📚 Reduce Study Hours',
            'description': f'You\'re studying {study_hours:.1f} hours per day, which exceeds the optimal 4-8 hour range. Extended study sessions can lead to diminishing returns, fatigue, and burnout. Consider breaking your study into shorter, focused sessions with regular breaks.',
            'priority': 'high',
            'category': 'study',
            'icon': '📚'
        })
    elif study_hours > 8:
        suggestions.append({
            'title': '⏱️ Optimize Study Duration',
            'description': f'You\'re studying {study_hours:.1f} hours daily. While dedication is commendable, studies show that 4-8 hours of focused study is most effective. Consider quality over quantity - shorter, focused sessions often yield better results.',
            'priority': 'medium',
            'category': 'study',
            'icon': '⏱️'
        })
    elif study_hours < 3:
        suggestions.append({
            'title': '📖 Increase Study Time',
            'description': f'You\'re studying {study_hours:.1f} hours per day. To make consistent progress, aim for at least 4-6 hours of focused study daily. Break it into manageable chunks throughout the day if needed.',
            'priority': 'medium',
            'category': 'study',
            'icon': '📖'
        })
    
    # ========================================================================
    # BREAK TIME SUGGESTIONS
    # ========================================================================
    
    if break_time < 0.5:
        suggestions.append({
            'title': '☕ Take More Breaks',
            'description': f'You\'re taking only {break_time:.1f} hours of breaks. Regular breaks are essential for maintaining focus and preventing mental fatigue. Aim for 1-3 hours of breaks throughout your study day. Try the Pomodoro Technique: 25 minutes study, 5 minutes break.',
            'priority': 'high',
            'category': 'break',
            'icon': '☕'
        })
    elif break_time < 1:
        suggestions.append({
            'title': '🌿 Increase Break Time',
            'description': f'You\'re taking {break_time:.1f} hours of breaks. Research shows that taking regular breaks (1-3 hours total) improves retention and prevents burnout. Consider adding short breaks every 1-2 hours of study.',
            'priority': 'medium',
            'category': 'break',
            'icon': '🌿'
        })
    elif break_time > 5:
        suggestions.append({
            'title': '⚖️ Balance Study and Breaks',
            'description': f'You\'re taking {break_time:.1f} hours of breaks, which is quite high. While rest is important, too many breaks can reduce study momentum. Aim for a balance: 1-3 hours of breaks for every 4-8 hours of study.',
            'priority': 'low',
            'category': 'break',
            'icon': '⚖️'
        })
    
    # ========================================================================
    # SCREEN TIME SUGGESTIONS
    # ========================================================================
    
    if screen_time > 12:
        suggestions.append({
            'title': '👁️ Reduce Screen Time',
            'description': f'You\'re spending {screen_time:.1f} hours on screens daily. Excessive screen time can cause eye strain, fatigue, and reduced focus. Try to limit screen time to 6-8 hours, take regular eye breaks (20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds), and consider offline study methods.',
            'priority': 'high',
            'category': 'screen',
            'icon': '👁️'
        })
    elif screen_time > 10:
        suggestions.append({
            'title': '💻 Manage Screen Usage',
            'description': f'You\'re spending {screen_time:.1f} hours on screens. While necessary for study, high screen time can impact sleep and eye health. Consider using blue light filters, taking regular breaks, and mixing in offline study activities like reading physical books or writing notes by hand.',
            'priority': 'medium',
            'category': 'screen',
            'icon': '💻'
        })
    
    # ========================================================================
    # BALANCE AND OVERALL SUGGESTIONS
    # ========================================================================
    
    # Check for multiple concerning patterns
    concerning_factors = 0
    if sleep_hours < 7:
        concerning_factors += 1
    if study_hours > 8:
        concerning_factors += 1
    if break_time < 1:
        concerning_factors += 1
    if screen_time > 10:
        concerning_factors += 1
    
    if concerning_factors >= 3:
        suggestions.append({
            'title': '⚖️ Rebalance Your Study Routine',
            'description': 'Multiple areas need attention. Consider creating a more balanced schedule: prioritize sleep (7-9h), moderate study hours (4-8h), include regular breaks (1-3h), and limit screen time (6-8h). A balanced approach leads to better long-term performance.',
            'priority': 'high',
            'category': 'balance',
            'icon': '⚖️'
        })
    
    # Productivity score based suggestions
    if productivity_score and productivity_score.get('total_score', 100) < 60:
        suggestions.append({
            'title': '📊 Improve Overall Productivity',
            'description': f'Your productivity score is {productivity_score.get("total_score", 0):.1f}/100. Focus on the areas with lowest scores in your breakdown. Small improvements in sleep, study balance, breaks, and screen time can significantly boost your overall productivity.',
            'priority': 'high',
            'category': 'balance',
            'icon': '📊'
        })
    
    # Burnout risk based suggestions
    if burnout_risk == 'High':
        suggestions.append({
            'title': '🚨 High Burnout Risk Detected',
            'description': 'Your study patterns indicate a high risk of burnout. Immediate action recommended: reduce study hours, prioritize sleep (7-9h), take more breaks, and limit screen time. Consider speaking with academic advisors or counselors for support.',
            'priority': 'high',
            'category': 'balance',
            'icon': '🚨'
        })
    elif burnout_risk == 'Medium':
        suggestions.append({
            'title': '⚠️ Monitor Burnout Risk',
            'description': 'You\'re at medium risk for burnout. Take proactive steps: ensure adequate sleep, maintain study-work-life balance, take regular breaks, and monitor your stress levels. Prevention is easier than recovery.',
            'priority': 'medium',
            'category': 'balance',
            'icon': '⚠️'
        })
    
    # Mood-based suggestions
    if mood_level == 'Low':
        suggestions.append({
            'title': '😊 Boost Your Mood',
            'description': 'Your mood level is low. Consider: taking regular breaks for activities you enjoy, getting adequate sleep, exercising, socializing, and maintaining a balanced study schedule. Remember, your well-being is as important as your studies.',
            'priority': 'medium',
            'category': 'mood',
            'icon': '😊'
        })
    
    # ========================================================================
    # POSITIVE REINFORCEMENT (when patterns are good)
    # ========================================================================
    
    # Check if most patterns are optimal
    optimal_count = 0
    if 7 <= sleep_hours <= 9:
        optimal_count += 1
    if 4 <= study_hours <= 8:
        optimal_count += 1
    if 1 <= break_time <= 3:
        optimal_count += 1
    if screen_time <= 8:
        optimal_count += 1
    
    if optimal_count >= 3 and len(suggestions) == 0:
        suggestions.append({
            'title': '✅ Great Study Habits!',
            'description': 'Your study patterns look excellent! You\'re maintaining a good balance between study, sleep, breaks, and screen time. Keep up the great work and continue monitoring your patterns to maintain this healthy routine.',
            'priority': 'low',
            'category': 'balance',
            'icon': '✅'
        })
    
    # Sort suggestions by priority (high first, then medium, then low)
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    # Limit to top 5 suggestions to avoid overwhelming the user
    return suggestions[:5]


def get_user_study_suggestions(user_id):
    """
    Get personalized study suggestions for a user based on their latest study pattern.
    
    This function retrieves the user's latest study pattern and generates
    personalized suggestions using rule-based logic.
    
    Args:
        user_id (int): User ID to get suggestions for
    
    Returns:
        list: List of suggestion dictionaries, or empty list if no data
    """
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Get the most recent study pattern
        cursor.execute("""
            SELECT study_hours, sleep_hours, break_time, screen_time, mood_level
            FROM study_patterns
            WHERE user_id = %s
            ORDER BY study_date DESC
            LIMIT 1
        """, (user_id,))
        
        pattern = cursor.fetchone()
        cursor.close()
        
        if not pattern:
            return []
        
        # Get productivity score and burnout prediction for context
        productivity_score = get_user_productivity_score(user_id)
        burnout_prediction = get_user_burnout_prediction(user_id)
        
        # Generate suggestions
        suggestions = generate_study_suggestions(
            float(pattern['study_hours']),
            float(pattern['sleep_hours']),
            float(pattern['break_time']),
            float(pattern['screen_time']),
            pattern['mood_level'],
            productivity_score,
            burnout_prediction['predicted_risk'] if burnout_prediction else None
        )
        
        return suggestions
        
    except Exception as e:
        print(f"Error getting study suggestions: {str(e)}")
        return []


# ============================================================================
# BURNOUT RISK PREDICTION MODULE (Machine Learning)
# ============================================================================

def load_burnout_model(model_path='burnout_model.pkl'):
    """
    Load the trained burnout risk prediction model.
    
    Returns:
        model: Trained Decision Tree classifier, or None if model not found
    """
    try:
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            return model
        else:
            print(f"Warning: Model file '{model_path}' not found. Please train the model first.")
            return None
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None


def mood_level_to_score(mood_level):
    """
    Convert mood level (Low/Medium/High) to numeric score (1-10).
    
    Args:
        mood_level (str): 'Low', 'Medium', or 'High'
    
    Returns:
        int: Numeric mood score (1-10)
    """
    mood_mapping = {
        'Low': 3,      # Low mood = 3 (on scale of 1-10)
        'Medium': 6,   # Medium mood = 6
        'High': 9      # High mood = 9
    }
    return mood_mapping.get(mood_level, 5)  # Default to 5 if unknown


def predict_burnout_risk(study_hours, sleep_hours, break_time, screen_time, mood_level):
    """
    Predict burnout risk using HYBRID LOGIC: Rule-based checks FIRST, then ML for borderline cases.
    
    PREDICTION APPROACH:
    ===================
    1. RULE-BASED LOGIC (Primary): Extreme patterns are caught by rules BEFORE ML
    2. ML SUPPORT (Secondary): Machine learning handles only normal/borderline cases
    3. PREDICTION STRENGTH: 70-95% (clamped, never 100%)
    
    RULE PRIORITY (Checked in order):
    =================================
    - Rule 1: Sleep < 4h → HIGH RISK (CRITICAL - checked first)
      * Why: Sleep < 4h is severely unhealthy regardless of other factors
      * Research: Sleep < 4h causes severe cognitive impairment and health risks
    
    - Rule 2: Sleep < 5h AND Study > 9h → HIGH RISK
      * Why: Excessive study without adequate rest = burnout pattern
      * Research: Optimal study is 4-8h; sleep < 5h is insufficient for recovery
    
    - Rule 3: Screen > 8h AND Sleep < 4h → HIGH RISK
      * Why: Excessive screen time with severe sleep deprivation = extreme fatigue
      * Research: Screens disrupt sleep quality; combined with <4h sleep is dangerous
    
    - Rule 4: Sleep ≥ 7h AND Study 4-7h → LOW RISK
      * Why: Balanced sleep and moderate study = healthy pattern
      * Research: 7-9h sleep is optimal; 4-7h study is effective range
    
    - Default: All other cases → Use ML for prediction (normal/borderline cases)
      * Why: Patterns that don't clearly indicate high or low risk need ML analysis
    
    ML SUPPORT:
    ===========
    - ML model handles only cases that don't match extreme rules
    - If ML predicts HIGH → Use ML prediction with 80-90% strength
    - If ML predicts MEDIUM → Use ML prediction with 75-85% strength
    - If ML predicts LOW → Use ML prediction with 70-80% strength
    - Prediction strength is clamped between 70% and 95% (never 100%)
    
    Args:
        study_hours (float): Hours spent studying
        sleep_hours (float): Hours of sleep
        break_time (float): Hours of break/rest
        screen_time (float): Total screen time
        mood_level (str): 'Low', 'Medium', or 'High'
    
    Returns:
        dict: Contains predicted_risk, prediction_strength, explanation, and model_status
    """
    # Convert mood level to numeric score for ML
    mood_score = mood_level_to_score(mood_level)
    
    # ========================================================================
    # STEP 1: SIMPLE RULE-BASED LOGIC (Checked BEFORE ML)
    # ========================================================================
    # CRITICAL: These 3 simple rules are checked FIRST, before ML.
    # If any rule matches, we use that prediction. ML will NOT override HIGH risk predictions.
    
    predicted_risk = None
    rule_applied = None
    explanation = ""
    use_ml = False  # Flag to determine if we should use ML
    is_high_risk_rule = False  # Flag to prevent ML from overriding HIGH risk
    
    # Rule 1: Sleep < 4 hours AND Screen > 8 hours → HIGH RISK
    if sleep_hours < 4 and screen_time > 8:
        predicted_risk = 'High'
        is_high_risk_rule = True
        rule_applied = 'Rule 1: Sleep < 4h AND Screen > 8h'
        explanation = (
            f"High risk detected: You're getting only {sleep_hours:.1f} hours of sleep and spending "
            f"{screen_time:.1f} hours on screens. This combination of severe sleep deprivation and "
            f"excessive screen exposure significantly increases burnout risk."
        )
    
    # Rule 2: Sleep < 4 hours → HIGH RISK
    elif sleep_hours < 4:
        predicted_risk = 'High'
        is_high_risk_rule = True
        rule_applied = 'Rule 2: Sleep < 4h'
        explanation = (
            f"High risk detected: You're getting only {sleep_hours:.1f} hours of sleep, which is "
            f"severely insufficient. Sleep deprivation below 4 hours causes severe cognitive impairment "
            f"and significantly increases burnout risk."
        )
    
    # Rule 3: Study > 9 hours AND Sleep < 5 hours → HIGH RISK
    elif study_hours > 9 and sleep_hours < 5:
        predicted_risk = 'High'
        is_high_risk_rule = True
        rule_applied = 'Rule 3: Study > 9h AND Sleep < 5h'
        explanation = (
            f"High risk detected: You're studying {study_hours:.1f} hours daily with only "
            f"{sleep_hours:.1f} hours of sleep. This pattern shows excessive study without "
            f"adequate rest, which is a classic burnout indicator."
        )
    
    # Rule 4: Sleep ≥ 7h AND Study 4-7h → LOW RISK (Healthy pattern)
    elif sleep_hours >= 7 and 4 <= study_hours <= 7:
        predicted_risk = 'Low'
        rule_applied = 'Rule 4: Healthy Balance'
        explanation = (
            f"Low risk detected: You're maintaining a healthy balance with {sleep_hours:.1f} hours "
            f"of sleep and {study_hours:.1f} hours of study. This pattern aligns with research "
            f"showing that 7-9 hours of sleep and 4-7 hours of focused study is optimal for "
            f"academic performance without burnout. Keep maintaining this balanced routine!"
        )
    
    # Default: Use ML for normal/borderline cases
    else:
        use_ml = True
        rule_applied = 'ML Analysis (Borderline Case)'
        explanation = (
            f"Your current pattern (Sleep: {sleep_hours:.1f}h, Study: {study_hours:.1f}h, "
            f"Breaks: {break_time:.1f}h, Screen: {screen_time:.1f}h) doesn't match extreme "
            f"patterns. Using machine learning analysis to determine risk level."
        )
    
    # ========================================================================
    # STEP 2: ML SUPPORT (For Borderline Cases or Validation)
    # ========================================================================
    
    model = load_burnout_model()
    ml_prediction = None
    ml_probabilities = None
    prediction_strength = 75.0  # Default strength
    
    if model is not None:
        try:
            # Prepare features for ML
            features = np.array([[study_hours, sleep_hours, break_time, screen_time, mood_score]])
            
            # Get ML prediction
            ml_prediction = model.predict(features)[0]
            
            # Get ML probabilities
            probabilities = model.predict_proba(features)[0]
            class_indices = {class_name: idx for idx, class_name in enumerate(model.classes_)}
            
            ml_probabilities = {
                'Low': round(probabilities[class_indices.get('Low', 0)] * 100, 2),
                'Medium': round(probabilities[class_indices.get('Medium', 1)] * 100, 2),
                'High': round(probabilities[class_indices.get('High', 2)] * 100, 2)
            }
            
            # Calculate ML confidence (but clamp it to avoid 100%)
            ml_confidence = probabilities[class_indices[ml_prediction]] * 100
            ml_confidence = min(95.0, max(70.0, ml_confidence))  # Clamp to 70-95%
            
            if use_ml:
                # Use ML prediction for borderline cases
                predicted_risk = ml_prediction
                prediction_strength = ml_confidence
                explanation = (
                    f"ML Analysis: Your pattern (Sleep: {sleep_hours:.1f}h, Study: {study_hours:.1f}h, "
                    f"Breaks: {break_time:.1f}h, Screen: {screen_time:.1f}h, Mood: {mood_level}) "
                    f"indicates {predicted_risk} burnout risk. "
                    f"Prediction probabilities: Low {ml_probabilities['Low']:.1f}%, "
                    f"Medium {ml_probabilities['Medium']:.1f}%, High {ml_probabilities['High']:.1f}%."
                )
            else:
                # Rule-based prediction: ML provides validation ONLY
                # CRITICAL: If HIGH risk rule matched, NEVER override with ML
                if is_high_risk_rule:
                    # HIGH risk rule takes absolute priority - ML cannot override
                    # Adjust strength based on ML agreement, but keep HIGH risk
                    if ml_prediction == 'High':
                        # ML agrees with HIGH → Higher strength (88-95%)
                        prediction_strength = 88.0 + (ml_confidence / 100) * 7  # 88-95%
                        prediction_strength = min(95.0, max(88.0, prediction_strength))
                    else:
                        # ML disagrees but rule is HIGH → Still HIGH, moderate strength (80-88%)
                        prediction_strength = 80.0 + (ml_confidence / 100) * 8  # 80-88%
                        prediction_strength = min(88.0, max(80.0, prediction_strength))
                    # Keep predicted_risk as 'High' (never change it)
                elif ml_prediction == predicted_risk:
                    # ML agrees with rule → Higher strength (85-95%)
                    prediction_strength = 85.0 + (ml_confidence / 100) * 10  # 85-95%
                    prediction_strength = min(95.0, max(85.0, prediction_strength))
                else:
                    # ML disagrees → Still use rule, but lower strength (75-85%)
                    # Rule-based logic takes priority for extreme cases
                    prediction_strength = 75.0 + (ml_confidence / 100) * 10  # 75-85%
                    prediction_strength = min(85.0, max(75.0, prediction_strength))
            
            model_status = 'available'
            
        except Exception as e:
            print(f"ML prediction error: {str(e)}")
            model_status = 'error'
            if use_ml:
                # If ML fails and we needed it, default to Medium risk
                predicted_risk = 'Medium'
                prediction_strength = 70.0
                explanation = (
                    f"Unable to analyze with ML. Defaulting to Medium risk. "
                    f"Your pattern: Sleep {sleep_hours:.1f}h, Study {study_hours:.1f}h, "
                    f"Breaks {break_time:.1f}h, Screen {screen_time:.1f}h."
                )
    else:
        model_status = 'not_available'
        if use_ml:
            # If ML not available and we needed it, default to Medium risk
            predicted_risk = 'Medium'
            prediction_strength = 70.0
            explanation = (
                f"ML model not available. Defaulting to Medium risk. "
                f"Your pattern: Sleep {sleep_hours:.1f}h, Study {study_hours:.1f}h, "
                f"Breaks {break_time:.1f}h, Screen {screen_time:.1f}h. "
                f"Monitor your patterns and aim for: 7-9h sleep, 4-8h study, 1-3h breaks, 6-8h screen time."
            )
        else:
            # Rule-based prediction without ML validation
            if rule_applied in ['Rule 1: Critical Sleep Deprivation', 'Rule 2: Excessive Study with Insufficient Sleep', 'Rule 3: Excessive Screen Time with Critical Sleep Deprivation']:
                prediction_strength = 85.0  # Strong rule-based prediction for high risk
            elif rule_applied == 'Rule 4: Healthy Balance':
                prediction_strength = 80.0  # Strong rule-based prediction for low risk
            else:
                prediction_strength = 75.0  # Default rule-based prediction
    
    # CRITICAL: Clamp prediction strength to 70-95% (never 100%)
    prediction_strength = min(95.0, max(70.0, prediction_strength))
    
    # FINAL VALIDATION: Ensure HIGH risk from rules is never changed
    if is_high_risk_rule and predicted_risk != 'High':
        # This should never happen, but safety check
        print(f"WARNING: HIGH risk rule matched but predicted_risk is {predicted_risk}. Forcing to High.")
        predicted_risk = 'High'
    
    return {
        'predicted_risk': predicted_risk,
        'prediction_strength': round(prediction_strength, 1),
        'explanation': explanation,
        'rule_applied': rule_applied,
        'ml_prediction': ml_prediction,
        'ml_probabilities': ml_probabilities,
        'model_status': model_status,
        'is_high_risk_rule': is_high_risk_rule,  # Debug info
        'features': {
            'study_hours': study_hours,
            'sleep_hours': sleep_hours,
            'break_time': break_time,
            'screen_time': screen_time,
            'mood_score': mood_score
        }
    }


def save_burnout_prediction(user_id, study_date, study_hours, sleep_hours, 
                           break_time, screen_time, mood_score, predicted_risk, prediction_strength):
    """
    Save burnout risk prediction to database.
    
    Args:
        user_id (int): User ID
        study_date (str): Date of study pattern
        study_hours, sleep_hours, break_time, screen_time (float): Features
        mood_score (int): Numeric mood score
        predicted_risk (str): Predicted risk level ('Low', 'Medium', 'High')
        prediction_strength (float): Prediction strength (65-95%), relative certainty
    
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Check if prediction exists for this date
        cursor.execute("""
            SELECT id FROM burnout_predictions 
            WHERE user_id = %s AND study_date = %s
        """, (user_id, study_date))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing prediction
            cursor.execute("""
                UPDATE burnout_predictions 
                SET study_hours = %s, sleep_hours = %s, break_time = %s,
                    screen_time = %s, mood_score = %s, predicted_risk = %s,
                    confidence = %s
                WHERE user_id = %s AND study_date = %s
            """, (study_hours, sleep_hours, break_time, screen_time, 
                  mood_score, predicted_risk, prediction_strength, user_id, study_date))
        else:
            # Insert new prediction
            cursor.execute("""
                INSERT INTO burnout_predictions 
                (user_id, study_date, study_hours, sleep_hours, break_time, 
                 screen_time, mood_score, predicted_risk, confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, study_date, study_hours, sleep_hours, break_time,
                  screen_time, mood_score, predicted_risk, prediction_strength))
        
        conn.commit()
        cursor.close()
        return True
        
    except Exception as e:
        print(f"Error saving burnout prediction: {str(e)}")
        return False


def get_user_burnout_prediction(user_id):
    """
    Get the latest burnout risk prediction for a user.
    
    Args:
        user_id (int): User ID
    
    Returns:
        dict: Latest prediction data, or None if not found
    """
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT predicted_risk, confidence as prediction_strength, study_date, mood_score
            FROM burnout_predictions
            WHERE user_id = %s
            ORDER BY study_date DESC
            LIMIT 1
        """, (user_id,))
        
        prediction = cursor.fetchone()
        cursor.close()
        
        return prediction
        
    except Exception as e:
        print(f"Error getting burnout prediction: {str(e)}")
        return None


def get_user_productivity_score(user_id):
    """
    Get the latest study pattern for a user and calculate productivity score.
    
    Args:
        user_id (int): User ID to get score for
    
    Returns:
        dict: Productivity score data, or None if no study pattern exists
    """
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Get the most recent study pattern
        cursor.execute("""
            SELECT study_hours, sleep_hours, break_time, screen_time, study_date
            FROM study_patterns
            WHERE user_id = %s
            ORDER BY study_date DESC
            LIMIT 1
        """, (user_id,))
        
        pattern = cursor.fetchone()
        cursor.close()
        
        if pattern:
            # Calculate productivity score
            score_data = calculate_productivity_score(
                float(pattern['study_hours']),
                float(pattern['sleep_hours']),
                float(pattern['break_time']),
                float(pattern['screen_time'])
            )
            score_data['study_date'] = pattern['study_date']
            return score_data
        
        return None
        
    except Exception as e:
        print(f"Error getting productivity score: {str(e)}")
        return None


@app.route('/dashboard')
def dashboard():
    """
    Dashboard route - displays user dashboard after login.
    
    PROTECTED ROUTE:
    - Requires authentication (user must be logged in)
    - Redirects to login if not authenticated
    - Shows personalized content based on logged-in user
    
    Shows user progress, available courses, and productivity score.
    """
    # Check authentication - redirect to login if not logged in
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        # Get productivity score for the user
        productivity_score = get_user_productivity_score(session['user_id'])
        
        # Get burnout risk prediction for the user
        burnout_prediction = get_user_burnout_prediction(session['user_id'])
        
        # Get personalized study suggestions
        study_suggestions = get_user_study_suggestions(session['user_id'])
        
        return render_template('dashboard.html', 
                             username=session.get('username'),
                             name=session.get('name', session.get('username')),
                             productivity_score=productivity_score,
                             burnout_prediction=burnout_prediction,
                             study_suggestions=study_suggestions)
        
    except Exception as e:
        return render_template('dashboard.html', 
                             username=session.get('username'),
                             name=session.get('name', session.get('username')),
                             productivity_score=None,
                             burnout_prediction=None,
                             study_suggestions=[],
                             error=str(e))


@app.route('/api/courses', methods=['GET'])
def get_courses():
    """
    API endpoint to get all available courses.
    Returns JSON data of all courses.
    """
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        cursor.close()
        
        return jsonify({'success': True, 'courses': courses})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/courses', methods=['POST'])
def create_course():
    """
    API endpoint to create a new course.
    Requires authentication (session).
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    instructor = data.get('instructor')
    duration = data.get('duration')
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO courses (title, description, instructor, duration) VALUES (%s, %s, %s, %s)",
            (title, description, instructor, duration)
        )
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Course created successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/study-pattern')
def study_pattern():
    """
    Study Pattern Analyzer page - displays form to track daily study data.
    
    PROTECTED ROUTE:
    - Requires authentication
    - Shows form to input daily study metrics
    - Displays user's study history
    
    FIELDS:
    - Study hours: Hours spent studying
    - Sleep hours: Hours of sleep
    - Break time: Hours of break/rest
    - Screen time: Hours spent on screen
    - Mood level: Low / Medium / High
    """
    # Check authentication
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        # Get user's recent study patterns (last 7 days)
        conn = mysql.connect
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, study_date, study_hours, sleep_hours, break_time, 
                   screen_time, mood_level, created_at
            FROM study_patterns
            WHERE user_id = %s
            ORDER BY study_date DESC
            LIMIT 7
        """, (session['user_id'],))
        
        recent_patterns = cursor.fetchall()
        cursor.close()
        
        # Get today's date for default form value
        today = date.today().isoformat()
        
        return render_template('study_pattern.html', 
                             name=session.get('name', session.get('username')),
                             recent_patterns=recent_patterns,
                             today=today)
        
    except Exception as e:
        today = date.today().isoformat()
        return render_template('study_pattern.html', 
                             name=session.get('name', session.get('username')),
                             recent_patterns=[],
                             today=today,
                             error=str(e))


@app.route('/api/study-pattern', methods=['POST'])
def submit_study_pattern():
    """
    API endpoint to submit daily study pattern data.
    
    REQUIRES AUTHENTICATION:
    - User must be logged in
    - Data is linked to logged-in user
    
    DATA VALIDATION:
    - All fields are required
    - Study hours, sleep hours, break time, screen time: Decimal numbers
    - Mood level: Must be 'Low', 'Medium', or 'High'
    - One entry per user per day (updates if exists)
    
    Returns:
        JSON response with success/error message
    """
    # Check authentication
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    # Get form data
    study_date = request.form.get('study_date')
    study_hours = request.form.get('study_hours')
    sleep_hours = request.form.get('sleep_hours')
    break_time = request.form.get('break_time')
    screen_time = request.form.get('screen_time')
    mood_level = request.form.get('mood_level')
    
    # Validate required fields
    if not all([study_date, study_hours, sleep_hours, break_time, screen_time, mood_level]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    # Validate mood level
    if mood_level not in ['Low', 'Medium', 'High']:
        return jsonify({'success': False, 'message': 'Invalid mood level'})
    
    # Validate numeric fields
    try:
        study_hours = float(study_hours)
        sleep_hours = float(sleep_hours)
        break_time = float(break_time)
        screen_time = float(screen_time)
        
        # Basic range validation
        if any(x < 0 or x > 24 for x in [study_hours, sleep_hours, break_time, screen_time]):
            return jsonify({'success': False, 'message': 'Hours must be between 0 and 24'})
            
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid number format'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Check if entry exists for this date (one entry per day per user)
        cursor.execute("""
            SELECT id FROM study_patterns 
            WHERE user_id = %s AND study_date = %s
        """, (session['user_id'], study_date))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing entry
            cursor.execute("""
                UPDATE study_patterns 
                SET study_hours = %s, sleep_hours = %s, break_time = %s,
                    screen_time = %s, mood_level = %s
                WHERE user_id = %s AND study_date = %s
            """, (study_hours, sleep_hours, break_time, screen_time, mood_level,
                  session['user_id'], study_date))
        else:
            # Insert new entry
            cursor.execute("""
                INSERT INTO study_patterns 
                (user_id, study_date, study_hours, sleep_hours, break_time, screen_time, mood_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], study_date, study_hours, sleep_hours, 
                  break_time, screen_time, mood_level))
        
        conn.commit()
        cursor.close()
        
        # Predict burnout risk using ML model
        prediction_result = predict_burnout_risk(
            study_hours, sleep_hours, break_time, screen_time, mood_level
        )
        
        # Save prediction to database (works with or without ML)
        if prediction_result['predicted_risk']:
            mood_score = mood_level_to_score(mood_level)
            save_burnout_prediction(
                session['user_id'], study_date, study_hours, sleep_hours,
                break_time, screen_time, mood_score,
                prediction_result['predicted_risk'],
                prediction_result['prediction_strength']  # Changed from 'confidence'
            )
        
        return jsonify({
            'success': True, 
            'message': 'Study pattern saved successfully!',
            'burnout_prediction': prediction_result if prediction_result['model_status'] == 'available' else None
        })
        
    except Exception as e:
        print(f"Error saving study pattern: {str(e)}")
        return jsonify({'success': False, 'message': 'Error saving data. Please try again.'})


@app.route('/api/study-pattern', methods=['GET'])
def get_study_patterns():
    """
    API endpoint to retrieve user's study patterns.
    
    REQUIRES AUTHENTICATION:
    - User must be logged in
    - Returns only logged-in user's data
    
    QUERY PARAMETERS:
    - limit: Number of records to return (default: 30)
    - days: Number of days to retrieve (optional)
    
    Returns:
        JSON response with study patterns array
    """
    # Check authentication
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Get limit from query parameter (default 30)
        limit = request.args.get('limit', 30, type=int)
        
        cursor.execute("""
            SELECT study_date, study_hours, sleep_hours, break_time, 
                   screen_time, mood_level, created_at
            FROM study_patterns
            WHERE user_id = %s
            ORDER BY study_date DESC
            LIMIT %s
        """, (session['user_id'], limit))
        
        patterns = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True, 
            'patterns': patterns
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/study-pattern/<int:pattern_id>', methods=['GET'])
def get_study_pattern(pattern_id):
    """
    API endpoint to get a specific study pattern by ID for editing.
    
    REQUIRES AUTHENTICATION:
    - User must be logged in
    - Can only access their own patterns
    
    Returns:
        JSON response with pattern data
    """
    # Check authentication
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Get pattern (only if it belongs to the user)
        cursor.execute("""
            SELECT id, study_date, study_hours, sleep_hours, break_time, 
                   screen_time, mood_level
            FROM study_patterns
            WHERE id = %s AND user_id = %s
        """, (pattern_id, session['user_id']))
        
        pattern = cursor.fetchone()
        cursor.close()
        
        if pattern:
            return jsonify({
                'success': True,
                'pattern': {
                    'id': pattern['id'],
                    'study_date': pattern['study_date'].isoformat() if isinstance(pattern['study_date'], date) else str(pattern['study_date']),
                    'study_hours': float(pattern['study_hours']),
                    'sleep_hours': float(pattern['sleep_hours']),
                    'break_time': float(pattern['break_time']),
                    'screen_time': float(pattern['screen_time']),
                    'mood_level': pattern['mood_level']
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Pattern not found or access denied'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/study-pattern/<int:pattern_id>', methods=['PUT'])
def update_study_pattern(pattern_id):
    """
    API endpoint to update a study pattern by ID.
    
    REQUIRES AUTHENTICATION:
    - User must be logged in
    - Can only update their own patterns
    
    Returns:
        JSON response with success/error message
    """
    # Check authentication
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    # Get data from request
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    study_date = data.get('study_date')
    study_hours = data.get('study_hours')
    sleep_hours = data.get('sleep_hours')
    break_time = data.get('break_time')
    screen_time = data.get('screen_time')
    mood_level = data.get('mood_level')
    
    # Validate required fields
    if not all([study_date, study_hours, sleep_hours, break_time, screen_time, mood_level]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    # Validate mood level
    if mood_level not in ['Low', 'Medium', 'High']:
        return jsonify({'success': False, 'message': 'Invalid mood level'})
    
    # Validate numeric fields
    try:
        study_hours = float(study_hours)
        sleep_hours = float(sleep_hours)
        break_time = float(break_time)
        screen_time = float(screen_time)
        
        # Basic range validation
        if any(x < 0 or x > 24 for x in [study_hours, sleep_hours, break_time, screen_time]):
            return jsonify({'success': False, 'message': 'Hours must be between 0 and 24'})
            
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid number format'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Check if pattern exists and belongs to user
        cursor.execute("""
            SELECT id FROM study_patterns 
            WHERE id = %s AND user_id = %s
        """, (pattern_id, session['user_id']))
        
        existing = cursor.fetchone()
        
        if not existing:
            cursor.close()
            return jsonify({'success': False, 'message': 'Pattern not found or access denied'})
        
        # Update the pattern
        cursor.execute("""
            UPDATE study_patterns 
            SET study_date = %s, study_hours = %s, sleep_hours = %s, break_time = %s,
                screen_time = %s, mood_level = %s
            WHERE id = %s AND user_id = %s
        """, (study_date, study_hours, sleep_hours, break_time, screen_time, mood_level,
              pattern_id, session['user_id']))
        
        conn.commit()
        cursor.close()
        
        # Recalculate burnout prediction for updated pattern
        prediction_result = predict_burnout_risk(
            study_hours, sleep_hours, break_time, screen_time, mood_level
        )
        
        # Update prediction in database
        if prediction_result['predicted_risk']:
            mood_score = mood_level_to_score(mood_level)
            save_burnout_prediction(
                session['user_id'], study_date, study_hours, sleep_hours,
                break_time, screen_time, mood_score,
                prediction_result['predicted_risk'],
                prediction_result['prediction_strength']
            )
        
        return jsonify({
            'success': True, 
            'message': 'Study pattern updated successfully! Productivity score and burnout prediction updated.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/study-pattern/<int:pattern_id>', methods=['DELETE'])
def delete_study_pattern(pattern_id):
    """
    API endpoint to delete a study pattern by ID.
    
    REQUIRES AUTHENTICATION:
    - User must be logged in
    - Can only delete their own patterns
    
    Returns:
        JSON response with success/error message
    """
    # Check authentication
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Check if pattern exists and belongs to user
        cursor.execute("""
            SELECT id, study_date FROM study_patterns 
            WHERE id = %s AND user_id = %s
        """, (pattern_id, session['user_id']))
        
        pattern = cursor.fetchone()
        
        if not pattern:
            cursor.close()
            return jsonify({'success': False, 'message': 'Pattern not found or access denied'})
        
        # Delete the pattern
        cursor.execute("""
            DELETE FROM study_patterns 
            WHERE id = %s AND user_id = %s
        """, (pattern_id, session['user_id']))
        
        conn.commit()
        cursor.close()
        
        return jsonify({
            'success': True, 
            'message': 'Study pattern deleted successfully!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/dashboard/weekly-study-hours', methods=['GET'])
def get_weekly_study_hours():
    """
    API endpoint to get weekly study hours data for chart.
    
    Returns study hours for the last 7 days.
    Used for weekly study hours chart visualization.
    
    Returns:
        JSON with dates and study hours for last 7 days
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Get last 7 days of study data
        cursor.execute("""
            SELECT study_date, study_hours
            FROM study_patterns
            WHERE user_id = %s
            ORDER BY study_date DESC
            LIMIT 7
        """, (session['user_id'],))
        
        patterns = cursor.fetchall()
        cursor.close()
        
        # Prepare data for chart (reverse to show oldest first)
        dates = []
        hours = []
        
        for pattern in reversed(patterns):
            dates.append(pattern['study_date'].strftime('%Y-%m-%d'))
            hours.append(float(pattern['study_hours']))
        
        return jsonify({
            'success': True,
            'dates': dates,
            'study_hours': hours
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/dashboard/sleep-vs-productivity', methods=['GET'])
def get_sleep_vs_productivity():
    """
    API endpoint to get sleep hours vs productivity score data for chart.
    
    Returns sleep hours and corresponding productivity scores for analysis.
    Used for sleep vs productivity correlation chart.
    
    Returns:
        JSON with sleep hours and productivity scores
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Get study patterns with dates
        cursor.execute("""
            SELECT study_date, sleep_hours, study_hours, break_time, screen_time, mood_level
            FROM study_patterns
            WHERE user_id = %s
            ORDER BY study_date DESC
            LIMIT 14
        """, (session['user_id'],))
        
        patterns = cursor.fetchall()
        cursor.close()
        
        # Calculate productivity score for each pattern
        sleep_hours_list = []
        productivity_scores = []
        dates = []
        
        for pattern in reversed(patterns):
            # Convert mood level to score
            mood_score = mood_level_to_score(pattern['mood_level'])
            
            # Calculate productivity score
            score_data = calculate_productivity_score(
                float(pattern['study_hours']),
                float(pattern['sleep_hours']),
                float(pattern['break_time']),
                float(pattern['screen_time'])
            )
            
            sleep_hours_list.append(float(pattern['sleep_hours']))
            productivity_scores.append(score_data['total_score'])
            dates.append(pattern['study_date'].strftime('%Y-%m-%d'))
        
        return jsonify({
            'success': True,
            'dates': dates,
            'sleep_hours': sleep_hours_list,
            'productivity_scores': productivity_scores
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/logout')
def logout():
    """
    Logout route - clears user session and redirects to home.
    
    SESSION CLEARING:
    - Removes all session data (user_id, username, etc.)
    - Effectively logs out the user
    - User must login again to access protected routes
    """
    # Clear all session data
    session.clear()
    return redirect(url_for('index'))


@app.route('/api/predict-burnout', methods=['POST'])
def predict_burnout_api():
    """
    API endpoint to predict burnout risk from study pattern data.
    
    REQUIRES AUTHENTICATION:
    - User must be logged in
    
    REQUEST BODY (JSON or Form):
    - study_hours: Hours spent studying
    - sleep_hours: Hours of sleep
    - break_time: Hours of break
    - screen_time: Total screen time
    - mood_level: 'Low', 'Medium', or 'High'
    
    Returns:
        JSON response with prediction and confidence
    """
    # Check authentication
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    # Get data from request
    if request.is_json:
        data = request.get_json()
        study_hours = data.get('study_hours')
        sleep_hours = data.get('sleep_hours')
        break_time = data.get('break_time')
        screen_time = data.get('screen_time')
        mood_level = data.get('mood_level')
    else:
        study_hours = request.form.get('study_hours')
        sleep_hours = request.form.get('sleep_hours')
        break_time = request.form.get('break_time')
        screen_time = request.form.get('screen_time')
        mood_level = request.form.get('mood_level')
    
    # Validate inputs
    if not all([study_hours, sleep_hours, break_time, screen_time, mood_level]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    if mood_level not in ['Low', 'Medium', 'High']:
        return jsonify({'success': False, 'message': 'Invalid mood level'})
    
    try:
        study_hours = float(study_hours)
        sleep_hours = float(sleep_hours)
        break_time = float(break_time)
        screen_time = float(screen_time)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid number format'})
    
    # Make prediction
    prediction_result = predict_burnout_risk(
        study_hours, sleep_hours, break_time, screen_time, mood_level
    )
    
    if prediction_result['predicted_risk']:
        return jsonify({
            'success': True,
            'predicted_risk': prediction_result['predicted_risk'],
            'prediction_strength': prediction_result['prediction_strength'],
            'explanation': prediction_result['explanation'],
            'rule_applied': prediction_result['rule_applied'],
            'ml_prediction': prediction_result.get('ml_prediction'),
            'ml_probabilities': prediction_result.get('ml_probabilities'),
            'model_status': prediction_result['model_status']
        })
    else:
        return jsonify({
            'success': False,
            'message': prediction_result.get('message', 'Model not available')
        })


# ============================================================================
# AI CHATBOT MODULE (OpenAI ChatGPT / Google Gemini Integration)
# ============================================================================

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path):
    """
    Extract text from PDF file using PyPDF2.
    
    Args:
        file_path (str): Path to PDF file
    
    Returns:
        str: Extracted text content
    """
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF: {str(e)}")
        return ""


def extract_text_from_text_file(file_path):
    """
    Extract text from plain text file.
    
    Args:
        file_path (str): Path to text file
    
    Returns:
        str: File content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading text file: {str(e)}")
        return ""


# Text extraction functions for document processing
def preprocess_text(text):
    """Simple text preprocessing - kept for document processing."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# Removed all old question generator NLP functions:
# - extract_concepts_from_text
# - identify_key_topics  
# - extract_important_sentences
# - generate_questions
# These are no longer needed as we're using AI for direct Q&A


@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    """
    API endpoint to upload and process documents for AI chatbot.
    
    PROCESS:
    1. Receive uploaded file (PDF or text)
    2. Extract text content
    3. Store document in database for chatbot context
    4. Return document ID for use in chat
    
    Returns:
        JSON with document_id and success message
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type. Only PDF and TXT files are allowed.'})
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Determine file type
        file_ext = filename.rsplit('.', 1)[1].lower()
        file_type = 'PDF' if file_ext == 'pdf' else 'TEXT'
        
        # Extract text
        if file_type == 'PDF':
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_text_file(file_path)
        
        if not text or len(text.strip()) < 50:
            os.remove(file_path)  # Clean up
            return jsonify({'success': False, 'message': 'File is too short or could not extract text. Minimum 50 characters required.'})
        
        # Store document in database
        conn = mysql.connect
        cursor = conn.cursor()
        
        # CRITICAL: Set connection charset to utf8mb4 BEFORE any operations
        # This ensures the connection can handle 4-byte UTF-8 characters (emojis, etc.)
        try:
            cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("SET CHARACTER SET utf8mb4")
            cursor.execute("SET character_set_connection=utf8mb4")
            cursor.execute("SET character_set_client=utf8mb4")
            cursor.execute("SET character_set_results=utf8mb4")
        except Exception as e:
            print(f"Warning: Could not set charset: {e}")
        
        # Ensure text is properly encoded for utf8mb4
        # Handle any encoding issues with special characters
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        
        # Clean text: remove or replace problematic characters
        # Normalize Unicode characters to composed form
        text = unicodedata.normalize('NFKC', text)
        
        # Remove or replace any remaining problematic characters
        # Keep only printable characters and common whitespace (newlines, tabs, etc.)
        # Filter out control characters except newlines, carriage returns, and tabs
        cleaned_text = []
        for char in text:
            cat = unicodedata.category(char)
            # Keep printable characters, newlines, tabs, carriage returns
            if cat[0] != 'C' or char in '\n\r\t':
                cleaned_text.append(char)
            # Replace other control characters with space
            elif cat == 'Cc':
                cleaned_text.append(' ')
        text = ''.join(cleaned_text)
        
        # Ensure text is valid UTF-8
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Use binary parameter binding to ensure proper encoding
        cursor.execute("""
            INSERT INTO user_documents 
            (user_id, filename, file_type, extracted_text)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], filename, file_type, text))
        document_id = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': f'Document "{filename}" uploaded successfully! You can now ask questions about it.',
            'document_id': document_id,
            'filename': filename
        })
        
    except Exception as e:
        print(f"Error uploading document: {str(e)}")
        # Clean up file if exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'})


# Removed: get_user_questions route - no longer needed


# ============================================================================
# HISTORY MANAGEMENT MODULE
# ============================================================================

@app.route('/history')
def history():
    """
    History Management page - displays user's historical data.
    
    PROTECTED ROUTE:
    - Requires authentication
    - Shows study patterns, burnout predictions, and generated questions
    - Organized in tabs for easy navigation
    """
    if not is_authenticated():
        return redirect(url_for('login'))
    
    return render_template('history.html', 
                         name=session.get('name', session.get('username')))


@app.route('/api/history/study-patterns', methods=['GET'])
def get_study_patterns_history():
    """
    API endpoint to retrieve user's study pattern history.
    
    Returns all study pattern entries for the logged-in user.
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        limit = request.args.get('limit', 100, type=int)
        
        cursor.execute("""
            SELECT study_date, study_hours, sleep_hours, break_time, 
                   screen_time, mood_level, created_at
            FROM study_patterns
            WHERE user_id = %s
            ORDER BY study_date DESC
            LIMIT %s
        """, (session['user_id'], limit))
        
        patterns = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'patterns': patterns,
            'count': len(patterns)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/history/burnout-predictions', methods=['GET'])
def get_burnout_predictions_history():
    """
    API endpoint to retrieve user's burnout prediction history.
    
    Returns all burnout predictions for the logged-in user.
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        limit = request.args.get('limit', 100, type=int)
        
        cursor.execute("""
            SELECT study_date, study_hours, sleep_hours, break_time, 
                   screen_time, mood_score, predicted_risk, confidence, created_at
            FROM burnout_predictions
            WHERE user_id = %s
            ORDER BY study_date DESC
            LIMIT %s
        """, (session['user_id'], limit))
        
        predictions = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'count': len(predictions)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# Removed: get_generated_questions_history route - no longer needed (old question generator removed)
    """
    API endpoint to retrieve user's generated questions history.
    
    Returns all generated questions for the logged-in user.
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        limit = request.args.get('limit', 100, type=int)
        
        cursor.execute("""
            SELECT id, source_filename, source_type, question_text, 
                   question_type, topic_keywords, created_at
            FROM generated_questions
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (session['user_id'], limit))
        
        questions = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# AI CHATBOT MODULE - Google Gemini
# ============================================================================

def get_ai_response(question, document_text=None):
    """
    Get AI response using Google Gemini API.
    
    Args:
        question (str): User's question
        document_text (str, optional): Document content for context
    
    Returns:
        str: AI-generated response
    """
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        raise ValueError("Gemini API key not configured. Please set GEMINI_API_KEY in .env file. Get your free key at: https://makersuite.google.com/app/apikey")
    
    try:
        # Use the stable google.generativeai package (deprecated but more reliable)
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        
        # Prepare context from document (use up to 8000 characters for better context)
        context = ""
        if document_text:
            context = document_text[:8000] + "..." if len(document_text) > 8000 else document_text
        
        # Create prompt
        if context:
            prompt = f"""You are an AI assistant helping students understand their course materials.
Answer questions based on the provided document context. Your responses must be clearly structured and well-formatted.

IMPORTANT FORMATTING REQUIREMENTS:
- Use clear headings and subheadings (use **bold** for emphasis)
- Use bullet points (•) or numbered lists for multiple items
- Use line breaks to separate sections
- Structure answers with:
  * Introduction/Definition (if applicable)
  * Main points (use bullets or numbers)
  * Examples (clearly labeled)
  * Conclusion/Summary (if needed)
- Use proper spacing between sections
- Make the answer easy to read and scan

If the answer isn't in the context, say so politely and provide general guidance if possible.

Document Context:
{context}

Question: {question}

Provide a clear, well-structured, and helpful answer based on the document context:"""
        else:
            prompt = f"""You are an AI assistant helping students understand their course materials.
Your responses must be clearly structured and well-formatted.

IMPORTANT FORMATTING REQUIREMENTS:
- Use clear headings and subheadings (use **bold** for emphasis)
- Use bullet points (•) or numbered lists for multiple items
- Use line breaks to separate sections
- Structure answers with:
  * Introduction/Definition (if applicable)
  * Main points (use bullets or numbers)
  * Examples (clearly labeled)
  * Conclusion/Summary (if needed)
- Use proper spacing between sections
- Make the answer easy to read and scan

Question: {question}

Provide a clear, well-structured, and helpful answer:"""
        
        # List available models first to see what's accessible
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            print(f"Available models: {available_models}")
            
            # Try to find a working model
            if available_models:
                # Use the first available model
                model_name = available_models[0].split('/')[-1]  # Extract just the model name
                print(f"Using model: {model_name}")
            else:
                # Fallback to common model names
                model_name = 'gemini-1.5-flash'
        except Exception as list_error:
            print(f"Could not list models: {list_error}")
            # Fallback to trying common model names
            model_names = ['gemini-1.5-flash', 'gemini-1.0-pro', 'gemini-pro']
            last_error = None
            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    return response.text.strip()
                except Exception as e:
                    last_error = e
                    error_msg = str(e)
                    if "404" in error_msg or "not found" in error_msg.lower():
                        print(f"Model {model_name} not available, trying next...")
                        continue
                    raise
            if last_error:
                raise Exception(f"Could not access any Gemini models. Error: {str(last_error)}. Please verify your API key at https://makersuite.google.com/app/apikey")
            return
        
        # Use the selected model
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except ImportError:
        raise ImportError("Google Generative AI library not installed. Run: pip install google-generativeai")
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API error details: {str(e)}")
        if "API key" in error_msg or "authentication" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
            raise Exception(f"API key error. Please check your GEMINI_API_KEY in .env file. Get your free key at: https://makersuite.google.com/app/apikey")
        raise Exception(f"Gemini API error: {error_msg}")


# Removed: generate_fallback_response - now using proper AI APIs


@app.route('/chatbot')
def chatbot():
    """
    AI Chatbot page - unified interface for document upload and chat.
    
    PROTECTED ROUTE:
    - Requires authentication
    - Displays document upload section
    - Displays chat interface
    - Shows list of uploaded documents
    - Uses Google Gemini API
    """
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Get user's uploaded documents
        cursor.execute("""
            SELECT id, filename, file_type, created_at
            FROM user_documents
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 20
        """, (session['user_id'],))
        
        documents = cursor.fetchall()
        cursor.close()
        
        return render_template('chatbot.html',
                             name=session.get('name', session.get('username')),
                             documents=documents)
    except Exception as e:
        return render_template('chatbot.html',
                             name=session.get('name', session.get('username')),
                             documents=[],
                             error=str(e))


# ============================================================================
# ACADEMIC PERFORMANCE TRACKER MODULE
# ============================================================================

@app.route('/academic-performance')
def academic_performance():
    """
    Academic Performance Tracker page - displays matrix/grid table of academic performance.
    
    PROTECTED ROUTE:
    - Requires authentication
    - Displays academic performance data grouped by Class/Semester
    - Matrix table format: Rows = Exams, Columns = Subjects
    """
    if not is_authenticated():
        return redirect(url_for('login'))
    
    return render_template('academic_performance.html',
                         name=session.get('name', session.get('username')))


@app.route('/api/academic-performance', methods=['GET'])
def get_academic_performance():
    """
    API endpoint to retrieve user's academic performance data.
    
    Returns data grouped by class/semester in matrix format.
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Get all academic performance records for the user
        cursor.execute("""
            SELECT id, class_semester, exam_name, subject_name, marks_scored, total_marks
            FROM academic_performance
            WHERE user_id = %s
            ORDER BY class_semester, exam_name, subject_name
        """, (session['user_id'],))
        
        records = cursor.fetchall()
        cursor.close()
        
        # Group data by class_semester
        grouped_data = {}
        for record in records:
            class_sem = record['class_semester']
            if class_sem not in grouped_data:
                grouped_data[class_sem] = {}
            
            exam_name = record['exam_name']
            if exam_name not in grouped_data[class_sem]:
                grouped_data[class_sem][exam_name] = {}
            
            grouped_data[class_sem][exam_name][record['subject_name']] = {
                'id': record['id'],
                'marks_scored': float(record['marks_scored']),
                'total_marks': float(record['total_marks'])
            }
        
        return jsonify({
            'success': True,
            'data': grouped_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/academic-performance', methods=['POST'])
def add_academic_performance():
    """
    API endpoint to add academic performance data.
    
    Required fields:
    - class_semester: Class or Semester name
    - exam_name: Name of the exam
    - subject_name: Name of the subject
    - marks_scored: Marks obtained
    - total_marks: Total marks for the exam
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    # Get data from request
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    class_semester = data.get('class_semester', '').strip()
    exam_name = data.get('exam_name', '').strip()
    subject_name = data.get('subject_name', '').strip()
    marks_scored = data.get('marks_scored')
    total_marks = data.get('total_marks')
    
    # Validate required fields
    if not all([class_semester, exam_name, subject_name, marks_scored, total_marks]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    # Validate numeric fields
    try:
        marks_scored = float(marks_scored)
        total_marks = float(total_marks)
        
        if marks_scored < 0 or total_marks <= 0:
            return jsonify({'success': False, 'message': 'Invalid marks values'})
        if marks_scored > total_marks:
            return jsonify({'success': False, 'message': 'Marks scored cannot exceed total marks'})
            
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid number format'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Insert new record
        cursor.execute("""
            INSERT INTO academic_performance 
            (user_id, class_semester, exam_name, subject_name, marks_scored, total_marks)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session['user_id'], class_semester, exam_name, subject_name, marks_scored, total_marks))
        
        conn.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Academic performance record added successfully!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/academic-performance/<int:record_id>', methods=['DELETE'])
def delete_academic_performance(record_id):
    """
    API endpoint to delete an academic performance record.
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Check if record exists and belongs to user
        cursor.execute("""
            SELECT id FROM academic_performance 
            WHERE id = %s AND user_id = %s
        """, (record_id, session['user_id']))
        
        record = cursor.fetchone()
        
        if not record:
            cursor.close()
            return jsonify({'success': False, 'message': 'Record not found or access denied'})
        
        # Delete the record
        cursor.execute("""
            DELETE FROM academic_performance 
            WHERE id = %s AND user_id = %s
        """, (record_id, session['user_id']))
        
        conn.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Record deleted successfully!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/chat', methods=['POST'])
def chat_api():
    """
    API endpoint for AI chatbot - handles user questions and returns AI responses.
    
    REQUEST BODY (JSON):
    - question: User's question
    - document_id (optional): ID of document to use as context
    
    Returns:
        JSON with AI response
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    data = request.get_json()
    question = data.get('question', '').strip()
    document_id = data.get('document_id')
    
    if not question:
        return jsonify({'success': False, 'message': 'Question is required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Get document text if document_id provided
        document_text = None
        if document_id:
            cursor.execute("""
                SELECT extracted_text FROM user_documents
                WHERE id = %s AND user_id = %s
            """, (document_id, session['user_id']))
            
            doc = cursor.fetchone()
            if doc:
                document_text = doc['extracted_text']
        
        # If no document selected, try to get the most recent document
        if not document_text:
            cursor.execute("""
                SELECT extracted_text FROM user_documents
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (session['user_id'],))
            
            doc = cursor.fetchone()
            if doc:
                document_text = doc['extracted_text']
                # Get the document_id for storage
                cursor.execute("""
                    SELECT id FROM user_documents
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (session['user_id'],))
                doc_id_result = cursor.fetchone()
                document_id = doc_id_result['id'] if doc_id_result else None
        
        # Get AI response using Gemini
        ai_response = get_ai_response(question, document_text)
        
        # Store conversation in database
        cursor.execute("""
            INSERT INTO chat_conversations
            (user_id, document_id, user_message, ai_response)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], document_id, question, ai_response))
        
        conn.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'document_id': document_id
        })
        
    except ValueError as e:
        # API key not configured
        return jsonify({
            'success': False, 
            'message': f'{str(e)}. Get your free API key at: https://makersuite.google.com/app/apikey'
        })
    except ImportError as e:
        # Library not installed
        return jsonify({
            'success': False, 
            'message': f'{str(e)}. Please run: pip install google-generativeai'
        })
    except Exception as e:
        error_msg = str(e)
        print(f"Chat API error: {error_msg}")
        if "API key" in error_msg or "authentication" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
            return jsonify({
                'success': False, 
                'message': f'API key error. Please check your GEMINI_API_KEY in .env file. Get your free key at: https://makersuite.google.com/app/apikey'
            })
        return jsonify({'success': False, 'message': f'Error processing question: {error_msg}'})


@app.route('/api/delete-document/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """
    API endpoint to delete a user's uploaded document.
    
    PROTECTED ROUTE:
    - Requires authentication
    - Only allows deletion of user's own documents
    - Deletes document and associated chat history
    
    Returns:
        JSON with success status
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        # Verify document belongs to user
        cursor.execute("""
            SELECT id, filename FROM user_documents
            WHERE id = %s AND user_id = %s
        """, (document_id, session['user_id']))
        
        doc = cursor.fetchone()
        if not doc:
            cursor.close()
            return jsonify({'success': False, 'message': 'Document not found or access denied'})
        
        # Delete associated chat conversations first (foreign key constraint)
        cursor.execute("""
            DELETE FROM chat_conversations
            WHERE document_id = %s AND user_id = %s
        """, (document_id, session['user_id']))
        
        # Delete the document
        cursor.execute("""
            DELETE FROM user_documents
            WHERE id = %s AND user_id = %s
        """, (document_id, session['user_id']))
        
        conn.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': f'Document "{doc["filename"]}" deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return jsonify({'success': False, 'message': f'Error deleting document: {str(e)}'})


@app.route('/api/user-documents', methods=['GET'])
def get_user_documents():
    """
    API endpoint to get user's uploaded documents.
    
    Returns:
        JSON with list of user's documents
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, filename, file_type, created_at
            FROM user_documents
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 20
        """, (session['user_id'],))
        
        documents = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/chat-history', methods=['GET'])
def get_chat_history():
    """
    API endpoint to get user's chat history.
    
    Query Parameters:
    - document_id (optional): Filter by document
    - limit: Number of messages (default: 50)
    
    Returns:
        JSON with chat history
    """
    if not is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        
        document_id = request.args.get('document_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        
        if document_id:
            cursor.execute("""
                SELECT user_message, ai_response, created_at
                FROM chat_conversations
                WHERE user_id = %s AND document_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (session['user_id'], document_id, limit))
        else:
            cursor.execute("""
                SELECT user_message, ai_response, created_at
                FROM chat_conversations
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (session['user_id'], limit))
        
        history = cursor.fetchall()
        cursor.close()
        
        # Reverse to show oldest first
        history.reverse()
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/health')
def health():
    """
    Health check endpoint - verifies database connection.
    """
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


# Run the application
if __name__ == '__main__':
    # Initialize database on first run
    init_database()
    
    # Run Flask app in debug mode (change to False in production)
    app.run(debug=True, host='0.0.0.0', port=5000)

