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

Put Enron emails into SQLite database. Currently this only gets the 'inbox' and 'sent' folders. Should it get more?
"""

__author__ = "Dan O'Day"
__copyright__ = "Copyright 2014, Dan O'Day, Purdue University"
__credits__ = ["Dan O'Day", "Robert Hinh", "Upasita Jain", "Sangmi Shin", "Penghao Wang", "Julia Taylor"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Dan O'Day"
__email__ = "doday@purdue.edu"
__status__ = "Development"


import sys
from models import Corpus


def main():
    path_to_corpus = sys.argv[1]  # ignore any additional parameters

    if not path_to_corpus:
        print 'No arguments specified.\nusage: python prep_corpus.py {folder(s) containing Enron corpus}\n'
        sys.exit(1)

    c = Corpus()
    c.build_sqlite_corpus(path_to_corpus)


if __name__ == '__main__':
    main()