# __init__.py
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from csrf import csrf
from flask_mail import Mail
from dotenv import load_dotenv
import os
from whitenoise import WhiteNoise

load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
csrf.init_app(app)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL = os.environ.get("EMAIL")
# Configure email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = EMAIL # Replace with your email
app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD     # Replace with your email password
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')

import re
from markupsafe import Markup

def nl2br(value):
    """Convert newlines to <br> tags."""
    value = re.sub(r'\r\n|\r|\n', '<br>', value)
    return Markup(value)

# Register the filter with Jinja2
app.jinja_env.filters['nl2br'] = nl2br

mail = Mail(app)
from sqlalchemy import Numeric
from app import models, routes
