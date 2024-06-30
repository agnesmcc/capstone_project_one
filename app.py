import os

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

@app.route('/')
def homepage():
    """Show homepage with links to recipes and lists."""

    if not g.user:
        return redirect('/signup')
    
    recipes = Recipe.query.all()
    lists = List.query.all()

    return render_template('home.html', recipes=recipes, lists=lists)

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

@app.route('/lists')
def show_lists():
    """Show all lists."""

    lists = List.query.all()
    return render_template('lists/lists.html', lists=lists)

@app.route('/lists/<int:list_id>')
def show_list(list_id):
    """Show list details."""

    lists = List.query.all()
    list = List.query.get_or_404(list_id)

    if list.username != g.user.username:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    recipes = list.recipes

    return render_template('lists/list.html', list=list, lists=lists, recipes=recipes)

@app.route('/lists/new', methods=["GET", "POST"])
def new_list():
    """Show form to add list and process form."""

    if not g.user:
        return redirect('/signup')

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
def delete_list(list_id):
    """Delete list."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    list = List.query.get_or_404(list_id)

    if list.username != g.user.username:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(list)
    db.session.commit()

    return redirect("/lists")

@app.route('/lists/add', methods=["POST"])
def add_recipe_to_list():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

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
