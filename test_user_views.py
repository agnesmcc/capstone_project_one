"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, User, List, Recipe, ListsRecipes, UsersFavoritesRecipes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///tender-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

with app.app_context():
    db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        self.app = app.app_context()
        self.app.push()
        
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

    def test_user_signup(self):
        """Can user sign up?"""
        with self.client as c:
            resp = c.post("/signup", data={"first_name": "Test",
                                            "last_name": "User",
                                            "username": "testuser3",
                                            "password": "testuser3",
                                            "email": "test3@test.com"})
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(User.query.count(), 3)

    def test_user_delete(self):
        """Can user delete themselves?"""

        testuser1_id = self.testuser.id

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/my-account/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(User.query.get(testuser1_id), None)
            
    def test_user_edit_profile(self):
        """Can user edit their profile?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/my-account")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"testuser", resp.data)

            resp = c.post(f"/my-account", 
                data={"username": "testuser3",
                     "password": "testuser", # This is the user's password not a new one
                     "email": "test3@test.com",
                     "image_url": None}, 
                follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(User.query.count(), 2)
            self.assertIn(b"testuser3", resp.data)
