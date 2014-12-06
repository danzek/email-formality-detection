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

Simple count features.
"""

__author__ = "Dan O'Day, Sangmi Shin, Robert Hinh"
__copyright__ = "Copyright 2014, Dan O'Day, Purdue University"
__credits__ = ["Dan O'Day", "Robert Hinh", "Upasita Jain", "Sangmi Shin", "Penghao Wang", "Julia Taylor"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Dan O'Day"
__email__ = "doday@purdue.edu"
__status__ = "Development"


import re
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
punkt_param = PunktParameters()
punkt_param.abbrev_types = set(['dr', 'vs', 'mr', 'mrs', 'ms', 'prof', 'inc', 'viz', 'cf'])


def clean_up(sentences):
    """
    The PunktSentenceTokenizer from NLTK incorrectly handles initial collocations such as 'e.g.' and 'i.e.'. There is a
    PunktParameter for collocations, but it takes tuples containing the collocated initial word and words commonly
    following it, which it learns from training data. For simplicity's sake, this method merely does a simple pattern
    match on the named initial collocations and concatenates the sentences improperly divided by these.
    """
    i = 0
    indexes_to_concatenate = []
    cleaned_up_sentence_list = []

    for s in sentences:
        if s.lower().endswith('e.g.') or s.lower().endswith('i.e.') or s.lower().endswith('p.s.') \
                or s.lower().endswith('f.y.i.') or s.lower().endswith('m.s.') or s.lower().endswith('b.s.'):
            indexes_to_concatenate.append(i)
        i += 1

    i = 0  # re-initialize index

    if len(indexes_to_concatenate) > 0:
        while i < len(sentences):
            if i in indexes_to_concatenate:
                new_sentence = sentences[i] + ' ' + sentences[i+1]
                cleaned_up_sentence_list.append(new_sentence)
                i += 2
            else:
                cleaned_up_sentence_list.append(sentences[i])
                i += 1
    else:
        return sentences

    return cleaned_up_sentence_list


def count_sentences(email):
    """Returns total number of sentences in email body."""
    return len(prepare_email(email))


def create_text_from_body(email):
    """Converts email body list object into string."""
    text = ""
    for line in email.enumerate_lines():
        text += line + ' '
    return text


def prepare_email(email):
    """Handles email object and returns list of sentences so that only one method must be used."""
    text = create_text_from_body(email)
    return split_sentences(text)


def punctuation(email):
    listOutput = prepare_email(email)

    punctFilter = re.compile("[\!?]{2,}")
    exFilter = re.compile("[\!]{2,}")
    quesFilter = re.compile("[\?]{2,}")
    periodFilter = re.compile("[\.]{4,}")
    punct_count = 0

    for i in listOutput:
        if re.search(punctFilter, i) or re.search(periodFilter, i) or re.search(exFilter, i) or re.search(quesFilter, i):
            punct_count += 1

    return punct_count


def punctRatio(email):
    listOutput = prepare_email(email)

    punct_count = punctuation(email)
    sentence_count = len(listOutput)

    try:
        punct_Ratio = "%.1f" % ((float(punct_count) / sentence_count) * 100)
    except ZeroDivisionError:
        punct_Ratio = 0.0

    return punct_Ratio


def ratio_incorrect_first_capitalization(email):
    """
    :param email:
    :return ratio of sentences start with incorrect capitalization:
    """
    sent_list = prepare_email(email)  # returns the list of sentences
    not_cap = 0
    for sent in sent_list:
        # if the first word of the sentence is in lower case
        if sent[0].isalpha() is True and sent[0].islower() is True:
            not_cap += 1
    count = count_sentences(email)  # number of total sentences in an email
    if count == 0:  # if it is an empty email
        percentage = 0.00
    else:
        percentage = round(float(not_cap)/count_sentences(email), 2) # round it to 2 decimal places
    return percentage


def split_sentences(text):
    """Takes string containing email body and splits into sentences and cleans up list."""
    sentence_splitter = PunktSentenceTokenizer(punkt_param)
    sentences = sentence_splitter.tokenize(text)
    return clean_up(sentences)