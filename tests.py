import pytest
from flask import url_for
from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash

@pytest.fixture
def test_client():
    # Set up Flask testing app
    flask_app = create_app('testing')  # Use a testing configuration
    testing_client = flask_app.test_client()

    # Establish application context
    ctx = flask_app.app_context()
    ctx.push()

    # Set up the database
    db.create_all()

    yield testing_client  # Testing happens here

    # Tear down
    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture
def new_user():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'is_business': True
    }

def test_register(test_client, new_user):
    """Test user registration"""

    # Simulate a POST request to register a user
    response = test_client.post(
        '/register',
        data=new_user,
        follow_redirects=True
    )
    assert response.status_code == 200  # Ensure the request was successful
    assert b'Registration successful! Please log in.' in response.data

    # Check if the user was added to the database
    user = User.query.filter_by(username=new_user['username']).first()
    assert user is not None
    assert user.email == new_user['email']
    assert user.is_business is True  # Ensure business user flag is correct
    assert check_password_hash(user.password, new_user['password'])  # Check password

def test_login(test_client, new_user):
    """Test user login"""

    # First, register the user
    test_register(test_client, new_user)

    # Simulate a POST request to log in
    response = test_client.post(
        '/login',
        data={
            'username': new_user['username'],
            'password': new_user['password']
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Logged in successfully.' in response.data

def test_logout(test_client, new_user):
    """Test user logout"""

    # First, log in the user
    test_login(test_client, new_user)

    # Simulate a GET request to log out
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Should redirect to the login page
