from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from whitenoise import WhiteNoise
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login = LoginManager()
mail = Mail()

from csrf import csrf

load_dotenv()


def create_app(config_name):
    # Create the Flask app
    app = Flask(__name__)

    # Load the configuration from the config class
    app.config.from_object(f'config.{config_name.capitalize()}Config')

    # Initialize extensions
    db.init_app(app)
    login.init_app(app)
    login.login_view = 'login'

    csrf.init_app(app)

    # Initialize email
    mail.init_app(app)

    # Use WhiteNoise to serve static files in production
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

    # Register the custom Jinja2 filter
    import re
    from markupsafe import Markup

    def nl2br(value):
        """Convert newlines to <br> tags."""
        value = re.sub(r'\r\n|\r|\n', '<br>', value)
        return Markup(value)

    app.jinja_env.filters['nl2br'] = nl2br

    # Import routes and models
    from app import routes, models

    return app
