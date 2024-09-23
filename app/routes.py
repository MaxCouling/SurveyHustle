#routes.py
from flask_wtf import FlaskForm

import os

from flask import render_template, redirect, url_for, flash, request

from app import app, db
from app.models import User, Survey, Question, Response, UserSurveyProgress


from app.forms import RegistrationForm, LoginForm, UploadSurveyForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from wtforms import StringField, TextAreaField, IntegerField, RadioField
from wtforms.validators import DataRequired, NumberRange

import csv
import json

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#from forms import RegistrationForm

# routes.py
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        print("Form validated successfully")
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_business=form.is_business.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        print("User added to the database")
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    else:
        print("Form validation failed")
        print(form.errors)
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
#@login_required
def dashboard():
    return render_template('dashboard.html', user = current_user)

@app.route('/explore')
@login_required
def explore():
    surveys = Survey.query.all()
    return render_template('explore.html', surveys=surveys)

@app.route('/profile')
#@login_required
def profile():
    return render_template('profile.html')

@app.route('/survey')
#@login_required
def survey():
    return render_template('survey.html')

@app.route('/settings')
#@login_required
def settings():
    return render_template('settings.html')


# routes.py

@ app.route('/upload_survey', methods=['GET', 'POST'])
@ login_required
def upload_survey():
    if not current_user.is_business:
        flash('You must be a business user to upload surveys.', 'danger')
        return redirect(url_for('dashboard'))
    form = UploadSurveyForm()
    if form.validate_on_submit():
        # Save survey details
        survey = Survey(
            title=form.title.data,
            description=form.description.data,
            terms_and_conditions=form.terms_and_conditions.data,
            total_payout=form.total_payout.data,
            owner=current_user
        )
        db.session.add(survey)
        db.session.commit()

        # Process CSV file
        file = form.csv_file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads/', filename)


        file.save(filepath)

        # Read CSV and create questions
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            order = 0
            for row in reader:
                question = Question(
                    survey_id=survey.id,
                    question_text=row['question_text'],
                    question_type=row['question_type'],
                    choices=row.get('choices', None),
                    order=order
                )
                db.session.add(question)
                order += 1
        db.session.commit()
        flash('Survey uploaded successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        if request.method == 'POST':
            flash('Please correct the errors below.', 'danger')
            print(form.errors)  # For debugging
    return render_template('upload_survey.html', form=form)

@app.route('/start_survey/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def start_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    progress = UserSurveyProgress.query.filter_by(user_id=current_user.id, survey_id=survey.id).first()
    if progress and progress.current_question_index > 0:
        return redirect(url_for('take_survey', survey_id=survey.id))
    else:
        if request.method == 'POST':
            if 'accept' in request.form:
                progress = UserSurveyProgress(user_id=current_user.id, survey_id=survey.id)
                db.session.add(progress)
                db.session.commit()
                return redirect(url_for('take_survey', survey_id=survey.id))
            else:
                flash('You must accept the terms to proceed.', 'danger')
                return redirect(url_for('explore'))
        return render_template('survey_terms.html', survey=survey)

# routes.py

@app.route('/take_survey/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def take_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    progress = UserSurveyProgress.query.filter_by(user_id=current_user.id, survey_id=survey.id).first()
    if not progress or progress.completed:
        flash('Survey not found or already completed.', 'danger')
        return redirect(url_for('explore'))

    questions = survey.questions.order_by(Question.order).all()
    total_questions = len(questions)

    if progress.current_question_index >= total_questions:
        progress.completed = True
        db.session.commit()
        flash('Survey completed! Thank you.', 'success')
        return redirect(url_for('dashboard'))

    question = questions[progress.current_question_index]

    class DynamicSurveyForm(FlaskForm):
        pass
    print(question.question_type)
    if question.question_type == 'multiple_choice':
        choices = json.loads(question.choices)
        setattr(DynamicSurveyForm, 'answer', RadioField(
            question.question_text,
            choices=[(choice, choice) for choice in choices],
            validators=[DataRequired()]
        ))
    elif question.question_type == 'text':
        setattr(DynamicSurveyForm, 'answer', StringField(
            question.question_text, validators=[DataRequired()]
        ))
    elif question.question_type == 'rating':
        setattr(DynamicSurveyForm, 'answer', IntegerField(
            question.question_text,
            validators=[DataRequired(), NumberRange(min=1, max=10)]
        ))
    else:
        flash('Unknown question type.', 'danger')
        return redirect(url_for('dashboard'))

    form = DynamicSurveyForm()

    if form.validate_on_submit():
        print("Form validated successfully.")
        # Retrieve the answer from the form
        answer = form.answer.data
        print(f"Received answer: {answer}")

        # Save the response
        response = Response(
            user_id=current_user.id,
            #survey_id=survey.id,
            question_id=question.id,
            answer=answer
        )
        db.session.add(response)
        print("Response added to the database.")

        # Update progress
        progress.current_question_index += 1
        print(f"Updated current_question_index to {progress.current_question_index}")
        if progress.current_question_index >= total_questions:
            progress.completed = True
            flash('Survey completed! Thank you for your participation.', 'success')
            print("Survey completed by user.")
        db.session.commit()
        print("Progress committed to the database.")

    # Pass 'progress' and 'total_questions' to the template
    return render_template('take_survey.html', form=form, question=question, survey=survey, progress=progress, total_questions=total_questions)
