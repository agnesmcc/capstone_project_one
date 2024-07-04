import os
from functools import wraps

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, UserEditForm, ListAddForm
from models import db, connect_db, User, Recipe, List, ListsRecipes, UsersFavoritesRecipes

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///tender'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

def authorize_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
def homepage():
    """Show homepage with links to recipes and lists."""

    if not g.user:
        return redirect('/signup')
    
    recipes = Recipe.query.all()
    lists = List.query.all()

    return render_template('home.html', recipes=recipes, lists=lists, user=g.user)

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

            default_list = List(
                title="My List",
                description="My first list",
                username=user.username
            )

            db.session.add(default_list)
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("Logged out successfully.", "success")
    return redirect("/")

@app.route('/favorites')
@authorize_user
def show_favorites():
    """Show all favorites."""

    favorites = g.user.favorites
    lists = List.query.all()
    return render_template('favorites/favorites.html', recipes=favorites, user=g.user, lists=lists)

@app.route('/favorites/add', methods=["POST"])
@authorize_user
def add_favorite():
    """Add favorite."""

    recipe_id = request.json['recipeId']
    recipe = Recipe.query.get(recipe_id)
    g.user.favorites.append(recipe)
    db.session.commit()
    return redirect("/favorites")

@app.route('/favorites/remove', methods=["POST"])
@authorize_user
def remove_favorite():
    """Remove favorite."""

    recipe_id = request.json['recipeId']
    recipe = Recipe.query.get(recipe_id)
    g.user.favorites.remove(recipe)
    db.session.commit()
    return redirect("/favorites")

@app.route('/lists')
@authorize_user
def show_lists():
    """Show all lists."""

    lists = List.query.all()
    return render_template('lists/lists.html', lists=lists)

@app.route('/lists/<int:list_id>')
@authorize_user
def show_list(list_id):
    """Show list details."""

    lists = List.query.all()
    list = List.query.get_or_404(list_id)

    if list.username != g.user.username:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    recipes = list.recipes

    return render_template('lists/list.html', list=list, lists=lists, recipes=recipes, user=g.user)

@app.route('/lists/new', methods=["GET", "POST"])
@authorize_user
def new_list():
    """Show form to add list and process form."""

    lists = List.query.all()

    form = ListAddForm()

    if form.validate_on_submit():
        list = List(
            username=g.user.username,
            title=form.title.data, 
            description=form.description.data
        )
        db.session.add(list)
        db.session.commit()
        return redirect(f"/lists")

    else:
        return render_template('lists/new_list.html', form=form, lists=lists)


@app.route('/lists/delete/<int:list_id>')
@authorize_user
def delete_list(list_id):
    """Delete list."""

    list = List.query.get_or_404(list_id)

    if list.username != g.user.username:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(list)
    db.session.commit()

    return redirect("/lists")

@app.route('/lists/add', methods=["POST"])
@authorize_user
def add_recipe_to_list():

    list_title = request.json["listTitle"]
    recipe_id = request.json["recipeId"]

    list = List.query.filter_by(title=list_title).first_or_404()

    if list.username != g.user.username:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    list_recipes = ListsRecipes(
        list_id=list.id,
        recipe_id=recipe_id
    )

    db.session.add(list_recipes)
    db.session.commit()

    return jsonify({'message': 'success'})


@app.route('/lists/delete_recipe/<int:list_id>/<int:recipe_id>')
@authorize_user
def delete_recipe_from_list(list_id, recipe_id):
    """Delete recipe from list."""

    list = List.query.get_or_404(list_id)

    if list.username != g.user.username:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    list_recipe = ListsRecipes.query.filter_by(list_id=list_id, recipe_id=recipe_id).first_or_404()

    db.session.delete(list_recipe)
    db.session.commit()

    return redirect(f"/lists/{list_id}")

@app.route('/my-account', methods=["GET", "POST"])
@authorize_user
def my_account():
    """Show user account page."""

    lists = List.query.all()

    form = UserEditForm(obj=g.user)

    if form.validate_on_submit():
        user = User.authenticate(g.user.username,
                                 form.password.data)

        if user:
            g.user.username = form.username.data
            g.user.email = form.email.data
            db.session.commit()
            flash("Account updated.", "success")
            return redirect("/my-account")

        flash("Invalid credentials.", 'danger')

    return render_template('users/my_account.html', user=g.user, form=form, lists=lists)

@app.route('/my-account/delete')
@authorize_user
def delete_user():
    """Delete user."""

    db.session.delete(g.user)
    db.session.commit()

    do_logout()
    return redirect("/signup")