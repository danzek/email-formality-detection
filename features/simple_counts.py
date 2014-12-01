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

__author__ = "Dan O'Day"
__copyright__ = "Copyright 2014, Dan O'Day, Purdue University"
__credits__ = ["Dan O'Day", "Robert Hinh", "Upasita Jain", "Sangmi Shin", "Penghao Wang", "Julia Taylor"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Dan O'Day"
__email__ = "doday@purdue.edu"
__status__ = "Development"


from nltk import word_tokenize, pos_tag
from nltk.corpus import cmudict  # Carnegie Mellon Pronouncing Dictionary used for finding syllables


d = cmudict.dict()  # cmudict loaded once initially (for speed)


def average_syllables_per_word(email):
    try:
        count = float("{0:.2f}".format((float(syllable_count(email)) / word_count(email))*100))
    except ZeroDivisionError:
        count = 0  # no words or other error
    return count


def character_count(email):
    count = 0
    for word in email.enumerate_words():
        for char in word:
            count += 1
    return count


def count_syllables(word):
    count = 0
    syllables = []
    try:
        syllables.append([len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]])  # returns list
        try:
            count += syllables[0]  # sometimes it returns more than one possible value, use first only
        except TypeError:
            pass  # not a word
    except KeyError:  # word not found in dictionary or invalid input
        count += 1  # all words have at least one syllable (controversial, may be a non-word); perhaps just pass?
    return count


def count_verbs(email):
    count = 0
    s = ''
    for line in email.enumerate_lines():
        s += line
    tagged_text = pos_tag(word_tokenize(s))
    for word, tag in tagged_text:
        if tag.startswith('VB'):
            count +=1
    return count

def syllable_count(email):
    count = 0
    for word in email.enumerate_words():
        count += count_syllables(word)
    return count


def word_count(email):
    count = 0
    for word in email.enumerate_words():
        count +=1
    return count