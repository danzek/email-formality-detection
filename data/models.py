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
import MySQLdb
import pickle
import random


class Corpus():
    """Corpus object.

        cnx -- mySQL connection object
        cur -- mySQL cursor object
    """
    def __init__(self):
        self.DB_PASSWORD = 'haha_no_not_on_github_:)'  # real password not uploaded to Github
        self.conn = MySQLdb.connect('mysql.server', 'cnit499nlt', self.DB_PASSWORD, 'cnit499nlt$enron')

    def build_sqlite_corpus(self, path_to_corpus):
        """Given the path to the unpacked corpus as available from https://www.cs.cmu.edu/~./enron/, parse data
        into SQLite.

        Arguments:
            path_to_corpus -- full path to unpacked Enron email corpus
        """
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

    def count_all_emails(self, classification=None, validated=None):
        """Count all emails in SQLite database, optionally count by classification type

        Optional arguments:
            classification -- classification type to count. Defaults to none (i.e. count all emails).
                              Options: ['unclassified', 'formal', 'informal', 'classified']
                              ('classified' means that email has been classified as either formal or informal)
        """

        if not classification and not validated:
            sql = "select max(Email_ID) from EMAIL;"
        elif classification and not validated:
            sql = "select count(Email_ID) from EMAIL "
            sql += self.__get_classification_sql_where_clause(classification)
        elif not classification and validated:
            sql = "select count(Email_ID) from EMAIL where Email_Correct_Current_Message"
            if validated.lower() == 'u':
                sql += "='U'"
            elif validated.lower() == 't':
                sql += "='T'"
            elif validated.lower() == 'a':
                sql += "<>'U'"

        self.db_connect()
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(sql)
            count = cur.fetchone()[0]

        return count

    def create_db_table(self):
        """Create sqlite database table for emails (also creates database if needed)."""
        print 'Creating EMAIL table...'
        self.db_connect()
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(""" create table `EMAIL` (
                                      Email_ID int not null auto_increment primary key,
                                      Email_Sender varchar(255) null,
                                      Email_Recipient text null,
                                      Email_Subject varchar(255) null,
                                      Email_Date varchar(255) null,
                                      Email_Body blob null,
                                      Email_Origin_Folder varchar(255) null,
                                      Email_Mailbox varchar(255) null,
                                      Email_Classification char(1) null,
                                      Email_Correct_Current_Message char(1) null
                              ) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ENGINE=InnoDB;""")
            print '\tEMAIL table created successfully.'

    def db_connect(self):
        self.conn = MySQLdb.connect('mysql.server', 'cnit499nlt', self.DB_PASSWORD, 'cnit499nlt$enron')

    def fetch_all_emails(self, column=None, query=None, exact_match=False):
        """Generator (coroutine) method to fetch all emails; returns one email object at a time. To use, do as
        follows (where c is the instantiated Corpus object):

            # get all emails
            for email in c.fetch_all_emails():
                print email.sender  # do something with email object

            # retrieves all emails with 'fraud' in the subject line
            for email in c.fetch_all_emails(column='subject', query='fraud', exact_match=False)
                print email.sender  # do something with email object

            # get emails in range
            for email in c.fetch_all_emails(start_id=1, end_id=500)
                print email.id  # do something with email object

        Optional arguments:
            column -- specify a column by which to filter. Options are:
                      ['id', 'mailbox', 'origin_folder', 'sender', 'recipient', 'date', 'subject', 'classification',
                      'validated']
            query -- value by which to filter specified column
            exact_match -- boolean, defaults to False. True will require an exact match (SQL '=' operator), and
                           False will perform a search using the specified query (SQL 'LIKE' operator).
            start_id -- if selecting a range of emails by id (pk), this is the first id of that range
            end_id -- if selecting a range of emails by id (pk), this is the last id of that range
        """

        DATABASE_COLUMNS = {
            'id': 'Email_ID',
            'mailbox': 'Email_Mailbox',
            'origin_folder': 'Email_Origin_Folder',
            'sender': 'Email_Sender',
            'recipient': 'Email_Recipient',
            'date': 'Email_Date',
            'subject': 'Email_Subject',
            'validated': 'Email_Correct_Current_Message',
        }

        # matching exact_match to SQL operators
        operator = 'like'  # since exact_match is False by default
        if exact_match:
            operator = '='

        # constructing sql query
        # I verified that SQLite requires no special handling for id, this still works even when treated as a string
        sql = "select * from EMAIL "
        if column and query and column != 'classification':
            sql += "where " + DATABASE_COLUMNS[column] + " " + operator + " '" + str(query) + "';"
        elif column and query and column == 'classification':
            sql += self.__get_classification_sql_where_clause(query)
        else:
            sql += ";"

        self.db_connect()
        with self.conn:
            cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(sql)
            rows = cur.fetchall()

            for row in rows:
                e = Email(self)
                e.assign_values(row['Email_ID'], row['Email_Sender'], row['Email_Recipient'], row['Email_Subject'],
                                row['Email_Date'], row['Email_Body'], row['Email_Origin_Folder'], row['Email_Mailbox'],
                                row['Email_Classification'], row['Email_Correct_Current_Message'])

                yield e  # generator method

    def fetch_random_sample(self, classification=None, validated=None):
        """Fetches a random email sample: returns one email object; optionally filter by classification type. To use,
        do as follows (where c is the instantiated Corpus object):

            email = c.fetch_random_sample():
            print email.recipient  # do something with email object

        This should be improved in a production model to improve performance.

        Arguments:
            classification -- classification type to count. Defaults to none (i.e. return any email).
                              Options: ['unclassified', 'formal', 'informal', 'classified']
                              ('classified' means that email has been classified as either formal or informal)
        """
        list_of_ids = []

        if classification:
            if classification.lower() == 'u' or classification.lower() == 'unclassified':
                # this is too slow, especially since initially all emails are unclassified
                #for email in self.fetch_all_emails(column='classification', query='u'):
                    #list_of_ids.append(email.id)

                # this revised method is much quicker for unclassified emails so long as they are the majority class
                remaining_unclassified_emails = self.count_all_emails(classification='u')
                if remaining_unclassified_emails > 0:
                    while True:
                        random_id = random.randrange(1, self.count_all_emails(classification='u')+1)
                        eg = self.fetch_all_emails(column='id', query=str(random_id), exact_match=True)
                        e = next(eg, None)
                        if e:
                            if e.classification == 'U':
                                return e
                else:
                    return None
            elif classification.lower() == 'f' or classification.lower() == 'formal':
                for email in self.fetch_all_emails(column='classification', query='f'):
                    list_of_ids.append(email.id)
            elif classification.lower() == 'i' or classification.lower() == 'informal':
                for email in self.fetch_all_emails(column='classification', query='i'):
                    list_of_ids.append(email.id)
            elif classification.lower() == 'c' or classification.lower() == 'classified':
                for email in self.fetch_all_emails(column='classification', query='c'):
                    list_of_ids.append(email.id)

        if validated:
            # this revised method is much quicker for unvalidated emails so long as they are the majority class
            if validated.lower() == 'u':
                total_emails = self.count_all_emails()
                while True:
                    random_id = random.randrange(1, total_emails+1)
                    eg = self.fetch_all_emails(column='id', query=str(random_id), exact_match=True)
                    e = next(eg, None)
                    if e:
                        #if e.current_message == 'U':
                        return e
            if validated.lower() == 't':
                for email in self.fetch_all_emails(column='validated', query='T', exact_match=True):
                    list_of_ids.append(email.id)
            if validated.lower() == 'f':
                for email in self.fetch_all_emails(column='validated', query='F', exact_match=True):
                    list_of_ids.append(email.id)


        # if list has values, choose a random list index and pass the generator function to eg (email generator)
        if list_of_ids:
            random_list_index = random.randrange(0, len(list_of_ids))
            eg = self.fetch_all_emails(column='id', query=str(list_of_ids[random_list_index]), exact_match=True)
            return next(eg, None)  # should only be one email, return None if StopIteration exception raised
        else:
            print 'There are no samples that meet the specified criteria.'
            return None

    def __get_classification_sql_where_clause(self, classification):
        """Given classification, returns WHERE clause for SQL statement to get results by classification type.
        (for internal class use only, i.e. private method)

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
        """Initial parameters are set to empty strings. Corpus object is required as parameter to instantiate email.

        Required arguments:
            c -- Corpus object to which email belongs.

        Optional arguments:
            id -- primary key integer ID of email in SQLite database
            mailbox -- name of direct parent folder in which email was extracted
            origin_folder -- upper level folder from which email was extracted (generally an Enron username)
            sender -- email sender
            recipient -- email recipient
            date -- date string from email header (as is, not parsed as python date object)
            subject -- email subject
            body -- email body stored in binary format (BLOB). Data is picked then written as binary. Use the provided
                    methods for retrieving email body to ensure data is unpickled and handled properly
                    (enumerate_lines() and enumerate_words())
            current_message -- Whether or not current message has been extracted (used in framework validation), default
                               is 'U' for unknown; other options are true and false ['U', 'T', 'F']
            CLASSIFICATION_TYPES -- for internal use only, convert plaintext classification to database character
            classification - single-character classification ['U', 'F', 'I']
            feature_set - feature vector (dictionary) storing extracted features from this object (populated with
                          add_feature())
        """
        self.c = corpus
        self.id = 0
        self.mailbox = ""
        self.origin_folder = ""
        self.sender = ""
        self.recipient = ""
        self.date = ""
        self.subject = ""
        self.body = ""
        self.current_message = "U"

        self.CLASSIFICATION_TYPES = {
            'Unclassified': 'U',
            'Formal': 'F',
            'Informal': 'I'}
        self.classification = self.CLASSIFICATION_TYPES['Unclassified']
        self.feature_set = {}

    def assign_values(self, pk, sender, recipient, subject, date, body, origin_folder, mailbox, classification, cmsg):
        """Takes parameters that are optional when object is instantiated and assigns them to the object (see docstring
        for __init__.py for an explanation of each argument)."""
        self.id = pk
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.date = date
        self.body = pickle.loads(body)
        self.origin_folder = origin_folder
        self.mailbox = mailbox
        self.classification = classification
        self.current_message = cmsg

    def add_feature(self, feature_id, value):
        """Adds a single new feature to the feature_set dictionary.

        Arguments:
            feature_id -- integer key to reference to the feature
            value -- extracted/calculated value of the feature
        """
        self.feature_set[feature_id] = value

    def classify(self, classification):
        """Classify an email.

        Arguments:
            classification -- specify object classification ['Unclassified', 'Formal', 'Informal']
        """
        self.classification = self.CLASSIFICATION_TYPES[classification]
        self.c.db_connect()
        with self.c.conn:
            cur = self.c.conn.cursor()
            cur.execute(
                "update EMAIL set Email_Classification = %s where Email_ID = %s", (self.classification, int(self.id)))
            self.c.conn.commit()

    def enumerate_lines(self):
        """Generator (coroutine) numerates lines in email body. Use like so:

        for line in email.enumerate_lines():
            print line  # do something with line
        """
        for line in self.body:
            yield line.rstrip()  # generator method

    def enumerate_words(self):
        """Generator (coroutine) numerates words in email body. Use like so:

        for word in email.enumerate_words():
            print word  # do something with word
        """
        words = []
        for line in self.enumerate_lines():
            words.extend(line.split(' '))

        for word in words:
            yield word  # generator method

    def extract_fields(self, email_file, mailbox):
        """Extracts fields from email file and saves them to database.

        Arguments:
            email_file -- file path to email from which data will be extracted
            mailbox -- name of direct parent folder in which email was extracted
        """
        valid_email = True

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
        """Reduce email body to most recent message only.

        Needs more work/improvement.
        """
        most_recent_body = []
        older_message_discriminators = [
            "----Original Message",
            "====Original Message",
            "----- Forwarded",
            "-----Forwarded",
            "===== Forwarded",
            "=====Forwarded",
        ]

        for line in self.enumerate_lines():
            for discriminator in older_message_discriminators:
                if (discriminator in line) or line.startswith('>'):
                    self.body = most_recent_body
                    return

            most_recent_body.append(line)

    def __is_missing_values(self):
        """Checks if email is missing important values. Private method."""
        if not self.mailbox or not self.origin_folder:
            return True
        elif not self.sender or not self.recipient:
            return True
        elif not self.subject and not self.body:
            return True
        else:
            return False

    def save_email(self):
        """Saves email to database."""
        if not self.__is_missing_values():
            self.c.db_connect()
            with self.c.conn:
                cur = self.c.conn.cursor()
                sql = """insert into EMAIL (Email_Sender, Email_Recipient, Email_Subject, Email_Date, Email_Body,
                        Email_Origin_Folder, Email_Mailbox, Email_Classification) values (%s, %s, %s, %s, %s, %s, %s, %s);
                        """
                params = (self.sender, self.recipient, self.subject, self.date, self.body, self.origin_folder,
                          self.mailbox, self.classification)
                cur.execute(sql, params)
                self.c.conn.commit()

    def validate(self, valid):
        """Classify an email.

        Arguments:
            valid -- Whether or not current message was retrieved (True or False)
        """
        if valid=='T':
            self.current_message = 'T'
        elif valid=='F':
            self.current_message = 'F'
        else:
            return

        self.c.db_connect()
        with self.c.conn:
            cur = self.c.conn.cursor()
            cur.execute(
                "update EMAIL set Email_Correct_Current_Message = %s where Email_ID = %s",
                (self.current_message, int(self.id)))
            self.c.conn.commit()