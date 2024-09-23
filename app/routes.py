from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.models import User
from app.forms import RegistrationForm, LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

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
#@login_required
def explore():
    return render_template('explore.html')

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


