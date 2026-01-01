# LearnSmart AI - Intelligent Learning Management System

A comprehensive full-stack web application for intelligent learning management, built with Flask (Python) backend and modern HTML/CSS/JavaScript frontend. This project integrates machine learning, natural language processing, and data analytics to help students optimize their study habits, prevent burnout, and track academic performance.

## 🎯 Project Overview

LearnSmart AI is an intelligent learning management system designed to help students:
- Track and analyze study patterns
- Predict burnout risk using machine learning
- Chat with AI about uploaded documents (Google Gemini)
- Track academic performance with matrix tables
- Receive personalized study improvement suggestions
- Visualize learning data with interactive charts
- Maintain comprehensive history of all activities

## ✨ Key Features

### 🔐 Authentication System
- Secure user registration (name, email, username, password)
- bcrypt password hashing (12 rounds)
- Session-based authentication
- Protected routes
- Client and server-side validation

### 📊 Study Pattern Analyzer
- Daily study data tracking (study hours, sleep, breaks, screen time, mood)
- MySQL database storage
- Recent history display
- Edit and delete functionality
- One entry per day (auto-updates)

### 📈 Productivity Score Calculator
- Rule-based scoring algorithm (0-100 scale)
- Component-wise breakdown (Study: 30%, Sleep: 30%, Break: 20%, Screen: 20%)
- Configurable weights
- Clear formula documentation

### ⚠️ Burnout Risk Prediction (Machine Learning)
- Hybrid approach: Rule-based checks + ML prediction
- Rules checked BEFORE ML (sleep < 4h → High, study > 9h + sleep < 5h → High)
- Decision Tree Classifier (default) or Logistic Regression
- ML-based risk prediction (Low/Medium/High)
- Prediction strength: 70-95% (never 100%)
- Automatic prediction on study data submission

### 🤖 AI Chatbot (Google Gemini)
- PDF and text file upload support
- Document-based context for intelligent responses
- Integration with Google Gemini API
- Conversation history storage
- Markdown-formatted responses

### 📊 Academic Performance Tracker
- Matrix/Grid table layout
- Grouped by Class/Semester
- Rows = Exams, Columns = Subjects
- Display format: Scored/Total (e.g., 55/100)
- Add, view, and delete records

### 💡 Study Suggestions & Insights
- Rule-based recommendation engine
- Personalized suggestions based on study patterns
- Priority-based recommendations (High/Medium/Low)
- Non-medical, student-friendly language

### 📊 Student Dashboard
- Productivity score display with breakdown
- Burnout risk visualization
- Weekly study hours chart (Chart.js)
- Sleep vs productivity correlation chart
- Recent study history
- Personalized suggestions display

### 📚 History Management
- Study pattern history
- Burnout prediction history
- Tabbed interface
- Tabular display format
- Proper database relationships

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: MySQL (Flask-MySQLdb)
- **ML Library**: scikit-learn 1.3.2
- **PDF Processing**: PyPDF2 3.0.1
- **Password Hashing**: bcrypt 4.1.2
- **AI Integration**: google-generativeai (Gemini)
- **Data Processing**: pandas 2.1.4, numpy 1.26.2

### Frontend
- **Markup**: HTML5
- **Styling**: CSS3 (custom, responsive)
- **Scripting**: JavaScript (ES6+)
- **Visualization**: Chart.js 4.4.0

### Database
- **RDBMS**: MySQL
- **Relationships**: Foreign keys with CASCADE DELETE
- **Encoding**: UTF8MB4 for emoji/special character support

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- MySQL Server
- pip (Python package manager)

### Installation

1. **Clone/Download the project**

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL database:**
   ```sql
   CREATE DATABASE learnsmart_ai;
   ```

5. **Configure environment:**
   - Copy `env_template.txt` to `.env`
   - Update MySQL credentials in `.env`
   - Add `GEMINI_API_KEY=your_api_key` (get from https://makersuite.google.com/app/apikey)

6. **Train ML model (optional but recommended):**
   ```bash
   python generate_burnout_dataset.py
   python train_burnout_model.py
   ```

7. **Create academic performance table (if needed):**
   ```bash
   python create_academic_table.py
   ```

8. **Run the application:**
   ```bash
   python app.py
   ```

9. **Access:** `http://localhost:5000`

## 📁 Project Structure

```
LearnSmart AI/
│
├── app.py                      # Main Flask application
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables (create from env_template.txt)
├── env_template.txt            # Environment variables template
│
├── generate_burnout_dataset.py  # ML dataset generator
├── train_burnout_model.py      # ML model training script
├── create_academic_table.py    # Academic table creation script
├── fix_encoding.py             # Database encoding fix script
│
├── README.md                    # This file (project overview)
├── DOCUMENTATION.md             # Technical documentation
│
├── templates/                   # HTML templates
│   ├── index.html              # Home page
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # Student dashboard
│   ├── study_pattern.html      # Study pattern analyzer
│   ├── academic_performance.html # Academic performance tracker
│   ├── chatbot.html            # AI Chatbot
│   └── history.html            # History management
│
└── static/                      # Static files
    ├── css/
    │   └── style.css           # Main stylesheet
    └── js/
        ├── main.js             # Main JavaScript
        ├── auth.js             # Authentication
        ├── dashboard.js        # Dashboard & charts
        ├── study_pattern.js    # Study pattern form
        ├── academic_performance.js # Academic performance
        ├── history.js          # History management
        └── questions_generator.js # (legacy)
```

## 🔌 API Endpoints

### Authentication
- `GET /` - Home page
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /register` - Registration page
- `POST /register` - Create account
- `GET /logout` - Logout

### Dashboard
- `GET /dashboard` - Student dashboard
- `GET /api/dashboard/weekly-study-hours` - Chart data
- `GET /api/dashboard/sleep-vs-productivity` - Chart data

### Study Patterns
- `GET /study-pattern` - Study pattern page
- `POST /api/study-pattern` - Save study data
- `GET /api/study-pattern` - Get patterns
- `GET /api/study-pattern/<id>` - Get specific pattern
- `PUT /api/study-pattern/<id>` - Update pattern
- `DELETE /api/study-pattern/<id>` - Delete pattern

### Academic Performance
- `GET /academic-performance` - Academic performance page
- `GET /api/academic-performance` - Get all performance data
- `POST /api/academic-performance` - Add performance record
- `DELETE /api/academic-performance/<id>` - Delete record

### AI Chatbot
- `GET /chatbot` - Chatbot page
- `POST /api/upload-document` - Upload document (PDF/TXT)
- `POST /api/chat` - Send chat message
- `DELETE /api/delete-document/<id>` - Delete document

### History
- `GET /history` - History page
- `GET /api/history/study-patterns` - Study patterns history
- `GET /api/history/burnout-predictions` - Predictions history

### Health
- `GET /health` - Health check

## 🗄️ Database Schema

### Tables
- **users** - User accounts (id, name, username, email, password)
- **study_patterns** - Daily study data (linked to users)
- **burnout_predictions** - ML predictions (linked to users)
- **user_documents** - Uploaded documents (PDF/TXT)
- **chat_conversations** - Chat history
- **academic_performance** - Academic performance records

### Relationships
- One-to-Many: users → study_patterns, burnout_predictions, user_documents, chat_conversations, academic_performance
- Foreign keys with CASCADE DELETE
- Data isolation (user_id filtering)

## 🔒 Security Features

- ✅ bcrypt password hashing (12 rounds)
- ✅ Session-based authentication
- ✅ SQL injection prevention (parameterized queries)
- ✅ Input validation (client and server-side)
- ✅ User data isolation
- ✅ Secure file upload handling
- ✅ Session security (HttpOnly, SameSite)
- ✅ XSS protection (input sanitization)

## 🐛 Troubleshooting

### Common Issues

1. **MySQL Connection Error**
   - Verify MySQL server is running
   - Check `.env` credentials
   - Ensure database exists

2. **Module Not Found**
   - Activate virtual environment
   - Run `pip install -r requirements.txt`

3. **Model Not Found**
   - Run `python train_burnout_model.py`

4. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`

5. **Encoding Error (utf8mb4)**
   - Run `python fix_encoding.py`

6. **Gemini API Error**
   - Check API key in `.env` file
   - Verify API key is valid
   - Restart Flask app after adding key

## 📝 License

This project is created for academic purposes. Feel free to use and modify as needed.

## 👤 Author

Final Year Project - LearnSmart AI

---

**LearnSmart AI - Empowering Students Through Intelligent Learning Management! 🚀**
