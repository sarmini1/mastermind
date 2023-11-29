import os

from dotenv import load_dotenv
from flask import Flask, request, render_template, session, redirect, flash, g
from sqlalchemy.exc import IntegrityError

from db import db, connect_db
from mastermind import MastermindGame
from forms import CSRFForm

# Flask loads our environmental variables for us when we start the app, but
# it's a good idea to load them explicitly in case we run this file without
# Flask.
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///mastermind')
CURR_GAME_KEY = "curr_game"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)


@app.before_request
def add_curr_game_to_g():
    """If a game has been started, put the instance onto g before each request."""

    if CURR_GAME_KEY in session:
        game_id = session[CURR_GAME_KEY]
        g.curr_game = MastermindGame.query.get_or_404(game_id)


@app.before_request
def add_csrf_form_to_g():
    """Add a blank CSRF form for that protection before each request."""

    g.csrf_form = CSRFForm()


@app.get("/")
def homepage():
    """
    On GET, render a template that includes a button to start a new game.
    """

    return render_template("home.html")


@app.post("/new-game")
def start_new_game():
    """
    On POST, start a new instance of MastermindGame and redirect to gameplay template.
    """

    if g.csrf_form.validate_on_submit():

        num_count = int(request.form["num-count"])
        try:
            new_game = MastermindGame.generate_new_game(num_count=num_count)
            db.session.commit()
            session[CURR_GAME_KEY] = new_game.id
            flash("New game started!")
        except IntegrityError:
            # Rollback a fouled transaction if an error occurs while committing
            # to the database
            db.session.rollback()

        return redirect("/play")
    else:
        flash("You didn't come from the right place and we're onto you!")
        return redirect("/")


@app.get("/play")
def play_game():
    """
    On GET, renders a template for the user to input their guess for the current
    game.

    If no current game exists, redirects home.
    """

    if CURR_GAME_KEY not in g:
        return redirect("/")

    if g.curr_game.has_won:
        return redirect("/win")

    if g.curr_game.game_over:
        return redirect("/loss")

    return render_template("gameplay.html")


@app.post("/submit-guess")
def submit_guess():
    """
    On POST, extract form data and score incoming guess for the current game.
    If the game is over, redirect to appropriate win/loss route.
    If the game is still going, redirect to the gameplay route.

    If no current game exists, redirects home.
    """

    if CURR_GAME_KEY not in g:
        return redirect("/")

    if not g.csrf_form.validate_on_submit():
        flash("You didn't come from the right place and we're onto you!")
        return redirect("/")

    guessed_nums = []

    # There could be either 4, 6, or 8 inputs to collect, so better to do it
    # dynamically
    for i in range(g.curr_game.num_count):
        try:
            num = int(request.form[f"num-{i}"])
            g.curr_game.validate_num(num)
            guessed_nums.append(num)
        except ValueError:
            flash(
                f"Integers must be between {g.curr_game.lower_bound} and {g.curr_game.upper_bound}."
            )
            return redirect("/play")

    try:
        # The below method call will add a new Guess instance to the db session
        g.curr_game.handle_guess(guessed_nums)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    if g.curr_game.has_won:
        return redirect("/win")

    if g.curr_game.game_over:
        return redirect("/loss")

    return redirect("/play")


@app.get("/win")
def display_win():
    """
    On GET, render a template with a win message and a button to start a new game.

    If no current game exists, redirects home.
    """

    if CURR_GAME_KEY not in g:
        return redirect("/")

    if not g.curr_game.has_won and not g.curr_game.game_over:
        return redirect("/play")

    if not g.curr_game.has_won and g.curr_game.game_over:
        return redirect("/loss")

    return render_template("win.html")


@app.get("/loss")
def display_loss():
    """
    On GET, render a template with a loss message and a button to start a new game.

    If no current game exists, redirects home.
    """

    if CURR_GAME_KEY not in g:
        return redirect("/")

    if not g.curr_game.has_won and not g.curr_game.game_over:
        return redirect("/play")

    if g.curr_game.has_won:
        return redirect("/win")

    return render_template("loss.html")


@app.post("/restart")
def restart():
    """On POST, delete CURR_GAME_KEY from session and redirect home."""

    if g.csrf_form.validate_on_submit():
        session.pop(CURR_GAME_KEY)

    return redirect("/")
