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


def main():
    c = Corpus()
    feature_dictionary = {}  # stores human-readable names for each feature
    classifier = ""

    with open('features.libsvm', 'w') as ff:
        for email in c.fetch_all_emails():
            error = False
            email.get_current_message()  # make sure only dealing with most recent message

            # TODO -- currently ignoring unclassified emails (only building training set), needs to be expanded
            # add classification as formal = 1 and informal = 0 for libsvm file (requires all numeric values)
            if email.classification == 'F':
                classifier = "1"
            elif email.classification == 'I':
                classifier = "0"
            else:
                print 'Error: Unclassified Email, Invalid Sample for Training Set'
                error = True

            if not error:
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

                # new features go here

                # write feature set for this sample to file
                ff.write(classifier)
                for f in email.feature_set.items():
                    ff.write(" %s:%s" % f)

                ff.write(" # email id: " + str(email.id))  # add comment to libsvm file with unique id for sample
                ff.write("\n")  # new line for next sample


if __name__ == '__main__':
    main()