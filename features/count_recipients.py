# count_recipients.py
# created on:       Dec. 2, 2014
# last updated on : Dec. 3, 2014
__author__ = 'Sangmi'

from features.extract_group_list import group_list


def count_recipients(email):
    """
    counts recipients
    * counts a group email address as 100
    returns the number of recipients (int)
    * (e.g. 1 group email + 2 individual email = 1*100 + 2 = 102 (returns 102))
    """

    recipients = set(email.recipient.replace('\r\n', '').lstrip().split(', '))

    # initialize
    group_count = 0  # one-to-many (group recipients)
    count = 0  # number of recipients

    # one-to-many (group recipients)
    # e.g. all.employees@enron.com, all.users@enron.com, etc.
    recipients = set(filter(None, recipients))
    group_count = len(recipients & group_list())

    # number of recipients
    count = len(recipients)

    return count + group_count*100 - group_count
    # return recipients # testing