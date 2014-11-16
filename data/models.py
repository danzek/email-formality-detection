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
import random


class Corpus():
    """Corpus object."""

    def __init__(self):
        """Initial parameter is relative path to the database, assumed to be in the same folder as this file."""
        self.database_filename = os.path.join(os.path.dirname(__file__), 'enron.db')  # hardcode relative path to data

    def build_sqlite_corpus(self, path_to_corpus):
        """Given the path to the unpacked corpus as available from https://www.cs.cmu.edu/~./enron/, parse data
        into SQLite."""
        exclusion_set = set(['contacts', 'calendar'])  # excluded folder names
        for root, subdirs, emails in os.walk(path_to_corpus, topdown=True):
            print 'Parsing ' + root + ' folder.'
            try:
                for email in emails:
                    e = Email(self)
                    e.extract_fields(os.path.join(root, email), root.rsplit('/', 1)[1])  # get parent directory
            except OSError:
                print '\tOSError while processing ' + root + ' directory.'

            subdirs[:] = [d for d in subdirs if d not in exclusion_set]

        print 'Finished creating SQLite corpus.'

    def count_all_emails(self, classification=None):
        """Count all emails in SQLite database, optionally count by classification type

        Optional arguments:
            classification -- classification type to count. Defaults to none (i.e. count all emails).
                              Options: ['unclassified', 'formal', 'informal', 'classified']
                              ('classified' means that email has been classified as either formal or informal)
        """
        conn = sqlite3.connect(self.database_filename)
        conn.text_factory = str
        conn.row_factory = sqlite3.Row

        if not classification:
            sql = "select max(Email_ID) from EMAIL;"
        else:
            sql = "select count(Email_ID) from EMAIL "
            sql += self.get_classification_sql_where_clause(classification)

        cur = conn.execute(sql)
        count = cur.fetchone()[0]

        conn.close()
        return count

    def fetch_all_emails(self, column=None, query=None, exact_match=False):
        """Generator (coroutine) function to fetch all emails; returns one email object at a time. To use, do as
        follows (where c is the instantiated corpus object):

        for email in c.fetch_all_emails():
            print email.sender  # do something with email object

        Optional arguments:
            column -- specify a column by which to filter. Options are:
                      ['id', 'mailbox', 'origin_folder', 'sender', 'recipient', 'date', 'subject', 'classification']
            query -- value by which to filter specified column
            exact_match -- boolean, defaults to False. True will require an exact match (SQL '=' operator), and
                           False will perform a search using the specified query (SQL 'LIKE' operator).
        """
        conn = sqlite3.connect(self.database_filename)
        conn.text_factory = str
        conn.row_factory = sqlite3.Row

        DATABASE_COLUMNS = {
            'id': 'Email_ID',
            'mailbox': 'Email_Mailbox',
            'origin_folder': 'Email_Origin_Folder',
            'sender': 'Email_Sender',
            'recipient': 'Email_Recipient',
            'date': 'Email_Date',
            'subject': 'Email_Subject'
        }

        # matching exact_match to SQL operators
        operator = 'like'  # since exact_match is False by default
        if exact_match:
            operator = '='

        # constructing sql query
        # I verified that SQLite requires no special handling for id, this still works even when treated as a string
        sql = "select * from EMAIL "
        if column and query and column != 'classification':
            sql += "where " + DATABASE_COLUMNS[column] + " " + operator + " '" + query + "';"
        elif column and query and column == 'classification':
            sql += self.get_classification_sql_where_clause(query)
        else:
            sql += ";"

        cur = conn.execute(sql)

        for row in cur:
            e = Email(self)
            e.assign_values(row['Email_ID'], row['Email_Sender'], row['Email_Recipient'], row['Email_Subject'],
                            row['Email_Date'], row['Email_Body'], row['Email_Origin_Folder'], row['Email_Mailbox'],
                            row['Email_Classification'])
            yield e  # generator method

        conn.close()

    def fetch_random_samples(self, quantity):
        """Generator (coroutine) function to fetch a random sample of unclassified emails; returns one email object at
        a time. To use, do as follows (where c is the instantiated corpus object):

        for email in c.fetch_random_sample():
            print email.sender  # do something with email object

        Arguments:
            quantity -- number of random emails to return
        """
        num_unclassified_emails = self.count_all_emails(classification='unclassified')

        # verify there are enough unclassified emails remaining for request; if not, set quantity to the number of
        # remaining unclassified emails
        if quantity > num_unclassified_emails:
            quantity = num_unclassified_emails

        for i in range(quantity):
            pass  # TODO -- handle random number generation and fetch emails, reuse existing code

    def get_classification_sql_where_clause(self, classification):
        """Given classification, returns WHERE clause for SQL statement to get results by classification type.

        Arguments:
            classification -- classification type to count.
                              Options: ['unclassified', 'formal', 'informal', 'classified']
                              ('classified' means that email has been classified as either formal or informal)
        """
        sql = "where Email_Classification "
        if classification.lower() == 'u' or classification.lower() == 'unclassified':
            sql += "= 'U';"
        elif classification.lower() == 'f' or classification.lower() == 'formal':
            sql += "= 'F';"
        elif classification.lower() == 'i' or classification.lower() == 'informal':
            sql += "= 'I';"
        elif classification.lower() == 'c' or classification.lower() == 'classified':
            sql += "= 'I' or Email_Classification = 'F';"  # could use "<> 'U'" but this is a whitelist approach
        else:
            raise ValueError('%s is an invalid classification option.' % classification)

        return sql


class Email():
    """Email object."""
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

    def classify(self, classification):
        self.classification = self.CLASSIFICATION_TYPES[classification]
        conn = sqlite3.connect(self.c.database_filename)
        conn.text_factory = str
        cur = conn.execute(
            """
            update EMAIL set Email Classification = ? where Email_ID = ?;
            """, (self.classification, self.id))
        conn.commit()
        conn.close()

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
            if "-----Original Message-----" in line or "---------------------- Forwarded" in line:
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
                Email_Origin_Folder, Email_Mailbox, Email_Classification) values (?, ?, ?, ?, ?, ?, ?, ?);
                """, (self.sender, self.recipient, self.subject, self.date, sqlite3.Binary(self.body),
                self.origin_folder, self.mailbox, self.classification))
            conn.commit()
            conn.close()