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

Main corpus processor.
"""

__author__ = "Dan O'Day"
__copyright__ = "Copyright 2014, Dan O'Day, Purdue University"
__credits__ = ["Dan O'Day", "Robert Hinh", "Upasita Jain", "Sangmi Shin", "Penghao Wang", "Julia Taylor"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Dan O'Day"
__email__ = "doday@purdue.edu"
__status__ = "Development"


from data.models import Corpus


def main():
    c = Corpus()
    features = {}

    for email in c.fetch_all_emails():
        # this is where all feature calls should go, e.g. pass the values needed to the feature
        # features[email.id] = my_feature(email.sender, email.body)  # or write to file after each feature extraction

        # sample code for how to retrieve values
        print email.sender
        print email.date

        # retrieving the body of the email is a special case; iterate through each line in your feature code like so:
        for line in email.body:
            print line.rstrip()  # pickling the data line by line adds extra carriage returns; rstrip() removes these


if __name__ == '__main__':
    main()