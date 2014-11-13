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


from nltk.corpus import cmudict  # Carnegie Mellon Pronouncing Dictionary used for finding syllables


d = cmudict.dict()  # cmudict loaded once initially (for speed)


def average_syllables_per_word(email):
    try:
        count = syllable_count(email) / word_count(email)
    except ZeroDivisionError:
        count = 0  # no words or other error


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
        count += syllables[0]  # sometimes it returns more than one possible value, use first only
    except KeyError:  # word not found in dictionary or invalid input
        count += 1  # all words have at least one syllable (controversial, may be a non-word); perhaps just pass?
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