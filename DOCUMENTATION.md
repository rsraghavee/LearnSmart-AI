# LearnSmart AI - Complete Technical Documentation

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Problem Statement](#problem-statement)
3. [Project Abstract](#project-abstract)
4. [Module Documentation](#module-documentation)
5. [Database Schema](#database-schema)
6. [API Reference](#api-reference)
7. [Implementation Details](#implementation-details)
8. [Viva Presentation Guide](#viva-presentation-guide)
9. [Installation & Setup](#installation--setup)
10. [Future Enhancements](#future-enhancements)

---

## System Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│              (Frontend - HTML/CSS/JavaScript)            │
│  - User Interface                                        │
│  - Client-side Validation                                │
│  - Chart.js Visualizations                               │
│  - AJAX API Calls                                        │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/JSON
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                      │
│              (Backend - Flask/Python)                    │
│  - Route Handlers                                        │
│  - Business Logic                                        │
│  - Authentication & Authorization                        │
│  - ML Model Integration                                  │
│  - AI Integration (Gemini)                               │
│  - API Endpoints                                         │
└─────────────────────────────────────────────────────────┘
                          ↕ SQL Queries
┌─────────────────────────────────────────────────────────┐
│                      DATA LAYER                          │
│                  (MySQL Database)                        │
│  - User Data                                             │
│  - Study Patterns                                        │
│  - Burnout Predictions                                   │
│  - Academic Performance                                  │
│  - Documents & Chat History                              │
└─────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Frontend (Presentation Layer)
- **Technologies**: HTML5, CSS3, JavaScript (ES6+), Chart.js
- **Responsibilities**: UI rendering, client validation, data visualization, API communication
- **Files**: `templates/*.html`, `static/css/style.css`, `static/js/*.js`

#### Backend (Application Layer)
- **Technologies**: Flask 3.0.0, Python 3.7+
- **Responsibilities**: Business logic, data processing, ML/NLP integration, API endpoints
- **Main File**: `app.py` (3200+ lines)

#### Database (Data Layer)
- **Technology**: MySQL
- **Responsibilities**: Data persistence, relationships, data integrity
- **Encoding**: UTF8MB4 for emoji/special character support

---

## Problem Statement

### Current Challenges

Modern students face challenges in managing academic workload:

1. **Lack of Study Pattern Awareness**: Students struggle to understand their study habits
2. **Burnout Risk**: Poor study-life balance leads to academic burnout
3. **Inefficient Material Processing**: Time-consuming manual question creation
4. **Limited Self-Assessment**: Lack of integrated insight systems
5. **Fragmented Data**: Study information scattered across platforms

### Solution: LearnSmart AI

- Study Pattern Analyzer with analytics
- Productivity Score Calculator
- ML-based Burnout Risk Prediction
- AI Chatbot for document Q&A (Google Gemini)
- Academic Performance Tracker (matrix tables)
- Personalized Study Suggestions
- Comprehensive Dashboard with visualizations

### Objectives

**Primary:**
- Develop web-based learning management system
- Implement machine learning for burnout prediction
- Integrate AI for document-based Q&A
- Create intuitive user interface
- Ensure data security and privacy

**Secondary:**
- Provide actionable insights
- Support academic performance improvement
- Prevent burnout through early detection
- Automate study material processing
- Maintain comprehensive learning history

---

## Project Abstract

LearnSmart AI is an intelligent learning management system that helps students optimize study habits, prevent burnout, and enhance academic performance through data-driven insights and AI-powered recommendations.

The system combines traditional web technologies with machine learning and artificial intelligence. Key features include secure authentication with password hashing, study pattern tracking, productivity scoring, ML-based burnout prediction, AI chatbot integration (Google Gemini), academic performance tracking with matrix tables, and personalized recommendations.

Built using Flask (Python) backend, HTML/CSS/JavaScript frontend, and MySQL database. Machine learning uses scikit-learn for burnout prediction, while AI integration uses Google Gemini API for document-based Q&A. The application follows RESTful API principles and implements security best practices.

**Keywords:** Learning Management System, Machine Learning, Artificial Intelligence, Student Analytics, Burnout Prediction, Educational Technology

---

## Module Documentation

### 1. Authentication Module

**Purpose**: Secure user registration and login

**Features**:
- User registration (name, email, username, password)
- Email and username validation
- bcrypt password hashing (12 rounds)
- Session-based authentication
- Protected routes with decorators
- Client and server-side validation

**Implementation**:
- Password hashing: `bcrypt.hashpw(password, bcrypt.gensalt(12))`
- Session management: Flask sessions with encrypted cookies
- Route protection: `@require_auth` decorator
- Validation: Email validation, password strength, unique constraints

**Security**:
- bcrypt adaptive hashing
- Session cookies with HttpOnly, SameSite
- SQL injection prevention (parameterized queries)
- XSS protection (input sanitization)

---

### 2. Study Pattern Analyzer Module

**Purpose**: Track and analyze daily study habits

**Features**:
- Daily data entry (study hours, sleep, breaks, screen time, mood)
- Edit and delete functionality
- One entry per day (auto-updates existing)
- Recent history display
- MySQL storage

**Data Fields**:
- Study Hours (0-24, decimal)
- Sleep Hours (0-24, decimal)
- Break Time (0-24, decimal)
- Screen Time (0-24, decimal)
- Mood Level (Low/Medium/High)
- Study Date

**API Endpoints**:
- `GET /study-pattern` - Display page
- `POST /api/study-pattern` - Save data
- `GET /api/study-pattern/<id>` - Get specific pattern
- `PUT /api/study-pattern/<id>` - Update pattern
- `DELETE /api/study-pattern/<id>` - Delete pattern

---

### 3. Productivity Score Calculator Module

**Purpose**: Calculate and display productivity score (0-100)

**Formula**:
```
Total Score = Study Score (30) + Sleep Score (30) + Break Score (20) + Screen Score (20)
```

**Component Weights**:
- **Study Hours**: 30 points (optimal: 4-8h, peak: 6h)
- **Sleep Hours**: 30 points (optimal: 7-9h, peak: 8h)
- **Break Time**: 20 points (optimal: 1-3h, peak: 2h)
- **Screen Time**: 20 points (optimal: ≤8h, penalty after 10h)

**Scoring Logic**:
- Bell curve for optimal ranges
- Linear interpolation for deviations
- Penalty for extreme values
- Maximum 100 points

**Calculation**: Rule-based algorithm (no ML)

---

### 4. Burnout Risk Prediction Module (Machine Learning)

**Purpose**: Predict burnout risk using hybrid approach

**Approach**: Rule-based checks FIRST, then ML for borderline cases

**Rules (Checked BEFORE ML)**:
1. Sleep < 4 hours → **HIGH RISK**
2. Sleep < 4 hours AND Screen > 8 hours → **HIGH RISK**
3. Study > 9 hours AND Sleep < 5 hours → **HIGH RISK**

**Machine Learning**:
- **Model**: Decision Tree Classifier (default) or Logistic Regression
- **Features**: study_hours, sleep_hours, break_time, screen_time, mood_score
- **Output**: Low/Medium/High risk
- **Confidence**: 70-95% (never 100%)
- **Accuracy**: ~85-90%

**Training**:
- Synthetic dataset (500 samples)
- Script: `generate_burnout_dataset.py`
- Training: `train_burnout_model.py`
- Model file: `burnout_model.pkl`

**Prediction Flow**:
1. Check rules first (extreme cases)
2. If no rule matches → Use ML
3. ML provides prediction + confidence
4. Confidence clamped to 70-95%

---

### 5. AI Chatbot Module (Google Gemini)

**Purpose**: Answer questions based on uploaded documents

**Features**:
- PDF and TXT file upload
- Text extraction (PyPDF2 for PDFs)
- Document-based context for responses
- Conversation history storage
- Markdown-formatted responses

**Integration**:
- API: Google Gemini (gemini-1.5-flash, gemini-1.0-pro, gemini-pro)
- Model fallback: Tries multiple models if one fails
- API Key: Stored in `.env` as `GEMINI_API_KEY`

**API Endpoints**:
- `GET /chatbot` - Chatbot page
- `POST /api/upload-document` - Upload file
- `POST /api/chat` - Send message
- `DELETE /api/delete-document/<id>` - Delete document

**Text Processing**:
- PDF extraction: PyPDF2
- UTF8MB4 encoding support
- Text cleaning and normalization

---

### 6. Academic Performance Tracker Module

**Purpose**: Track academic performance in matrix/grid format

**Features**:
- Matrix table layout
- Grouped by Class/Semester
- Rows = Exam Names
- Columns = Subject Names
- Display: Scored/Total (e.g., 55/100)
- Percentage calculation
- Add and delete records

**Data Structure**:
- Class/Semester (e.g., "Class 11", "Semester 1")
- Exam Name (e.g., "Terminal 1", "PT-1", "IA-1")
- Subject Name (e.g., "English", "Maths", "Science")
- Marks Scored (decimal)
- Total Marks (decimal)

**Display Format**:
```
Class 11
----------------------------------------------------
Exam Name | English | Maths | Science | Social
----------------------------------------------------
Terminal 1 | 55/100 | 70/100 | 96/100 | 80/100
PT 1       | 35/50  | 40/50  | 41/50  | 50/50
```

**API Endpoints**:
- `GET /academic-performance` - Display page
- `GET /api/academic-performance` - Get all data (grouped)
- `POST /api/academic-performance` - Add record
- `DELETE /api/academic-performance/<id>` - Delete record

---

### 7. Study Suggestions Module

**Purpose**: Provide personalized study recommendations

**Approach**: Rule-based engine

**Rules Examples**:
- IF sleep < 6h → "Increase Sleep Hours" (High Priority)
- IF study > 10h → "Reduce Study Hours" (High Priority)
- IF break < 0.5h → "Take More Breaks" (High Priority)
- IF multiple issues → "Rebalance Routine" (High Priority)

**Priority Levels**:
- **High**: Critical issues requiring immediate attention
- **Medium**: Important but not urgent
- **Low**: General recommendations

**Process**:
1. Analyze current study patterns
2. Check productivity score
3. Check burnout risk
4. Apply rule-based conditions
5. Generate prioritized suggestions
6. Return top 5-10 suggestions

---

### 8. Dashboard Module

**Purpose**: Display comprehensive overview of user data

**Components**:
- Productivity Score (with breakdown)
- Burnout Risk Prediction
- Personalized Suggestions
- Weekly Study Hours Chart (Chart.js)
- Sleep vs Productivity Chart (Chart.js)
- Recent Study History

**Visualizations**:
- **Bar Chart**: Weekly study hours (last 7 days)
- **Dual-Axis Line Chart**: Sleep hours vs Productivity score
- Interactive tooltips
- Responsive design

**Data Sources**:
- `/api/dashboard/weekly-study-hours`
- `/api/dashboard/sleep-vs-productivity`
- Productivity score calculation
- Burnout prediction
- Suggestions engine

---

### 9. History Management Module

**Purpose**: Display historical data in tabbed interface

**Tabs**:
- Study Patterns History
- Burnout Predictions History

**Features**:
- Tabbed interface
- Tabular display
- Date sorting (newest first)
- Count badges
- User-specific filtering

**API Endpoints**:
- `GET /history` - History page
- `GET /api/history/study-patterns` - Study patterns data
- `GET /api/history/burnout-predictions` - Predictions data

---

## Database Schema

### Tables

#### users (Primary Table)
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- bcrypt hash (60 chars)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### study_patterns (Child Table)
```sql
CREATE TABLE study_patterns (
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
);
```

#### burnout_predictions (Child Table)
```sql
CREATE TABLE burnout_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    study_date DATE NOT NULL,
    study_hours DECIMAL(4,2) NOT NULL,
    sleep_hours DECIMAL(4,2) NOT NULL,
    break_time DECIMAL(4,2) NOT NULL,
    screen_time DECIMAL(4,2) NOT NULL,
    mood_score INT NOT NULL,
    predicted_risk ENUM('Low', 'Medium', 'High') NOT NULL,
    confidence DECIMAL(5,2),  -- Prediction strength (70-95)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### user_documents (Child Table)
```sql
CREATE TABLE user_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type ENUM('PDF', 'TEXT') NOT NULL,
    extracted_text LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### chat_conversations (Child Table)
```sql
CREATE TABLE chat_conversations (
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
);
```

#### academic_performance (Child Table)
```sql
CREATE TABLE academic_performance (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Relationships

- **One-to-Many**: users → study_patterns, burnout_predictions, user_documents, chat_conversations, academic_performance
- **Foreign Keys**: All child tables have `user_id` FK with CASCADE DELETE
- **Data Isolation**: All queries filter by `user_id = session['user_id']`

---

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Home page | No |
| GET | `/login` | Login page | No |
| POST | `/login` | Authenticate user | No |
| GET | `/register` | Registration page | No |
| POST | `/register` | Create account | No |
| GET | `/logout` | Logout | Yes |

### Dashboard Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/dashboard` | Dashboard page | Yes |
| GET | `/api/dashboard/weekly-study-hours` | Weekly chart data | Yes |
| GET | `/api/dashboard/sleep-vs-productivity` | Correlation chart data | Yes |

### Study Pattern Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/study-pattern` | Study pattern page | Yes |
| POST | `/api/study-pattern` | Save study data | Yes |
| GET | `/api/study-pattern` | Get all patterns | Yes |
| GET | `/api/study-pattern/<id>` | Get specific pattern | Yes |
| PUT | `/api/study-pattern/<id>` | Update pattern | Yes |
| DELETE | `/api/study-pattern/<id>` | Delete pattern | Yes |

### Academic Performance Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/academic-performance` | Academic performance page | Yes |
| GET | `/api/academic-performance` | Get all data (grouped) | Yes |
| POST | `/api/academic-performance` | Add record | Yes |
| DELETE | `/api/academic-performance/<id>` | Delete record | Yes |

### AI Chatbot Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/chatbot` | Chatbot page | Yes |
| POST | `/api/upload-document` | Upload PDF/TXT | Yes |
| POST | `/api/chat` | Send chat message | Yes |
| DELETE | `/api/delete-document/<id>` | Delete document | Yes |

### History Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/history` | History page | Yes |
| GET | `/api/history/study-patterns` | Study patterns history | Yes |
| GET | `/api/history/burnout-predictions` | Predictions history | Yes |

### Health Endpoint

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | No |

---

## Implementation Details

### Security Implementation

**Password Hashing:**
```python
import bcrypt

# Registration
salt = bcrypt.gensalt(12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

# Login
if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
    # Login successful
```

**SQL Injection Prevention:**
```python
# ✅ Safe (parameterized)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ❌ Unsafe (NEVER DO THIS)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**Session Management:**
```python
# Session creation
session['user_id'] = user['id']
session['username'] = user['username']
session.permanent = True

# Session validation
def is_authenticated():
    return 'user_id' in session
```

### Machine Learning Implementation

**Model Training:**
```python
from sklearn.tree import DecisionTreeClassifier
import joblib

# Load dataset
X_train, y_train = load_dataset()

# Train model
model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'burnout_model.pkl')
```

**Prediction:**
```python
# Load model
model = joblib.load('burnout_model.pkl')

# Prepare features
features = np.array([[study_hours, sleep_hours, break_time, screen_time, mood_score]])

# Predict
prediction = model.predict(features)[0]
probabilities = model.predict_proba(features)[0]
```

### AI Integration (Gemini)

**API Configuration:**
```python
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Try multiple models
models_to_try = ['gemini-1.5-flash', 'gemini-1.0-pro', 'gemini-pro']
for model_name in models_to_try:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except:
        continue
```

### Database Encoding (UTF8MB4)

**Table Creation:**
```sql
CREATE TABLE user_documents (
    ...
    extracted_text LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    ...
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Connection Configuration:**
```python
app.config['MYSQL_CHARSET'] = 'utf8mb4'

# Set connection charset
cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci")
```

---

## Viva Presentation Guide

### Common Questions & Answers

#### Q1: What is LearnSmart AI?
**Answer:** LearnSmart AI is an intelligent learning management system that combines web development, machine learning, and AI to help students optimize study habits, prevent burnout, and track academic performance. It includes study pattern tracking, productivity scoring, ML-based burnout prediction, AI chatbot for document Q&A, and academic performance tracking.

#### Q2: Explain the system architecture.
**Answer:** Three-tier architecture:
1. **Presentation Layer**: HTML/CSS/JavaScript frontend
2. **Application Layer**: Flask (Python) backend with business logic
3. **Data Layer**: MySQL database for persistence

#### Q3: How does burnout prediction work?
**Answer:** Hybrid approach:
1. **Rules First**: Check extreme cases (sleep < 4h → High, study > 9h + sleep < 5h → High)
2. **ML Second**: If no rule matches, use Decision Tree Classifier
3. **Features**: study_hours, sleep_hours, break_time, screen_time, mood_score
4. **Output**: Low/Medium/High with 70-95% confidence

#### Q4: How does the AI chatbot work?
**Answer:** Uses Google Gemini API:
1. User uploads PDF/TXT document
2. Text extracted and stored in database
3. User asks questions
4. System sends document context + question to Gemini
5. AI generates response based on document content
6. Response formatted as Markdown and displayed

#### Q5: Explain the database design.
**Answer:** Relational model with:
- **Parent Table**: users
- **Child Tables**: study_patterns, burnout_predictions, user_documents, chat_conversations, academic_performance
- **Relationships**: One-to-many with foreign keys
- **CASCADE DELETE**: Auto-cleanup when user deleted
- **Data Isolation**: All queries filter by user_id

#### Q6: How do you ensure security?
**Answer:** Multiple layers:
1. bcrypt password hashing (12 rounds)
2. Session-based authentication
3. Parameterized SQL queries (SQL injection prevention)
4. Input validation (client & server)
5. User data isolation (user_id filtering)
6. Secure file upload handling
7. XSS protection (input sanitization)

#### Q7: Why Flask and not Django?
**Answer:** Flask chosen because:
- Lightweight and flexible
- Easier to understand for academic project
- Better for demonstrating individual components
- No enforced structure (more control)

#### Q8: What are the limitations?
**Answer:**
- ML model uses synthetic data (not real-world)
- Simple NLP (keyword-based, no semantic understanding)
- Manual data entry (no automatic tracking)
- Web-only (no mobile app)
- Basic analytics (charts only)

#### Q9: What future enhancements?
**Answer:**
- Real-world ML training data
- Advanced NLP (spaCy/NLTK)
- Mobile app development
- Automatic study tracking
- Advanced analytics
- Password reset functionality

---

## Installation & Setup

### Prerequisites
- Python 3.7+
- MySQL Server
- pip (Python package manager)

### Step-by-Step Installation

1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create MySQL Database:**
   ```sql
   CREATE DATABASE learnsmart_ai;
   ```

4. **Configure Environment:**
   Create `.env` file:
   ```
   SECRET_KEY=your-secret-key-here
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DB=learnsmart_ai
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. **Train ML Model (Optional):**
   ```bash
   python generate_burnout_dataset.py
   python train_burnout_model.py
   ```

6. **Create Academic Performance Table (Optional):**
   ```bash
   python create_academic_table.py
   ```

7. **Run Application:**
   ```bash
   python app.py
   ```

8. **Access:** `http://localhost:5000`

### Troubleshooting

**MySQL Connection Error:**
- Verify MySQL server is running
- Check `.env` credentials
- Ensure database exists

**Module Not Found:**
- Activate virtual environment
- Run `pip install -r requirements.txt`

**Encoding Error:**
- Run `python fix_encoding.py`

**Gemini API Error:**
- Check API key in `.env`
- Verify API key is valid
- Restart Flask app

---

## Future Enhancements

### Short-term
- Password reset functionality
- Real-world ML training data
- Advanced NLP integration
- Mobile-responsive improvements
- Export data functionality

### Medium-term
- Mobile app development
- Calendar integration
- Automatic study tracking
- Advanced analytics
- Personalization engine

### Long-term
- Deep learning models
- Multi-platform support
- Enterprise features
- Research collaboration
- Advanced AI integrations

---

## Quick Reference

### Technology Stack
- **Backend**: Flask 3.0.0, Python 3.7+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: MySQL (UTF8MB4)
- **ML**: scikit-learn 1.3.2
- **AI**: google-generativeai (Gemini)
- **Visualization**: Chart.js 4.4.0
- **Security**: bcrypt 4.1.2

### Key Features
1. ✅ Secure Authentication
2. ✅ Study Pattern Tracking
3. ✅ Productivity Scoring
4. ✅ Burnout Prediction (ML)
5. ✅ AI Chatbot (Gemini)
6. ✅ Academic Performance Tracker
7. ✅ Study Suggestions
8. ✅ Dashboard Visualizations
9. ✅ History Management

### Database Tables
- users, study_patterns, burnout_predictions
- user_documents, chat_conversations
- academic_performance

---

**This documentation provides comprehensive information about LearnSmart AI. For quick setup, refer to README.md. For viva preparation, focus on the Viva Presentation Guide section above.**


