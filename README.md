Mastermind
==========

A server-side app for playing Mastermind!

Introduction
============

This was quite a fun project! I chose to use Flask, SQLAlchemy, and PostgreSQL
under the hood for this one. I love both object orientation and data design,
so I'll gladly take any opportunity to use an ORM.

Overall, my strategy was to abstract as much logic into the models as possible,
letting the Mastermind and Guess classes do most of the work, leaving the routes
fairly simple. Good naming, docstrings, and comments where necessary are always key
considerations of mine-- I hope you find these pieces helpful!

## Models

There are two main classes (and corresponding tables in PostgreSQL) for now: *Mastermind
and Guess*. There is a *one-to-many relationship* between Mastermind and Guess, such that
one mastermind game instance can be tied to many guess instances. That relationship is
defined in the Mastermind class.

As you look at the models themselves (in the `mastermind.py` file), you'll see a few class
methods-- both classes have factory methods that generate a new instance for us.
I also tucked the API call to fetch some random numbers into an internal class
method on the Mastermind class for its factory method to lean on.

The Mastermind class in particular encapsulates a lot of logic, which I organized
into various instance methods and internal methods (these lead with a single underscore
and are used by instance methods as needed).

## Routes

With the models doing a lot of the work, the routes themselves can be focused on the
web-related logic-- taking in data from the request, running operations defined
in a class elsewhere, and returning data or redirecting if necessary.

I chose to incorporate the session to allow my application to send small bits of data
as a cookie to the browser (and to receive it back) to easily keep track of which game
is being played. In this case, the current game id is the only thing in the session.

I also incorporated `g`, which is a global object available to Flask applications
to make data accessible across the entire app. As the values in `g` only live for
the duration of a single request, I populate it with the current game instance
(identified by the game id in the session) so that data is accessible everywhere
if needed.

As I have a few forms that make a POST request to my server when submitted, I added
some baseline CSRF protection with Flask-WTForms as well.

You'll also see some error-handling via try/except blocks. For example, to handle any
invalid inputs a user provides or if an error happens when trying to to commit a
transaction to the database.

## Extensions

I incorporated the extension of configurable difficulty levels, where a user can select
to play a game that has 4 numbers (easy), 6 numbers (medium), or 8 numbers (hard). They
do this by submitting a form when they start their new game with their choice, which is then
used to fetch their random number combination and ultimately generate their new Mastermind game
instance.

## Tests

I've written tests for the application routes, incorporating mocking for the random nums API to
ensure we're never actually calling that API in our tests.


Development Environment Setup
=============================

Add a `.env` file in the top level directory and include the following:
```
  DATABASE_URL=postgresql:///mastermind
  SECRET_KEY=whatever-you-want
```

You'll need Python3 and PostgreSQL installed globally. Then, create a virtual environment,
activate it, and install the dependencies:

 - `python3 -m venv venv`
 - `source venv/bin/activate`
 - `pip3 install -r requirements.txt`

 - `createdb mastermind`
 - `createdb mastermind_test`

Creating the Database Tables
============================

From the top-level directory, enter ipython and run the main app.py file with:

- `%run app.py`

Then, create all tables by running:

- `db.create_all()`

Then quit ipython.

Starting the App
================

If you want to run on port 5000, from the top-level directory, run:

 - `flask run`

If port 5000 is already taken by another process, as is often the case for
newer machines, run on the port of your choosing with:

 - `flask run -p [port number here] # Note: port 5001 is often a good choice!`

Then, visit `localhost:[port-num-here]/` in your browser to go to the home page!

Running Tests
=============

Run all tests:
- `python3 -m unittest -v` (from highest level)

Run a specific file of tests:
- `python3 -m unittest -v [file-name-here]`