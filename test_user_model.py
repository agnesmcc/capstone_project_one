"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, List, Recipe, ListsRecipes, UsersFavoritesRecipes
from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///tender-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    
    def tearDown(self):
        """Clean up after each test."""
        try:
            db.session.rollback()
        except InvalidRequestError:
            pass
        finally:
            db.session.close()

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()


        self.client = app.test_client()

        self.testuser = User.signup(first_name="Test",
                                    last_name="User",
                                    username="testuser",
                                    email="test@test",
                                    password="testuser")

        self.testuser2 = User.signup(first_name="Test",
                                     last_name="User",
                                     username="testuser2",
                                     email="test2@test",
                                     password="testuser2")
        
        db.session.add_all([self.testuser, self.testuser2])
        db.session.commit()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            first_name="Test",
            last_name="User",
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()


    def test_repr(self):
        """Does the repr method work?"""

        self.assertEqual(repr(self.testuser), 
            f"<User #{self.testuser.id}: {self.testuser.username}, {self.testuser.email}>")
        self.assertEqual(repr(self.testuser2), 
            f"<User #{self.testuser2.id}: {self.testuser2.username}, {self.testuser2.email}>")


    def test_failed_creation(self):
        """Does user creation fail with bad data?"""

        first_user = User(
            first_name="Test",
            last_name="User",
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )

        db.session.add(first_user)
        db.session.commit()

        # test that a duplicate user cannot be created
        duplicate_user = User(
            first_name="Test",
            last_name="User",
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )

        with self.assertRaises(IntegrityError):
            db.session.add(duplicate_user)
            db.session.commit()

        db.session.rollback()    
    
        # test that a user cannot be created with a null password
        with self.assertRaises(IntegrityError):
            db.session.add(User(
                first_name="Test",
                last_name="User",
                email="test4@test.com",
                username="testuser4",
                password=None
            ))
            db.session.commit()

    def test_user_authenticate_success(self):
        """Does user authentication work?"""
        user = User.authenticate(self.testuser.username, "testuser")
        self.assertEqual(user, self.testuser)

    def test_user_authenticate_fail_invalid_username(self):
        """Does user authentication fail with invalid username?"""
        user = User.authenticate("testuser3", "testuser")
        self.assertFalse(user)
    
    def test_user_authenticate_fail_invalid_password(self):
        """Does user authentication fail with invalid password?"""
        user = User.authenticate(self.testuser.username, "testuser3")
        self.assertFalse(user)
