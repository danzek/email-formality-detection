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
import cStringIO


app = flask.Flask(__name__)
c = Corpus()

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
        return flask.render_template('login.html')

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
    e = c.fetch_random_sample(classification='unclassified')
    if e:
        return show_email(e.id, classify=True)
    else:
        flask.abort(404)

@app.route('/email/')
def search_emails():
    return 'test'

@app.route('/email/<int:email_id>')
def show_email(email_id, classify=False):
    if classify:
        form_value = '''<input class="btn btn-primary btn-lg btn-block" type="submit" value="Formal"><br />
                        <input class="btn btn-danger btn-lg btn-block" type="submit" value="Informal">'''
    else:
        form_value = ""
    eg = c.fetch_all_emails(column='id', query=email_id, exact_match=True)  # eg = email generator method
    email = next(eg, None)
    if email:
        return flask.render_template('emailview.html',
                                     email_id=email.id,
                                     email_sender=email.sender,
                                     email_recipient=email.recipient,
                                     email_date=email.date,
                                     email_subject=email.subject,
                                     email_body=render_email_body(email.id),
                                     form=form_value)
    else:
        flask.abort(404)

@app.route('/email/<int:email_id>/body/')
def render_email_body(email_id):
    eg = c.fetch_all_emails(column='id', query=email_id, exact_match=True)  # eg = email generator method
    e = next(eg, None)
    if e:
        f = cStringIO.StringIO()
        for line in e.enumerate_lines():
            f.write(line + '&nbsp;<br />')  # have to add html newline or else it renders as a clump
        return f.getvalue()
    else:
        flask.abort(404)

if __name__ == '__main__':
    app.debug = True
    app.secret_key = SECRET_KEY
    app.run()