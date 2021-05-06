import os
from unittest import TestCase

from datetime import date
 
from books_app import app, db, bcrypt
from books_app.models import Book, Author, User, Audience

"""
Run these tests with the command:
python -m unittest books_app.main.tests
"""

#################################################
# Setup
#################################################

def create_books():
    a1 = Author(name='Harper Lee')
    b1 = Book(
        title='To Kill a Mockingbird',
        publish_date=date(1960, 7, 11),
        author=a1
    )
    db.session.add(b1)

    a2 = Author(name='Sylvia Plath')
    b2 = Book(title='The Bell Jar', author=a2)
    db.session.add(b2)
    db.session.commit()

def create_user():
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        # - Make a POST request to /signup, sending a username & password
        passHash = bcrypt.generate_password_hash('Password').decode('utf-8')
        post_data = {
            'username': 'Bobert',
            'password': passHash,
        }
        self.app.post('/signup', data=post_data)
        # - Check that the user now exists in the database
        testUser = User.query.filter_by(username="Bobert").one()
        self.assertIsNotNone(testUser)

    def test_signup_existing_user(self):
        # - Create a user
        create_user()
        # - Make a POST request to /signup, sending the same username & password
        passHash = bcrypt.generate_password_hash('password').decode('utf-8')
        post_data = {
            'username': 'me1',
            'password': passHash,
        }
        response = self.app.post('/signup', data=post_data)
        # - Check that the form is displayed again with an error message
        responseText = response.get_data(as_text=True)
        self.assertIn("taken", responseText)

    def test_login_correct_password(self):
        # - Create a user
        create_user()
        # - Make a POST request to /login, sending the created username & password
        post_data = {
            'username': 'me1',
            'password': "password",
        }
        self.app.post('/login', data=post_data)
        # - Check that the "login" button is not displayed on the homepage
        response = self.app.get('/', follow_redirects=True)
        responseText = response.get_data(as_text=True)
        self.assertNotIn('Login', responseText)

    def test_login_nonexistent_user(self):
        # - Make a POST request to /login, sending a username & password
        post_data = {
            'username': 'banana',
            'password': "password",
        }
        response = self.app.post('/login', data=post_data)
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        responseText = response.get_data(as_text=True)
        self.assertIn('No user with', responseText)

    def test_login_incorrect_password(self):
        # - Create a user
        create_user()
        # - Make a POST request to /login, sending the created username &
        #   an incorrect password
        post_data = {
            'username': 'me1',
            'password': "bananas?",
        }
        response = self.app.post('/login', data=post_data)
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        responseText = response.get_data(as_text=True)
        self.assertIn('Please try again', responseText)

    def test_logout(self):
        # - Create a user
        create_user()
        # - Log the user in (make a POST request to /login)
        post_data = {
            'username': 'me1',
            'password': "password",
        }
        self.app.post('/login', data=post_data)
        # - Make a GET request to /logout
        self.app.get('/logout')
        # - Check that the "login" button appears on the homepage
        response = self.app.get('/', follow_redirects=True)
        responseText = response.get_data(as_text=True)
        self.assertIn('Log In', responseText)
