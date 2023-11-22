import os

from flask import Flask, request, render_template, jsonify, session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# games = {}

# @app.get("/")
# def homepage():