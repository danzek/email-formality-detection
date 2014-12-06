# closing.py
# Created on: Nov 22. 2014
# Last updated: Dec 2, 2014
__author__ = 'Sangmi'


import os


def closing(email):
    """
    Finds email (letter) closing.
    Returns 0 (none) or 1 (exists)
    Email closing list from About.com (http://jobsearch.about.com/od/letterwritingtips/a/letter-closings-list.htm)
    """
    result = 0  # 0: none, 1: closing exists

    # open closing list file
    f = open(os.path.join(os.path.dirname(__file__), 'closings.txt'), 'r')
    # f = open('test.txt', 'r')
    closings = f.read().split("\n")  # e.g. ["Sincerely,", "Best regards,", "Yours Faithfully,"]
    f.close()

    # search for a closing phrase from the bottom line of the current message
    # email.get_current_message() # deals with only current message
    for line in email.body[::-1]: # searches from the last line of the body msg
        for c in closings:
            if line.lower().find(c.lower()) > -1:
                # return c # for testing
                result = 1
                return result
    # returns 0 (none) or 1 (exists)
    return result