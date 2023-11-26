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
    """If a game has been started, put the instance onto g before each request."""

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

    difficulty = int(request.form["difficulty"])

    game = Mastermind(count=difficulty)
    game_id = str(uuid4())
    session[CURR_GAME_KEY] = game_id
    games[game_id] = game

    flash("New game started!")
    return redirect("/play")


@app.get("/play")
def play_game():
    """
    On GET, renders a template for the user to input their guess for the current
    game.

    If no current game exists, redirects home.
    """

    if "curr_game" not in g:
        return redirect("/")

    return render_template("gameplay.html")


@app.post("/submit-guess")
def submit_guess():
    """
    On POST, extract form data and score incoming guess for the current game.

    If no current game exists, redirects home.
    """

    if "curr_game" not in g:
        return redirect("/")

    guessed_nums = []
    i = 0

    for i in range(g.curr_game.count):
        try:
            num = int(request.form[f"num-{i}"])
            guessed_nums.append(num)
            i += 1
        except ValueError:
            flash("Your guess is invalid; you can only input integers here.")
            return redirect("/play")

    game_id = session[CURR_GAME_KEY]
    game = games[game_id]

    breakpoint()
    game.handle_guess(guessed_nums)
    if game.has_won:
        return redirect("/win")

    if game.game_over:
        return redirect("/loss")

    return redirect("/play")


@app.get("/win")
def display_win():
    """
    On GET, render a template with a win message and a button to start a new game.

    If no current game exists, redirects home.
    """

    if "curr_game" not in g:
        return redirect("/")

    return render_template("win.html")


@app.get("/loss")
def display_loss():
    """
    On GET, render a template with a loss message and a button to start a new game.

    If no current game exists, redirects home.
    """

    if "curr_game" not in g:
        return redirect("/")

    return render_template("loss.html")


# @app.post("/restart")
# def restart():
#     """
#     On POST, wipe out the session and redirect home endpoint.
#     """

#     if CURR_GAME_KEY in session:
#         del session[CURR_GAME_KEY]

#     return redirect("/")
