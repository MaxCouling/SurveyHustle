# models.py

from datetime import datetime
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    is_business = db.Column(db.Boolean, default=False)
    surveys = db.relationship('Survey', backref='owner', lazy='dynamic')
    responses = db.relationship('Response', backref='user', lazy='dynamic')
    survey_progress = db.relationship('UserSurveyProgress', backref='user', lazy='dynamic')
    balance = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    terms_and_conditions = db.Column(db.Text)
    total_payout = db.Column(db.Float)
    desired_respondents = db.Column(db.Integer)
    current_respondents = db.Column(db.Integer, default=0)
    per_question_payout = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('Question', backref='survey', lazy='dynamic')

    def __repr__(self):
        return f'<Survey {self.title}>'


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))
    question_text = db.Column(db.Text)
    question_type = db.Column(db.String(20))  # 'multiple_choice', 'short_answer', etc.
    choices = db.Column(db.Text)  # For multiple-choice questions; store as JSON string
    order = db.Column(db.Integer)  # Question order in the survey
    responses = db.relationship('Response', backref='question', lazy='dynamic')

    def __repr__(self):
        return f'<Question {self.question_text[:50]}>'

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    answer = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Response {self.id}>'

class UserSurveyProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))
    current_question_index = db.Column(db.Integer, default=0)
    payout = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<UserSurveyProgress User:{self.user_id} Survey:{self.survey_id}>'

