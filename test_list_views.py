"""List View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_list_views.py


import os, json
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

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class ListViewTestCase(TestCase):
    """Test views for lists."""

    def setUp(self):
        """Create test client, add sample data."""

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

        self.list = List(
            title="Test List",
            description="Test description",
            username="testuser"
        )

        self.recipe = Recipe(
            source_id="12345",
            title="Test Recipe",
            image_url="https://example.com/image.jpg"
        )

        db.session.add_all([self.testuser, self.testuser2, self.list, self.recipe])
        db.session.commit()

    def test_show_lists(self):
        """Can we show lists?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/lists")
            self.assertEqual(resp.status_code, 200)

            self.assertIn(b"Test List", resp.data)


    def test_show_list(self):
        """Can we show list details?"""

        list_id = self.list.id

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/lists/{list_id}")
            self.assertEqual(resp.status_code, 200)

            self.assertIn(b"Test List", resp.data)

    def test_create_new_list(self):
        """Can we create new list?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/lists/new", data={
                "title": "Test List 2",
                "description": "Test description"
            }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Test List", resp.data)

    def test_add_recipe_to_list(self):
        """Can we add recipe to list?"""

        list_title = self.list.title
        recipe_id = self.recipe.id

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/lists/add", json={
                "listTitle": list_title, 
                "recipeId": recipe_id}, follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertEqual({'message': 'success'}, json.loads(resp.data))


    def test_delete_list(self):
        """Can we delete list?"""

        list_id = self.list.id

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/lists/delete/{list_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(List.query.get(list_id), None)

    def test_remove_recipe_from_list(self):
        """Can we remove recipe from list?"""

        self.list.recipes.append(self.recipe)
        db.session.commit()

        self.assertEqual(len(self.list.recipes), 1)

        list_id = self.list.id
        list_title = self.list.title
        recipe_id = self.recipe.id

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/lists/delete_recipe/{list_id}/{recipe_id}", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(b'{list_title}', resp.data)
            self.assertEqual(len(List.query.get(list_id).recipes), 0)
