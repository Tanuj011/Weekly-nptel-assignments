from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///nptel.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Custom Jinja filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(value):
    return json.loads(value) if value else []

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.relationship('UserProgress', backref='user', lazy=True)

class Week(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='upcoming')  # upcoming, active, completed
    questions = db.relationship('Question', backref='week', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON string
    answer = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=1)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week_id = db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    revealed = db.Column(db.Boolean, default=False)
    revealed_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    weeks = Week.query.order_by(Week.week_number).all()
    
    # Calculate progress for each week
    week_stats = []
    for week in weeks:
        total_questions = len(week.questions)
        revealed = UserProgress.query.filter_by(
            user_id=current_user.id, 
            week_id=week.id, 
            revealed=True
        ).count()
        
        week_stats.append({
            'week': week,
            'total': total_questions,
            'revealed': revealed,
            'percentage': (revealed / total_questions * 100) if total_questions > 0 else 0
        })
    
    return render_template('dashboard.html', week_stats=week_stats)

@app.route('/week/<int:week_id>')
@login_required
def view_week(week_id):
    week = Week.query.get_or_404(week_id)
    questions = Question.query.filter_by(week_id=week_id).order_by(Question.question_number).all()
    
    # Get user progress
    user_progress = {}
    for question in questions:
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            week_id=week_id,
            question_id=question.id
        ).first()
        user_progress[question.id] = progress.revealed if progress else False
    
    return render_template('week.html', week=week, questions=questions, user_progress=user_progress)

@app.route('/toggle_answer/<int:question_id>', methods=['POST'])
@login_required
def toggle_answer(question_id):
    question = Question.query.get_or_404(question_id)
    
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        week_id=question.week_id,
        question_id=question_id
    ).first()
    
    if progress:
        progress.revealed = not progress.revealed
        progress.revealed_at = datetime.utcnow()
    else:
        progress = UserProgress(
            user_id=current_user.id,
            week_id=question.week_id,
            question_id=question_id,
            revealed=True
        )
        db.session.add(progress)
    
    db.session.commit()
    return {'success': True, 'revealed': progress.revealed}

@app.route('/admin/reset_db')
def reset_database():
    """Reset database - WARNING: Deletes all data!"""
    db.drop_all()
    db.create_all()
    return redirect(url_for('init_database'))

@app.route('/admin/init_db')
def init_database():
    db.create_all()
    
    # Delete existing Week 1 if it exists
    existing_week = Week.query.filter_by(week_number=1).first()
    if existing_week:
        db.session.delete(existing_week)
        db.session.commit()
    
    # Always add Week 1
    if True:
        # Add Week 1
        week1 = Week(
            week_number=1,
            title='Software Testing Fundamentals',
            due_date='2026-02-25, 23:59 IST',
            status='active'
        )
        db.session.add(week1)
        db.session.commit()
        
        # Add questions for Week 1
        questions_data = [
            {
                'number': 1,
                'text': 'Which of the following situations describe a software defect rather than a failure?',
                'options': '["a. A developer accidentally omits a boundary condition in an algorithm.", "b. A tester observes that the login module rejects valid credentials.", "c. The compiler issues a warning about a missing null-pointer check in the code.", "d. The deployed application displays an incorrect total in the inventory report when running on production data.", "e. A programmer encodes an incorrect formula in the code."]',
                'answer': 'a, c, e'
            },
            {
                'number': 2,
                'text': 'About half the effort of developing a typical software is spent on testing. But testing typically requires only 10% of the development time. Which one of the following explains this apparent anomaly?',
                'options': '["a. About half the effort of developing a typical software is spent on testing. But testing typically requires only 10% of the development time. Which one of the following explains this apparent anomaly?", "b. A team has too many coders as compared to testers", "c. Testing permits many parallel activities", "d. A team has too many designers as compared to coders", "e. Testers are more proficient as compared to other developers", "f. Managers force testers to work overtime"]',
                'answer': 'c'
            },
            {
                'number': 3,
                'text': 'Which of the following are true concerning verification in the context of waterfall-based development?',
                'options': '["a. Carried out by the testers", "b. Carried out by the developers", "c. Involves both static and dynamic activities", "d. Involves only static activities", "e. Involves only dynamic activities"]',
                'answer': 'b, c'
            },
            {
                'number': 4,
                'text': 'Which one of the following statements is true concerning unit testing?',
                'options': '["a. Carried out by the developers", "b. Involves testing the system as a whole", "c. Often carried out by a separate testing team", "d. Carried out by the customers", "e. Concerns validation of system functions"]',
                'answer': 'a'
            },
            {
                'number': 5,
                'text': 'Which of the following statements are not implied by the pesticide paradox?',
                'options': '["a. A software can be tested by repeated application of a testing methodology", "b. A software should be tested by the successive application of a wide range of testing methodologies", "c. The best testing methodology should be used towards the end of the testing phase", "d. A software should be tested by deploying the best among all the testing methodologies", "e. Any testing methodology is effective only for certain types of errors"]',
                'answer': 'a, c, d'
            },
            {
                'number': 6,
                'text': 'Which one of the following is true concerning integration testing?',
                'options': '["a. Carried out by the developers", "b. Involves testing the system as a whole", "c. Often carried out by a separate testing team", "d. Carried out by the customers", "e. Concerns validation of system functions"]',
                'answer': 'a'
            },
            {
                'number': 7,
                'text': 'What is the purpose of smoke test?',
                'options': '["a. Check the sanity of the developed system before actual testing can begin", "b. Carry out a final round of testing of the software after black-box and white-box test are over", "c. Carry out performance testing", "d. Carry out monkey testing", "e. Try multiple test cases concurrently to stress the system"]',
                'answer': 'a'
            },
            {
                'number': 8,
                'text': 'Which of the following should NOT be a goal of the test team?',
                'options': '["a. To find faults in the software.", "b. To assess whether the software is ready for release.", "c. To crash the software by using negative test cases", "d. To demonstrate that the software doesn\'t work.", "e. To prove that the software is correct."]',
                'answer': 'e'
            },
            {
                'number': 9,
                'text': 'Which one of the following activities is a validation activity?',
                'options': '["a. Design inspection", "b. Acceptance testing", "c. Code inspection", "d. Simulation", "e. Unit testing"]',
                'answer': 'b'
            },
            {
                'number': 10,
                'text': 'Which of the following are not true of the V model?',
                'options': '["a. During the requirements specification phase, system test cases are designed", "b. During the design phase, integration test cases are designed", "c. During the coding phase, unit test cases are designed", "d. During the design phase, unit test cases are designed", "e. During the requirements specification phase, integration test cases are designed"]',
                'answer': 'c, e'
            }
        ]
        
        for q_data in questions_data:
            question = Question(
                week_id=week1.id,
                question_number=q_data['number'],
                question_text=q_data['text'],
                options=q_data['options'],
                answer=q_data['answer'],
                points=1
            )
            db.session.add(question)
        
        db.session.commit()
        return 'Database initialized with Week 1 data!'
    
    return 'Database already initialized!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
