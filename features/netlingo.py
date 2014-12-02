# netlingo.py
# Nov 26. 2014
__author__ = 'Sangmi'

from data.models import Corpus
import re
import os


def find_netlingo(email):
    """ Detects abbreviated terms in emails
    based on netlingo.com acronyms: http://www.netlingo.com/top50
    """
    # read NetLingo file and store with 'set' type
    f = open(os.path.join(os.path.dirname(__file__), 'NetLingo.txt'), 'r')
    netlingo = set(f.read().lower().split())
    f.close()

    # remove some of the potentially naturally occurring terms
    new_list = set([w for w in netlingo if len(w) > 2])

    # split the email body with whitespace and special characters to compare with the netlingo set
    # e.g. "FYI," --> "FYI"
    #      "ASAP!" --> "ASAP"
    body = ""
    for line in email.enumerate_lines():
        body += line.lower()
    body = set(re.split('\W+',body)) # remove any special characters behind words
    detected_lingo = set(body) & new_list # AND operation between two sets

    return len(detected_lingo)