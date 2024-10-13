from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField, FileField, IntegerField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional, NumberRange
from app.models import User
import re


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    is_business = BooleanField('Register as a Business User')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('An account with this email already exists.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

# forms.py

class UploadSurveyForm(FlaskForm):
    title = StringField('Survey Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    privacy_level = SelectField('Privacy Level', choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], validators=[DataRequired()])
    terms_and_conditions = TextAreaField('Terms and Conditions', validators=[DataRequired()])
    total_payout = DecimalField('Total Payout', validators=[DataRequired()])
    desired_respondents = IntegerField('Number of Respondents', validators=[DataRequired()])
    csv_file = FileField('Survey Questions CSV', validators=[DataRequired()])
    submit = SubmitField('Upload Survey')


# forms.py

class AddBalanceForm(FlaskForm):
    amount = RadioField('Select Amount', choices=[('10', '$10'), ('100', '$100'), ('1000', '$1000')], validators=[Optional()])
    custom_amount = DecimalField('Custom Amount (optional)', validators=[Optional(), NumberRange(min=0.01)])
    submit = SubmitField('Add Balance')


# forms.py

class PayoutForm(FlaskForm):
    nz_bank_account = StringField('NZ Bank Account', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired()])
    submit = SubmitField('Cash Out')

    def validate_nz_bank_account(form, field):
        pattern = r'^\d{2}-\d{4}-\d{7}-\d{2,3}$'
        if not re.match(pattern, field.data):
            raise ValidationError(
                'Invalid NZ bank account number format. Please enter in the format BB-bbbb-AAAAAAA-SSS.')

class AcceptTermsForm(FlaskForm):
    pass

class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])

class DataRequestForm(FlaskForm):
    request_data = SubmitField('Request My Data')
