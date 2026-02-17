# from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin

# db = SQLAlchemy()

# # Link table for Student-Course enrollment
# enrollment = db.Table('enrollment',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
# )

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)
#     role = db.Column(db.String(10), nullable=False) # 'student', 'faculty', 'admin'
#     # submissions = db.relationship('Submission', backref='author', lazy=True)
#     courses = db.relationship('Course', secondary=enrollment, backref='students')

# class Course(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     code = db.Column(db.String(20), unique=True, nullable=False)
#     faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     faculty = db.relationship('User', backref='managed_courses', lazy=True)
#     # This link is necessary for the dashboard to show assignments
#     assignments = db.relationship('Assignment', backref='course', lazy=True)

# class Submission(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
#     timestamp = db.Column(db.String(50))
#     filename = db.Column(db.String(100))
#     text_content = db.Column(db.Text)
#     content_hash = db.Column(db.String(64))
#     status = db.Column(db.String(20))
#     score = db.Column(db.Float)
#     assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
#     author = db.relationship('User', backref='submissions', lazy=True)

# class Assignment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     instructions = db.Column(db.Text)      # This matches the missing column!
#     question_file = db.Column(db.String(100))
#     deadline = db.Column(db.DateTime, nullable=False)
#     attempt_limit = db.Column(db.Integer, default=3)
#     course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
#     is_published = db.Column(db.Boolean, default=False)
#     submissions = db.relationship('Submission', backref='assignment', lazy=True)
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Helper table for Many-to-Many relationship
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False) # 'admin', 'faculty', 'student'
    
    # Students use this to see enrolled courses
    enrolled_courses = db.relationship('Course', secondary=enrollments, 
                                     backref=db.backref('students', lazy='dynamic'))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Faculty uses this to see courses they teach
    faculty = db.relationship('User', backref=db.backref('managed_courses', lazy=True))
    assignments = db.relationship('Assignment', backref='course', lazy=True)
    
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=False) 
    attempt_limit = db.Column(db.Integer, default=3)
    question_file = db.Column(db.String(255), nullable=True) 
    is_published = db.Column(db.Boolean, default=True) 
    
    submissions = db.relationship('Submission', backref='assignment', lazy=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    content_hash = db.Column(db.String(64), nullable=True) # Add this line
    filename = db.Column(db.String(100))
    score = db.Column(db.Float, default=0.0)
    # status = db.Column(db.String(20)) # 'accepted' or 'rejected'
    status = db.Column(db.String(20)) # 'accepted' or 'rejected'
    # score = db.Column(db.Float)
    reason = db.Column(db.String(255)) # ADD THIS LINE
    # Optimization: Use DateTime for easier sorting/filtering in reports
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    author = db.relationship('User', backref='user_submissions')