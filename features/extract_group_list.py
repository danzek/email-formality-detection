# extract_group_list.py
# created on:       Dec. 2, 2014
# last updated on : Dec. 3, 2014
__author__ = 'Sangmi'

from data.models import Corpus


def total_list():

    """
    extracts recipients from email headers
    creates: recipient_list_set.txt (whole recipient list)
    :return: a set of total recipients
    """
    c = Corpus()
    try:
        f2 = open('recipient_list_set.txt', 'r')
    except IOError:
        f2 = open('recipient_list_set.txt', 'a')
        r_set = set() # recipient set
        for i in range (1,490682): # id from 1 to 490682
            el = c.fetch_all_emails(column="id", query=i, exact_match=True)
            e = next(el)
            this_re = set(e.recipient.replace('\r\n', '').replace('\n', '').split(',')) # split multiple email addresses
            r_set = r_set.union(this_re) # union operation with the previous recipient set

        file_list="" # list container to print out the set
        for r in r_set:
            file_list += r.lstrip() + "\n"
        f2.write(file_list)
        f2.close()


def group_list():
    """
    Enron email uses group emails in forms of "all.*@enron.com"
    group_list() extracts group email addresses among the whole recipient list that starts with 'all.' or 'enron.'
    creates recipient_group_list.txt (group recipient list)
    :return: a set of group recipients (type: set)
    """
    try:
        f4 = open('recipient_group_list.txt','r') # text file of group emailing list
        group_set = set()
        for line in f4:
            if line is not '\n' or line is not '\r\n':
                group_set.add(line.replace('\r\n', '').lstrip().replace('\n', ''))
        try:
            group_set.remove('')
        except KeyError:
            pass
        f4.close()
    except IOError:
        try:
            f3 = open('recipient_list_set.txt','r')
        except IOError:
            total_list() # creates recipient_list_set.txt
            f3 = open('recipient_list_set.txt','r')
        group_set = set()
        for line in f3:
            if line.startswith('all.') or line.startswith('enron.'):
                if line.replace('\r\n', '').replace('\n', '').lstrip().endswith('@enron.com'):
                    group_set.add(line.replace('\r\n', '').replace('\n', ''))
        f3.close()
        try:
            group_set.remove('')
        except KeyError:
            pass
        f4 = open('recipient_group_list.txt','a')
        for g in group_set:
            f4.write(g + '\n')
        f4.close()

    return group_set