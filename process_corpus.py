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
from features.simple_counts import average_syllables_per_word, character_count, syllable_count, word_count
from features.netlingo import find_netlingo


def process_features(email):
    classifier_to_write_to_file = ""
    feature_dictionary = {}  # stores human-readable names for each feature

    # determine classification; if unclassified then 0, if informal then 1, if formal then 2
    if email.classification == 'U':
        classifier_to_write_to_file = "0"
    elif email.classification == 'I':
        classifier_to_write_to_file = "1"
    elif email.classification == 'F':
        classifier_to_write_to_file = "2"

    # process each email with each feature, and add the id of the feature and a description of it to the
    # feature_dictionary
    print 'Processing email #' + str(email.id)

    feature_dictionary[0] = "Character Count"
    email.add_feature(0, character_count(email))

    feature_dictionary[1] = "Syllable Count"
    email.add_feature(1, syllable_count(email))

    feature_dictionary[2] = "Average # Syllables per Word"
    email.add_feature(2, average_syllables_per_word(email))

    feature_dictionary[3] = "Word Count"
    email.add_feature(3, word_count(email))

    feature_dictionary[4] = "Net Lingo Term Count"
    email.add_feature(4, find_netlingo(email))

    # new features go here

    return classifier_to_write_to_file


def main():
    with open('features.libsvm', 'w') as ff:
        c = Corpus()

        for email in c.fetch_all_emails():
            email.get_current_message()  # make sure only dealing with most recent message
            classifier_to_write_to_file = process_features(email)

            # write feature set for this sample to file
            ff.write(classifier_to_write_to_file)
            for f in email.feature_set.items():
                ff.write(" %s:%s" % f)

            ff.write(" # email id: " + str(email.id))  # add comment to libsvm file with unique id for sample
            ff.write("\n")  # new line for next sample


if __name__ == '__main__':
    main()