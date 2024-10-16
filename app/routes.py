#routes.py
from flask_wtf import FlaskForm
from decimal import Decimal, ROUND_HALF_UP

import os
import io
import csv

from flask import render_template, redirect, url_for, flash, request, send_file, session

from app import app, db
from app.models import User, Survey, Question, Response, UserSurveyProgress


from app.forms import RegistrationForm, LoginForm, UploadSurveyForm, AddBalanceForm, AcceptTermsForm, PayoutForm, DeleteAccountForm, DataRequestForm
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


import random
import numpy as np
from app.models import Question

import random
import numpy as np
from app.models import Question

import random
import numpy as np
from app.models import Question


def apply_ldp(response, privacy_level, question_id):
    question = Question.query.get(question_id)
    if question is None:
        print(f"Error: Question with id {question_id} not found")
        return response

    question_type = question.question_type

    if question_type in ['rating', 'number']:
        try:
            response = float(response)
            if privacy_level == 'high':
                return max(min(response + np.random.laplace(0, 1.5), 10),
                           0)  # Increased noise, clamped between 0 and 10
            elif privacy_level == 'medium':
                return max(min(response + np.random.laplace(0, 1), 10), 0)
            else:
                return max(min(response + np.random.laplace(0, 0.5), 10), 0)
        except ValueError:
            print(f"Error: Could not convert response '{response}' to float for question {question_id}")
            return response
    elif question_type == 'multiple_choice':
        choices = question.choices.split(',') if question.choices else []
        if not choices:
            print(f"Error: No choices found for multiple choice question {question_id}")
            return response

        if privacy_level == 'high':
            return random.choice(choices) if random.random() < 0.3 else response  # 30% chance to randomise
        elif privacy_level == 'medium':
            return random.choice(choices) if random.random() < 0.2 else response  # 20% chance to randomise
        else:
            return random.choice(choices) if random.random() < 0.1 else response  # 10% chance to randomise
    else:
        # For text data, no randomization
        return response
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

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')
@app.route('/explore')
def explore():
    privacy_level = request.args.get('privacy_level', 'All').lower()  # Convert to lowercase to match DB

    if privacy_level == 'all':
        surveys = Survey.query.filter_by(active=True).all()
    else:
        surveys = Survey.query.filter_by(active=True, privacy_level=privacy_level).all()

    return render_template('explore.html', surveys=surveys, selected_privacy_level=privacy_level)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = AddBalanceForm()

    return render_template('profile.html', user=current_user, form=form)

@app.route('/survey')
#@login_required
def survey():
    return render_template('survey.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = DataRequestForm()
    delete_form = DeleteAccountForm()
    return render_template('settings.html', delete_form=delete_form, form=form)


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
        total_payout = Decimal(str(form.total_payout.data)).quantize(Decimal('0.01'))
        # Deduct the total payout from the business user's balance
        current_user.balance -= form.total_payout.data

        # Create the survey
        survey = Survey(
            title=form.title.data,
            description=form.description.data,
            privacy_level=form.privacy_level.data,
            terms_and_conditions=form.terms_and_conditions.data,
            total_payout=total_payout,
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
        # Calculate per-question payout
        total_questions = survey.questions.count()
        desired_respondents = survey.desired_respondents

        # Ensure total_questions and desired_respondents are not zero to avoid division by zero
        if total_questions == 0 or desired_respondents == 0:
            flash('Survey must have at least one question and one desired respondent.', 'danger')
            return redirect(url_for('profile'))

        per_question_payout = (survey.total_payout / (desired_respondents * total_questions)).quantize(
            Decimal('0.0001'))
        survey.per_question_payout = per_question_payout
        db.session.commit()

        flash('Survey uploaded successfully!', 'success')
        return redirect(url_for('profile'))
    else:
        if request.method == 'POST':
            flash('Please correct the errors below.', 'danger')
    return render_template('upload_survey.html', form=form)
import re
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
        survey_description = re.sub(r'\r', '<br>', survey.description)
        survey_terms = re.sub(r'\r', '<br>', survey.terms_and_conditions)
        if request.method == 'POST':
            if 'accept' in request.form:
                progress = UserSurveyProgress(user_id=current_user.id, survey_id=survey.id)
                db.session.add(progress)
                db.session.commit()
                return redirect(url_for('take_survey', survey_id=survey.id))
            else:
                flash('You must accept the terms to proceed.', 'danger')
                return redirect(url_for('explore'))
        return render_template('survey_terms.html', survey=survey, form=form, description=survey_description, terms=survey_terms)






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
    elif question.question_type == 'number':
        setattr(DynamicSurveyForm, 'answer', IntegerField(
            question.question_text,
            validators=[DataRequired()]
        ))
    else:
        flash('Unknown question type.', 'danger')
        return redirect(url_for('profile'))

    form = DynamicSurveyForm()

    # Handle form submission
    if form.validate_on_submit():
        privacy_level = survey.privacy_level
        original_response = form.answer.data
        randomized_response = apply_ldp(original_response, privacy_level, question.id)

        # Convert randomized_response to string for storage
        if isinstance(randomized_response, (int, float)):
            randomized_response = f"{randomized_response:.2f}"
        else:
            randomized_response = str(randomized_response)

        # Save the response
        response = Response(
            user_id=current_user.id,
            question_id=question.id,
            answer=randomized_response
        )
        db.session.add(response)

        # Add per-question payout to user's balance
        current_user.balance += survey.per_question_payout
        current_user.balance = current_user.balance.quantize(Decimal('0.01'))

        progress.payout += survey.per_question_payout
        progress.payout = progress.payout.quantize(Decimal('0.01'))

        # Update progress
        progress.current_question_index += 1

        db.session.add(progress)
        db.session.add(current_user)

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
    from app import mail, EMAIL
    msg = Message('Payout Request',
                  sender=EMAIL,
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
        amount = Decimal(str(form.amount.data)).quantize(Decimal('0.01'))
        bank_account = form.nz_bank_account.data

        if current_user.balance < amount:
            flash('Insufficient balance.', 'danger')
            return redirect(url_for('payment'))

        # Send email to support
        send_payout_email(current_user.username, bank_account, amount)

        # Deduct amount from user's balance
        current_user.balance -= amount
        current_user.balance = current_user.balance.quantize(Decimal('0.01'))
        db.session.commit()
        flash('Your payout request has been submitted.', 'success')
        return redirect(url_for('profile'))
    return render_template('payment.html', form=form, user=current_user)





# STRIPE
import stripe

stripe.api_key = app.config['STRIPE_SECRET_KEY']
@app.route('/add_balance', methods=['GET', 'POST'])
@login_required
def add_balance():
    if not current_user.is_business:
        flash('You must be a business user to add balance.', 'danger')
        return redirect(url_for('profile'))

    form = AddBalanceForm()
    if form.validate_on_submit():
        amount = None
        if form.custom_amount.data:
            amount = Decimal(str(form.custom_amount.data))
        elif form.amount.data:
            amount = Decimal(str(form.amount.data))
        else:
            amount = None

        if amount is None or amount <= Decimal('0.00'):
            flash('Please select a valid amount.', 'danger')
            return redirect(url_for('add_balance'))

        # Quantize the amount to 2 decimal places
        amount = amount.quantize(Decimal('0.01'))

        # Save the amount to session to use it after payment
        session['top_up_amount'] = str(amount)

        # Redirect to create checkout session
        return redirect(url_for('create_checkout_session'))
    else:
        print("Form validation failed")
        print(form.errors)
        print("Request form data:", request.form)
    return render_template('add_balance.html', form=form)



@app.route('/create-checkout-session', methods=['GET'])
@login_required
def create_checkout_session():
    amount_str = session.get('top_up_amount')
    if not amount_str:
        flash('No amount specified for top-up.', 'danger')
        return redirect(url_for('add_balance'))

    # Convert amount to Decimal
    amount = Decimal(amount_str)

    # Convert amount to cents (Stripe expects amounts in the smallest currency unit)
    amount_cents = int((amount * 100).quantize(Decimal('1')))

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'nzd',
                    'unit_amount': amount_cents,
                    'product_data': {
                        'name': 'Account Balance Top-up',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment_cancel', _external=True),
            customer_email=current_user.email,
            metadata={
                'user_id': current_user.id,
                'top_up_amount': amount
            }
        )
        return redirect(checkout_session.url)
    except Exception as e:
        flash(f'An error occurred while creating the checkout session: {str(e)}', 'danger')
        return redirect(url_for('add_balance'))

@ app.route('/success')
@ login_required
def payment_success():
    session_id = request.args.get('session_id')
    if not session_id:
        flash('No session ID provided.', 'danger')
        return redirect(url_for('profile'))

    try:
        # Retrieve the session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        amount = checkout_session['metadata']['top_up_amount']
        user_id = checkout_session['metadata']['user_id']
    except Exception as e:
        flash(f'Error retrieving payment information: {str(e)}', 'danger')
        return redirect(url_for('profile'))

    # Verify that the user ID matches the current user
    if str(current_user.id) != user_id:
        flash('User ID mismatch.', 'danger')
        return redirect(url_for('profile'))
    # Convert amount to Decimal
    amount_decimal = Decimal(amount)

    # Add the amount to the user's balance
    current_user.balance += amount_decimal
    current_user.balance = current_user.balance.quantize(Decimal('0.01'))
    db.session.commit()
    flash(f'Added ${amount_decimal} to your balance.', 'success')
    return redirect(url_for('profile'))
@app.route('/cancel')
@login_required
def payment_cancel():
    flash('Payment canceled.', 'info')
    return redirect(url_for('profile'))

# routes.py
@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        user = current_user
        password = form.password.data

        # Verify the password
        if not check_password_hash(user.password, password):
            flash('Incorrect password. Please try again.', 'danger')
            return redirect(url_for('settings'))

        # Delete user's responses
        Response.query.filter_by(user_id=user.id).delete()

        # Delete user's survey progress
        UserSurveyProgress.query.filter_by(user_id=user.id).delete()

        # Delete user's surveys and associated data
        surveys = Survey.query.filter_by(owner_id=user.id).all()
        for survey in surveys:
            # Delete responses to survey questions
            question_ids = [q.id for q in survey.questions]
            Response.query.filter(Response.question_id.in_(question_ids)).delete()
            # Delete survey questions
            Question.query.filter_by(survey_id=survey.id).delete()
            # Delete the survey
            db.session.delete(survey)

        # Delete the user
        db.session.delete(user)
        db.session.commit()

        # Log out the user
        logout_user()

        flash('Your account has been deleted.', 'success')
        return redirect(url_for('index'))
    else:
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('settings'))
@app.route('/request_data', methods=['GET', 'POST'])
@login_required
def request_data():
    form = DataRequestForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        if user:
            data_type = request.form.get('data_type', 'basic')
            if data_type == 'all':
                all = True
            else:
                all = False
            user_data = user.get_all_data(all)

            # Convert the user data to a readable format (e.g., JSON or plain text)
            user_data_str = f"User Data:\n{str(user_data)}\n\n"

            # Email logic
            msg = Message("Your Data Request",
                          sender="admin@yourdomain.com",
                          recipients=[user.email])
            msg.body = f"Here is the data we have for you:\n\n{user_data_str}"
            mail.send(msg)

            flash("An email with your data has been sent.", "success")
            return redirect(url_for('settings'))  # Redirect to settings or another page
    return render_template('request_data.html', form=form)