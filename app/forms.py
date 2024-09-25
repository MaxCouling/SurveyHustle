from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField, FileField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

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
    terms_and_conditions = TextAreaField('Terms and Conditions', validators=[DataRequired()])
    total_payout = FloatField('Total Payout', validators=[DataRequired()])
    desired_respondents = IntegerField('Number of Respondents', validators=[DataRequired()])
    csv_file = FileField('Survey Questions CSV', validators=[DataRequired()])
    submit = SubmitField('Upload Survey')


class AddBalanceForm(FlaskForm):
    submit = SubmitField('Add $20')