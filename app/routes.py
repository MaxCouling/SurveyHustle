#routes.py
from flask_wtf import FlaskForm

import os
import io
import csv

from flask import render_template, redirect, url_for, flash, request, send_file

from app import app, db
from app.models import User, Survey, Question, Response, UserSurveyProgress


from app.forms import RegistrationForm, LoginForm, UploadSurveyForm, AddBalanceForm, AcceptTermsForm, PayoutForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


from wtforms import StringField, TextAreaField, IntegerField, RadioField
from wtforms.validators import DataRequired, NumberRange

import json

from flask_mail import Message
from app import mail
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#from forms import RegistrationForm

# routes.py
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
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
        return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('profile'))
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
    surveys = Survey.query.filter_by(active=True).all()
    return render_template('explore.html', surveys=surveys)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = AddBalanceForm()
    if form.validate_on_submit():
        current_user.balance += 20
        db.session.commit()
        flash('Your balance has been updated.', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=current_user, form=form)

@app.route('/survey')
#@login_required
def survey():
    return render_template('survey.html')

@app.route('/settings')
#@login_required
def settings():
    return render_template('settings.html')


# routes.py

@app.route('/upload_survey', methods=['GET', 'POST'])
@login_required
def upload_survey():
    if not current_user.is_business:
        flash('You must be a business user to upload surveys.', 'danger')
        return redirect(url_for('profile'))

    form = UploadSurveyForm()
    if form.validate_on_submit():
        # Check if the user has enough balance
        if current_user.balance < form.total_payout.data:
            flash('Insufficient balance to upload survey.', 'danger')
            return redirect(url_for('profile'))

        # Deduct the total payout from the business user's balance
        current_user.balance -= form.total_payout.data

        # Create the survey
        survey = Survey(
            title=form.title.data,
            description=form.description.data,
            terms_and_conditions=form.terms_and_conditions.data,
            total_payout=form.total_payout.data,
            desired_respondents=form.desired_respondents.data,
            owner=current_user
        )
        db.session.add(survey)
        db.session.commit()  # Commit to get survey.id

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

        # Calculate per-question payout
        total_questions = survey.questions.count()
        per_question_payout = survey.total_payout / (survey.desired_respondents * total_questions)
        survey.per_question_payout = per_question_payout
        db.session.commit()

        flash('Survey uploaded successfully!', 'success')
        return redirect(url_for('profile'))
    else:
        if request.method == 'POST':
            flash('Please correct the errors below.', 'danger')
    return render_template('upload_survey.html', form=form)

@app.route('/start_survey/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def start_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)

    if not survey.active or survey.current_respondents >= survey.desired_respondents:
        survey.active = False
        db.session.commit()
        flash('This survey is no longer available.', 'danger')
        return redirect(url_for('explore'))

    progress = UserSurveyProgress.query.filter_by(user_id=current_user.id, survey_id=survey.id).first()
    if progress and progress.current_question_index > 0:
        return redirect(url_for('take_survey', survey_id=survey.id))
    else:
        form = AcceptTermsForm()
        if request.method == 'POST':
            if 'accept' in request.form:
                progress = UserSurveyProgress(user_id=current_user.id, survey_id=survey.id)
                db.session.add(progress)
                db.session.commit()
                return redirect(url_for('take_survey', survey_id=survey.id))
            else:
                flash('You must accept the terms to proceed.', 'danger')
                return redirect(url_for('explore'))
        return render_template('survey_terms.html', survey=survey, form=form)






@app.route('/take_survey/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def take_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)

    # Check if the survey is active
    if not survey.active:
        flash('This survey is no longer active.', 'danger')
        return redirect(url_for('explore'))

    # Ensure survey hasn't reached desired respondents
    if survey.current_respondents >= survey.desired_respondents:
        survey.active = False
        db.session.commit()
        flash('This survey has reached its maximum number of respondents.', 'info')
        return redirect(url_for('explore'))

    progress = UserSurveyProgress.query.filter_by(user_id=current_user.id, survey_id=survey.id).first()

    if not progress:
        flash('You have not started this survey yet.', 'danger')
        return redirect(url_for('explore'))

    if progress.completed:
        flash('You have already completed this survey.', 'info')
        return redirect(url_for('profile'))

    questions = survey.questions.order_by(Question.order).all()
    total_questions = len(questions)

    if progress.current_question_index >= total_questions:
        progress.completed = True
        # Increment current respondents
        survey.current_respondents += 1
        if survey.current_respondents >= survey.desired_respondents:
            survey.active = False
        db.session.commit()
        flash('Survey completed! Thank you.', 'success')
        return redirect(url_for('profile'))

    question = questions[progress.current_question_index]

    class DynamicSurveyForm(FlaskForm):
        pass

    if question.question_type == 'multiple_choice':
        try:
            choices = json.loads(question.choices)
        except json.JSONDecodeError:
            flash('Invalid choices format for multiple choice question.', 'danger')
            return redirect(url_for('profile'))
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
        return redirect(url_for('profile'))

    form = DynamicSurveyForm()

    # Handle form submission
    if form.validate_on_submit():
         # Save the response
        response = Response(
            user_id=current_user.id,
            question_id=question.id,
            answer=form.answer.data
        )
        db.session.add(response)

        # Add per-question payout to user's balance
        current_user.balance += survey.per_question_payout
        progress.payout += survey.per_question_payout

        # Update progress
        progress.current_question_index += 1

        db.session.commit()

        # Redirect to the same route to load the next question
        return redirect(url_for('take_survey', survey_id=survey.id))
    else:
        if request.method == 'POST':
            flash('Please correct the errors below.', 'danger')

    return render_template('take_survey.html', form=form, question=question, survey=survey, progress=progress,
                               total_questions=total_questions)

@app.route('/export_responses/<int:survey_id>')
@login_required
def export_responses(survey_id):
    survey = Survey.query.get_or_404(survey_id)

    # Check if the current user is the owner of the survey
    if survey.owner_id != current_user.id:
        flash('You do not have permission to access this survey.', 'danger')
        return redirect(url_for('dashboard'))

    # Retrieve all questions and their responses
    questions = survey.questions.order_by(Question.order).all()

    # Prepare the CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write the header row
    header = ['Respondent ID']
    header.extend([f'Q{question.order + 1}: {question.question_text}' for question in questions])
    writer.writerow(header)

    # Get all respondent IDs who have completed the survey
    respondent_ids = db.session.query(Response.user_id).join(Question).filter(
        Question.survey_id == survey.id
    ).distinct().all()
    respondent_ids = [r[0] for r in respondent_ids]

    # For each respondent, collect their answers
    for respondent_id in respondent_ids:
        row = [respondent_id]
        for question in questions:
            response = Response.query.filter_by(
                question_id=question.id,
                user_id=respondent_id
            ).first()
            answer = response.answer if response else ''
            row.append(answer)
        writer.writerow(row)

    # Prepare the file for download
    output.seek(0)
    filename = f'survey_{survey.id}_responses.csv'

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename  # This parameter is outdated in Flask 2.0+
    )



def send_payout_email(username, bank_account, amount):
    msg = Message('Payout Request',
                  sender='support@surveyhustle.tech',
                  recipients=['support@surveyhustle.tech'])
    msg.body = f'User {username} has requested a payout.\n' \
               f'Bank Account: {bank_account}\n' \
               f'Amount: ${amount:.2f}'
    mail.send(msg)

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    form = PayoutForm()
    if form.validate_on_submit():
        amount = form.amount.data
        bank_account = form.nz_bank_account.data
        if current_user.balance < amount:
            flash('Insufficient balance.', 'danger')
            return redirect(url_for('payment'))
        # Send email to support
        send_payout_email(current_user.username, bank_account, amount)
        # Deduct amount from user's balance
        current_user.balance -= amount
        db.session.commit()
        flash('Your payout request has been submitted.', 'success')
        return redirect(url_for('profile'))
    return render_template('payment.html', form=form)