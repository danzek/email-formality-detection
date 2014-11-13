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

Models for corpus preparation.
"""

__author__ = "Dan O'Day"
__copyright__ = "Copyright 2014, Dan O'Day, Purdue University"
__credits__ = ["Dan O'Day", "Robert Hinh", "Upasita Jain", "Sangmi Shin", "Penghao Wang", "Julia Taylor"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Dan O'Day"
__email__ = "doday@purdue.edu"
__status__ = "Development"


import os
import sqlite3
import pickle


class Corpus():
    """
    Corpus object.
    """

    def __init__(self):
        self.database_filename = "enron.db"

    def build_sqlite_corpus(self, path_to_corpus):
        for person in os.listdir(path_to_corpus):
            print 'Processing email for ' + person
            inbox = os.path.join(path_to_corpus, person, 'inbox').decode('utf-8')
            sent = os.path.join(path_to_corpus, person, 'sent').decode('utf-8')

            try:
                for email in os.listdir(inbox):
                    e = Email()
                    e.extract_fields(os.path.join(inbox, email), 'Inbox')
            except OSError:
                print '\tNo inbox folder in ' + person + ' directory.'

            try:
                for email in os.listdir(sent):
                    e = Email()
                    e.extract_fields(os.path.join(sent, email), 'Sent')
            except OSError:
                print '\tNo sent folder in ' + person + ' directory.'

        print 'Finished creating SQLite corpus.'

    def fetch_all_emails(self):
        conn = sqlite3.connect(self.database_filename)
        conn.text_factory = str
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur = conn.execute("select * from EMAIL;")

        for row in cur:
            e = Email(self)
            e.assign_values(row['Email_ID'], row['Email_Sender'], row['Email_Recipient'], row['Email_Subject'],
                            row['Email_Date'], row['Email_Body'], row['Email_Origin_Folder'], row['Email_Mailbox'],
                            row['Email_Classification'])
            yield e  # generator method

        conn.close()



class Email():
    """
    Email object.
    """

    def __init__(self, corpus):
        self.c = corpus
        self.id = 0
        self.mailbox = ""
        self.origin_folder = ""
        self.sender = ""
        self.recipient = ""
        self.date = ""
        self.subject = ""
        self.body = ""

        self.CLASSIFICATION_TYPES = {
            'Unclassified': 'U',
            'Formal': 'F',
            'Informal': 'I'}
        self.classification = self.CLASSIFICATION_TYPES['Unclassified']
        self.feature_set = {}

    def assign_values(self, pk, sender, recipient, subject, date, body, origin_folder, mailbox, classification):
        self.id = pk
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.date = date
        self.body = pickle.loads(body)
        self.origin_folder = origin_folder
        self.mailbox = mailbox
        self.classification = classification

    def add_feature(self, feature_id, value):
        self.feature_set[feature_id] = value

    def create_db_table(self):
        print 'Creating database...'
        conn = sqlite3.connect(self.c.database_filename)
        cur = conn.cursor()

        cur.execute(""" create table EMAIL (
                          Email_ID integer primary key autoincrement not null,
                          Email_Sender varchar null,
                          Email_Recipient varchar null,
                          Email_Subject varchar null,
                          Email_Date varchar null,
                          Email_Body blob null,
                          Email_Origin_Folder varchar null,
                          Email_Mailbox varchar null,
                          Email_Classification int null
                    );""")  # Email_Classification = 0 if deemed informal and 1 if formal
        print '\tEMAIL table created successfully.'

        conn.close()

    def enumerate_lines(self):
        for line in self.body:
            yield line.rstrip()  # generator method

    def enumerate_words(self):
        for line in self.enumerate_lines():
            for word in line:
                yield word  # generator method

    def extract_fields(self, email_file, mailbox):
        valid_email = True

        # check if database already exists; if not, create it
        if not os.path.isfile(self.c.database_filename):
            print 'A database with this name does not yet exist.'
            self.create_db_table()

        try:
            f = open(email_file, 'r')
        except IOError:
            print '\tDirectory passed as email, skipping folder and all children.'
            valid_email = False

        self.mailbox = mailbox

        if valid_email:
            lines = f.readlines()

            for line_number, line in enumerate(lines):
                if line.startswith("Date: "):
                    self.date = line[6:]
                elif line.startswith("From: "):
                    self.sender = line[6:]
                elif line.startswith("To: "):
                    self.recipient = line[4:]
                elif line.startswith("Subject: "):
                    self.subject = line[9:]
                elif line.startswith("X-Origin: "):
                    self.origin_folder = line[10:]
                elif line.startswith("X-FileName:"):
                    offset = line_number + 1  # skip blank line separating description from body
                    self.body = pickle.dumps(lines[offset:])
                    break

            f.close()

            self.save_email()

    def get_current_message(self):
        most_recent_body = []
        for line in self.body:
            if "-----Original Message-----" in line:
                self.body = most_recent_body
            else:
                most_recent_body.append(line)

    def is_missing_values(self):
        if not self.mailbox or not self.origin_folder:
            return True
        elif not self.sender or not self.recipient:
            return True
        elif not self.subject and not self.body:
            return True
        else:
            return False

    def save_email(self):
        if not self.is_missing_values():
            conn = sqlite3.connect(self.c.database_filename)
            conn.text_factory = str
            cur = conn.execute(
                """
                insert into EMAIL (Email_Sender, Email_Recipient, Email_Subject, Email_Date, Email_Body,
                Email_Origin_Folder, Email_Mailbox) values (?, ?, ?, ?, ?, ?, ?);
                """, (self.sender, self.recipient, self.subject, self.date, sqlite3.Binary(self.body),
                self.origin_folder, self.mailbox))
            conn.commit()
            conn.close()