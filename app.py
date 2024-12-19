from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studysitare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'student_login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    semester = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    completed_topics = db.Column(db.Integer, default=0)
    total_topics = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        password = request.form.get('password')
        
        user = User.query.filter_by(student_id=student_id, is_admin=False).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid student ID or password', 'error')
            
    return render_template('student_login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, is_admin=True).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('admin_login.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name')
        student_id = request.form.get('student_id')
        semester = request.form.get('semester')
        password = request.form.get('password')
        
        if User.query.filter_by(student_id=student_id).first():
            flash('Student ID already registered', 'error')
            return redirect(url_for('student_register'))
            
        user = User(
            name=name,
            student_id=student_id,
            semester=semester,
            is_admin=False
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('student_login'))
        except:
            db.session.rollback()
            flash('Error during registration', 'error')
            
    return render_template('student_register.html')

@app.route('/admin/register', methods=['GET', 'POST'])
@admin_required
def admin_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('admin_register'))
            
        user = User(
            name=name,
            email=email,
            is_admin=True
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Admin registration successful!', 'success')
            return redirect(url_for('admin_login'))
        except:
            db.session.rollback()
            flash('Error during registration', 'error')
            
    return render_template('admin_register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
        
    # Get subjects for current semester
    subjects = Subject.query.filter_by(semester=current_user.semester).all()
    
    # Get progress for each subject
    progress_data = Progress.query.filter_by(user_id=current_user.id).all()
    
    # Calculate overall progress
    total_completed = sum(p.completed_topics for p in progress_data)
    total_topics = sum(p.total_topics for p in progress_data) if progress_data else 0
    overall_progress = round((total_completed / total_topics * 100) if total_topics > 0 else 0)
    
    return render_template('dashboard.html', 
                         subjects=subjects,
                         progress=progress_data,
                         overall_progress=overall_progress,
                         completed_topics=total_completed,
                         total_topics=total_topics)

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    subjects = Subject.query.all()
    students = User.query.filter_by(is_admin=False).all()
    return render_template('admin_dashboard.html', subjects=subjects, students=students)

@app.route('/subject/<int:subject_id>')
@login_required
def subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if not current_user.is_admin and current_user.semester != subject.semester:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    return render_template('subject.html', subject=subject)

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@studysitare.com').first()
        if not admin:
            admin = User(
                name='Admin',
                email='admin@studysitare.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Add some sample subjects
        subjects = [
            Subject(name='Mathematics', semester=1, description='Basic mathematics and calculus'),
            Subject(name='Physics', semester=1, description='Classical mechanics and thermodynamics'),
            Subject(name='Programming', semester=2, description='Introduction to programming concepts'),
            Subject(name='Database Systems', semester=2, description='Database design and SQL')
        ]
        
        for subject in subjects:
            existing = Subject.query.filter_by(name=subject.name, semester=subject.semester).first()
            if not existing:
                db.session.add(subject)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)