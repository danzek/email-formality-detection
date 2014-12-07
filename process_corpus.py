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


import csv
from data.models import Corpus
from features.bagofwords import extract_words_as_features
from features.simple_counts import average_syllables_per_word, character_count, syllable_count, word_count, \
    is_forward, is_reply, subject_line_counts, count_verbs
from features.netlingo import find_netlingo
from features.contractionFeature import contraction
from features.timeFeature import weekend, day, time
from features.closing import closing
from features.count_recipients import count_recipients
from features.capitalization import ratio_incorrect_first_capitalization, punctRatio, \
    incorrect_first_person_pronoun_capitalization_count, ratio_cap_letters, create_text_from_body
from features.spelling import ratio_misspelled_words


def populate_word_features(all=True):
    c = Corpus()
    all_word_features = []

    print 'Preprocessing unigram features...'

    if all:
        email_generator = c.fetch_all_emails()
    else:
        email_generator = c.fetch_all_emails(column='classification', query='classified')

    for email in email_generator:
        email.get_current_message()  # make sure only dealing with most recent message
        text = create_text_from_body(email)
        email_features = extract_words_as_features(text)
        all_word_features.extend(email_features)

    return all_word_features


def process_features(email, wf):
    classifier_to_write_to_file = ""
    feature_dictionary = {}  # stores human-readable names for each feature

    # determine classification; if unclassified then 2, if informal then 0, if formal then 1
    if email.classification == 'I':
        classifier_to_write_to_file = "0"
    elif email.classification == 'F':
        classifier_to_write_to_file = "1"
    elif email.classification == 'U':
        classifier_to_write_to_file = "2"

    # process each email with each feature, and add the id of the feature and a description of it to the
    # feature_dictionary
    print 'Processing email #' + str(email.id)
    i = 1

    feature_dictionary[i] = "Character Count"
    email.add_feature(i, character_count(email))
    i += 1

    feature_dictionary[i] = "Syllable Count"
    email.add_feature(i, syllable_count(email))
    i += 1

    feature_dictionary[i] = "Average # Syllables per Word"
    email.add_feature(i, average_syllables_per_word(email))
    i += 1

    feature_dictionary[i] = "Word Count"
    email.add_feature(i, word_count(email))
    i += 1

    feature_dictionary[i] = "Net Lingo Term Count"
    email.add_feature(i, find_netlingo(email))
    i += 1

    feature_dictionary[i] = "Contractions to All Words Ratio"
    email.add_feature(i, contraction(email))
    i += 1

    feature_dictionary[i] = "Weekend"
    email.add_feature(i, weekend(email))
    i += 1

    feature_dictionary[i] = "Day"
    email.add_feature(i, day(email))
    i += 1

    feature_dictionary[i] = "Time"
    email.add_feature(i, time(email))
    i += 1

    feature_dictionary[i] = "Closing Present"
    email.add_feature(i, closing(email))
    i += 1

    feature_dictionary[i] = "Recipients Count"
    email.add_feature(i, count_recipients(email))
    i += 1

    feature_dictionary[i] = "Ratio of Sentences Not Beginning With Capital Letters"
    email.add_feature(i, ratio_incorrect_first_capitalization(email))
    i += 1

    feature_dictionary[i] = "Ratio of Excessive Punctuation to Normal Punctuation"
    email.add_feature(i, punctRatio(email))
    i += 1

    feature_dictionary[i] = "Incorrect Capitalization of 'i' Count"
    email.add_feature(i, incorrect_first_person_pronoun_capitalization_count(email))
    i += 1

    feature_dictionary[i] = "Ratio of contiguous capital letters to total letters"
    email.add_feature(i, ratio_cap_letters(email))
    i += 1

    feature_dictionary[i] = "Ratio of misspelled words to total words"
    email.add_feature(i, ratio_misspelled_words(email))
    i += 1

    feature_dictionary[i] = "Is Forward?"
    email.add_feature(i, is_forward(email))
    i += 1

    feature_dictionary[i] = "Is Reply?"
    email.add_feature(i, is_reply(email))
    i += 1

    feature_dictionary[i] = "Subject Line Reply Count"
    email.add_feature(i, subject_line_counts(email, 'reply'))
    i += 1

    feature_dictionary[i] = "Subject Line Forward Count"
    email.add_feature(i, subject_line_counts(email, 'forward'))
    i += 1

    # feature_dictionary[i] = "Verb Count"
    # email.add_feature(i, count_verbs(email))
    # i += 1

    # word features (unigrams only)
    email_text = create_text_from_body(email)
    email_word_features = extract_words_as_features(email_text)
    for feature in wf:
        feature_dictionary[i] = feature
        if feature in email_word_features:
            fv = 1
        else:
            fv = 0
        email.add_feature(i, fv)
        i += 1

    return feature_dictionary, classifier_to_write_to_file


def write_libsvm_file(wf, all=True):
    with open('features.libsvm', 'w') as ff:
        c = Corpus()

        if all:
            email_generator = c.fetch_all_emails()
        else:
            email_generator = c.fetch_all_emails(column='classification', query='classified')

        for email in email_generator:
            email.get_current_message()  # make sure only dealing with most recent message
            feature_dictionary, classifier_to_write_to_file = process_features(email, wf)

            # write feature set for this sample to file
            string_builder = ""
            string_builder += classifier_to_write_to_file
            for f in email.feature_set.items():
                string_builder += " %s:%s" % f

            # ff.write(" # email id: " + str(email.id))  # add comment to libsvm file with unique id for sample
            try:
                ff.write(string_builder + '\n')
            except IOError:
                pass


def write_csv_file(wf, all=True):
    ff = open('features.csv', 'w')
    csv_writer = csv.writer(ff)
    c = Corpus()
    features = []

    if all:
        email_generator = c.fetch_all_emails()
    else:
        email_generator = c.fetch_all_emails(column='classification', query='classified')

    i = 0

    for email in email_generator:
        email.get_current_message()  # make sure only dealing with most recent message
        feature_dictionary, classifier_to_write_to_file = process_features(email, wf)
        if i == 0:
            tmp = ['Email ID#', 'Classification']
            tmp.extend(feature_dictionary.values())
            features.append(tmp)
        email_features = []
        email_features.append(email.id)
        email_features.append(classifier_to_write_to_file)
        email_features.extend(email.feature_set.values())
        features.append(email_features)
        i += 1

    csv_writer.writerows(features)


def main():
    all_word_features = populate_word_features(all=False)
    write_libsvm_file(all_word_features, all=False)
    write_csv_file(all_word_features, all=False)

if __name__ == '__main__':
    main()