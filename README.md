MastermindGame
==========

A server-side app for playing Mastermind!

Introduction
============

This was quite a fun project! I chose to use Flask, SQLAlchemy, and PostgreSQL
under the hood for this one. I love both object orientation and data design,
so I'll gladly take any opportunity to use an ORM.

Overall, my strategy was to abstract as much logic into the models as possible,
letting the MastermindGame and Guess classes do most of the work, leaving the routes
fairly simple. Good naming, docstrings, and comments where necessary are always key
considerations of mine-- I hope you find these pieces helpful!

## Models

There are two main classes (and corresponding tables in PostgreSQL) for now: **MastermindGame
and Guess**. There is a **one-to-many relationship** between MastermindGame and Guess, such that
one MastermindGame instance can be tied to many Guess instances. That relationship is
defined in the MastermindGame class.

As you look at the models themselves (in the `mastermind.py` file), you'll see a few class
methods-- both classes have factory methods that generate a new instance for us.
I also tucked the API call to fetch some random numbers into an internal class
method on the MastermindGame class for its factory method to lean on.

The MastermindGame class in particular encapsulates a lot of logic, which I organized
into various instance methods and internal methods (these lead with a single underscore
and are used by instance methods as needed).

## Routes

With the models doing a lot of the work, the routes themselves can be focused on the
web-related logic-- taking in data from the request, running operations defined
elsewhere, and returning data or redirecting if necessary.

I chose to incorporate the session to allow my application to send small bits of data
as a cookie to the browser (and to receive it back) to easily keep track of which game
is being played. At this time, the current game id is the only piece of data in the session.
I chose this approach as it's a fairly straightforward way of keeping track of the current game,
plus, if I were to deploy, then people on different browsers would be able to play
their own games.

I also incorporated `g`, which is a global object available to Flask applications
to make data accessible across the entire application, including templates. As the
values in `g` only persist for the duration of a single request, I populate it with
the current game instance before every request (identified by the game id in the session).

As I have a few forms that make a POST request to my server when submitted, I added
some baseline CSRF protection with Flask-WTForms as well.

You'll also see some error-handling via try/except blocks. For example, to handle any
invalid inputs a user provides or if an error happens when trying to to commit a
transaction to the database.

## Extensions

I incorporated the extension of configurable difficulty levels, where a user can select
to play a game that has 4 numbers (easy), 6 numbers (medium), or 8 numbers (hard). They
do this by submitting a form when they start their new game with their choice, which is then
used to fetch their random number combination and ultimately generate their new MastermindGame game
instance.

## Tests

I've written integration tests for the application routes and unit tests for the models,
incorporating mocking for the random nums API to ensure we're never actually calling
that API in our tests. I've reached 96% coverage overall, with 100% coverage of the models.


Development Environment Setup
=============================

Add a `.env` file in the top-level directory and include the following:
```
  DATABASE_URL=postgresql:///mastermind
  SECRET_KEY=whatever-you-want
```

You'll need Python3 and PostgreSQL installed globally. Then, create a virtual environment,
activate it, install the dependencies, and create the databases:

 - `python3 -m venv venv`
 - `source venv/bin/activate`
 - `pip3 install -r requirements.txt`

 - `createdb mastermind`
 - `createdb mastermind_test`

Creating the Database Tables
============================

From the top-level directory, enter ipython (type `ipython` in the terminal) and
run the main app.py file with:

- `%run app.py`

Then, create all tables by running:

- `db.create_all()`

Then quit ipython (on Mac, this is ctrl+d).

Starting the App
================

If you want to run on port 5000, from the top-level directory, run:

 - `flask run`

If port 5000 is already taken by another process, as is often the case for
newer machines, run on the port of your choosing with:

 - `flask run -p [port number here] # Tip: port 5001 is often a good choice!`

Then, visit `localhost:[port-num-here]/` in your browser to go to the homepage
and start a new game!

Running Tests
=============

Run all tests:
- `python3 -m unittest -v` (from highest level)

Run a specific file of tests:
- `python3 -m unittest -v [file-name-here]`

Run tests and generate a coverage report in the terminal:

- `coverage run -m unittest`
- `coverage report -m`