"""List model tests."""

# run these tests like:
#
#    python -m unittest test_list_model.py


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

with app.app_context():
    db.create_all()


class ListModelTestCase(TestCase):
    """Test List model."""
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            db.session.rollback()
        except InvalidRequestError:
            pass
        finally:
            db.session.close()
            self.app.pop()

    def setUp(self):
        """Create test client, add sample data."""

        self.app = app.app_context()
        self.app.push()

        User.query.delete()
        List.query.delete()
        Recipe.query.delete()

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
        
        self.recipe = Recipe(
            source_id="12345",
            title="Test Recipe",
            image_url="https://example.com/image.jpg"
        )

        
        db.session.add_all([self.testuser, self.testuser2, self.recipe])
        db.session.commit()

    def test_list_model(self):
        """Does basic model work?"""
        
        l = List(
            title="Test List",
            description="Test Description",
            username="testuser"
        )

        db.session.add(l)
        db.session.commit()

        self.assertEqual(l.title, "Test List")
        self.assertEqual(l.username, self.testuser.username)
        self.assertEqual(len(self.testuser.lists), 1)


    def test_add_recipe_to_list(self):
        """Can user add recipe to list?"""

        l = List(
            title="Test List",
            description="Test Description",
            username="testuser"
        )

        db.session.add(l)
        db.session.commit()

        self.assertEqual(len(l.recipes), 0)

        l.recipes.append(self.recipe)

        self.assertEqual(len(l.recipes), 1)

    def test_list_repr_method(self):
        """Does list repr method work?"""

        l = List(
            title="Test List",
            description="Test Description",
            username="testuser"
        )

        db.session.add(l)
        db.session.commit()

        self.assertEqual(repr(l), 
            f"<List #{l.id}: {l.title}, {l.username}>")
