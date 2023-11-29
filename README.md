# Mastermind

A server-side app for playing Mastermind!

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

If port 5000 is already taken by another process, run on the port of your choosing with:
Note: port 5001 is often a good option!

 - `flask run -p [port number here]`

Running Tests
=============

Run all tests:
- `python3 -m unittest -v` (from highest level)

Run a specific file of tests:
- `python3 -m unittest -v [file-name-here]`