import os

from flask import Flask, request, render_template, session, redirect, flash, g
from uuid import uuid4

from mastermind import Mastermind

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

CURR_GAME_KEY = "curr_game"

# TODO: store games in a DB instead
games = {}


@app.before_request
def add_curr_game_to_g():
    """If a game has been started, put into onto g before each request."""

    if CURR_GAME_KEY in session:
        g.curr_game = games[session[CURR_GAME_KEY]]


@app.get("/")
def homepage():
    """
    On GET, render a template that includes a button to start a new game.
    """

    return render_template("home.html")


@app.post("/new-game")
def start_new_game():
    """
    On POST, start a new game of Mastermind and redirect to gameplay template.
    """

    game = Mastermind()
    game_id = str(uuid4())
    session[CURR_GAME_KEY] = game_id
    games[game_id] = game

    flash("New game started!")
    return redirect("/play")


@app.get("/play")
def play_game():
    """
    On GET, renders a template for the user to input their guess for the specified
    game.
    """
    return render_template("gameplay.html")


@app.post("/submit-guess")
def submit_guess():
    """
    On POST, extract form data and score incoming guess for the specified
    game.
    """

    try:
        first_num = int(request.form["first-num"])
        second_num = int(request.form["second-num"])
        third_num = int(request.form["third-num"])
        fourth_num = int(request.form["fourth-num"])

    except ValueError:
        flash("Your guess is invalid; you can only input integers here.")
        return redirect(f"/play")

    game_id = session[CURR_GAME_KEY]
    game = games[game_id]
    guessed_nums = [first_num, second_num, third_num, fourth_num]

    game.handle_guess(guessed_nums)

    if game.has_won:
        return redirect("/win")

    if game.game_over:
        return redirect("/loss")

    return redirect(f"/play")


@app.get("/win")
def display_win():
    """
    On GET, render a template with a win message and a button to start a new game.
    """

    return render_template("win.html")

@app.get("/loss")
def display_loss():
    """
    On GET, render a template with a loss message and a button to start a new game.
    """

    return render_template("loss.html")

@app.post("/restart")
def restart():
    """
    On POST, wipe out the session and redirect to the new-game endpoint.
    """

    if CURR_GAME_KEY in session:
        del session[CURR_GAME_KEY]

    return redirect("/new-game")
