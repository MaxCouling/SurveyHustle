# __init__.py
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from csrf import csrf
from flask_mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
csrf.init_app(app)

EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
# Configure email
app.config['MAIL_SERVER'] = 'smtp.zoho.com.au'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'support@surveyhustle.tech'  # Replace with your email
app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD     # Replace with your email password
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')

mail = Mail(app)
from app import models, routes
