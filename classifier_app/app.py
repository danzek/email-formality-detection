#!/usr/bin/env python
# -*- coding: utf_8 -*-

"""
Dan O'Day
Robert Hinh
Upasita Jain
Sangmi Shin
Penghao Wang

Purdue University
CNIT499 Natural Language Technologies

Flask web app for classifying a random sample of emails
"""

__author__ = "Dan O'Day"
__copyright__ = "Copyright 2014, Dan O'Day, Purdue University"
__credits__ = ["Dan O'Day", "Robert Hinh", "Upasita Jain", "Sangmi Shin", "Penghao Wang", "Julia Taylor"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Dan O'Day"
__email__ = "doday@purdue.edu"
__status__ = "Development"


import flask
from auth import authenticate_user, SECRET_KEY  # this file is not included on github for (hopefully) obvious reasons
import sys
sys.path.append("..")  # the next import won't work without this
from data.models import Corpus


app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        if not username or not password:
            return flask.render_template('login.html', message='Missing required field')
        elif authenticate_user(username, password):
            flask.session['username'] = flask.request.form['username']
            return flask.render_template('menu.html', username=username)
        else:
            return flask.render_template('login.html', message='Invalid credentials')
    else:
        return flask.render_template('login.html', message="Please log in")

@app.route('/logout/')
def logout():
    flask.session.pop('username', None)
    return flask.redirect(flask.url_for('index'))

@app.route('/menu/')
def menu():
    if 'username' in flask.session:
        return flask.render_template('menu.html', username=flask.session['username'])
    else:
        return flask.redirect(flask.url_for('login'))

@app.route('/classify/')
def classify():
    return flask.render_template('emailview.html')  # emailview is master, actually redirect to specific random email


if __name__ == '__main__':
    app.debug = True
    app.secret_key = SECRET_KEY
    app.run()