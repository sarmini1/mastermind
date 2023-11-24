import os

from flask import Flask, request, render_template, session, redirect, flash
from uuid import uuid4

from mastermind import Mastermind

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

curr_game = {}
# TODO: implement session so that multiple folks can play


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
    curr_game[game_id] = game
    flash("New game started!")

    return redirect(f"/play/{game_id}")


@app.get("/play/<game_id>")
def play_game(game_id):
    """
    On GET, renders a template for the user to input their guess for the specified
    game.
    """

    game = curr_game[game_id]
    remaining_guesses = game.remaining_guesses
    guess_history = game.guessed_nums_history
    feedback = game.feedback

    return render_template(
        "gameplay.html",
        game_id=game_id,
        remaining_guesses=remaining_guesses,
        guess_history=guess_history,
        feedback=feedback
    )


@app.post("/submit-guess/<game_id>")
def submit_guess(game_id):
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
        return redirect(f"/play/{game_id}")

    breakpoint()
    game = curr_game[game_id]
    guessed_nums = [first_num, second_num, third_num, fourth_num]

    game.handle_guess(guessed_nums)

    if game.has_won:
        return redirect("win.html")

    if game.game_over:
        return redirect("lose.html")

    return redirect(f"/play/{game_id}")
