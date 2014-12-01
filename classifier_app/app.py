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
sys.path.append("..")  # the next import won't work without this, only for local site
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
        classified = c.count_all_emails(classification='c')
        total = c.count_all_emails()
        percentage_classified = float("{0:.2f}".format((float(classified) / total)*100))
        return flask.render_template('menu.html', username=flask.session['username'],
                                     classified_num=str(classified),
                                     total_num=str(total),
                                     progress=str(percentage_classified),
                                     progress2=str(percentage_classified),
                                     progress_again=str(percentage_classified))
    else:
        return flask.redirect(flask.url_for('login'))

@app.route('/classify/')
def classify():
    if 'username' in flask.session:
        e = c.fetch_random_sample(classification='unclassified')
        if e:
            return show_email(e.id, classify=True)
        else:
            flask.abort(404)
    else:
        return flask.redirect(flask.url_for('login'))

@app.route('/classify-email/<int:email_pk>/<classification>')
def classify_email(email_pk, classification):
    if 'username' in flask.session:
        eg = c.fetch_all_emails(column='id', query=str(email_pk), exact_match=True)
        e = next(eg, None)
        if e:
            e.classify(classification)

        return flask.redirect('classify')
    else:
        return flask.redirect(flask.url_for('login'))

@app.route('/email/', methods=['GET', 'POST'])
def search_emails():
    if 'username' in flask.session:
        if flask.request.method == 'POST':
            email_id = flask.request.form['email_id']
            if not email_id:
                return flask.render_template('emailsearch.html', message='Specify ID')
            else:
                try:
                    int_id = int(email_id)
                except ValueError:
                    return flask.render_template('emailsearch.html', message='Invalid ID')

                return show_email(int_id)
        else:
            return flask.render_template('emailsearch.html')
    else:
        return flask.redirect(flask.url_for('login'))

@app.route('/email/<int:email_id>')
def show_email(email_id, classify=False):
    if 'username' in flask.session:
        if classify:
            form_value = '<a class="btn btn-primary btn-lg btn-block" href="' + flask.url_for('classify_email',
                         email_pk=email_id, classification='Formal') + '" role="button">Formal</a><br />' + \
                         '<a class="btn btn-danger btn-lg btn-block" href="' + flask.url_for('classify_email',
                         email_pk=email_id, classification='Informal') + '" role="button">Informal</a><br />' + \
                         '<a class="btn btn-warning btn-lg btn-block" href="' + flask.url_for('classify') + \
                         '" role="button">Unsure</a><br />'
        else:
            form_value = '<a class="btn btn-primary btn-lg btn-block" href="' + flask.url_for('search_emails') + \
                         '" role="button">New Email ID</a>'
        eg = c.fetch_all_emails(column='id', query=email_id, exact_match=True)  # eg = email generator method
        email = next(eg, None)
        if email:
            class_types = {
                'U': 'UNCLASSIFIED',
                'F': 'FORMAL',
                'I': 'INFORMAL'
            }
            return flask.render_template('emailview.html',
                                         email_id=email.id,
                                         email_class=class_types[email.classification],
                                         email_sender=email.sender,
                                         email_recipient=email.recipient,
                                         email_date=email.date,
                                         email_subject=email.subject,
                                         email_body=render_email_body(email.id),
                                         form=form_value)
        else:
            flask.abort(404)
    else:
        return flask.redirect(flask.url_for('login'))

@app.route('/email/<int:email_id>/body/')
def render_email_body(email_id):
    if 'username' in flask.session:
        eg = c.fetch_all_emails(column='id', query=email_id, exact_match=True)  # eg = email generator method
        e = next(eg, None)
        if e:
            f = cStringIO.StringIO()
            for line in e.enumerate_lines():
                f.write(line + '&nbsp;<br />')  # have to add html newline or else it renders as a clump
            return f.getvalue()
        else:
            flask.abort(404)
    else:
        return flask.redirect(flask.url_for('login'))

if __name__ == '__main__':
    app.debug = True
    app.secret_key = SECRET_KEY
    app.run()