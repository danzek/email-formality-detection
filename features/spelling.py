__author__ = ['Upasita', 'Sangmi']

import re
import os


def ratio_misspelled_words(email):
    """
    Finds common misspelled words based on "the top misspellings according to the Oxford English Corpus"
    (http://www.oxforddictionaries.com/words/common-misspellings)
    :param email:
    :return percentage of misspelling:
    """
    m_count = 0
    source = ""
    # remove special characters
    # e.g. '.', '?', '!', ' ', ';', ':', ','
    for line in email.enumerate_lines():
        source += line
    source = re.split('\W+', source)
    if len(source) == 0:
        return 0.0

    #testing
    # test = ['futher','goverment','jist','freind','foriegn']
    # for line in test:
    #     source += line + ' '
    # source = re.split('\W+', source)

    try:
        source.remove('')  # remove empty entries
    except:
        pass
    f = open(os.path.join(os.path.dirname(__file__), 'misspelling.txt'), 'r')  # list of common misspellings
    for misspell in f:
        for word in source:
            if misspell.lstrip().lower().replace('\n', '') == word.lstrip().lower():
                m_count += 1
    word_count = len(source) # number of total words
    if word_count == 0: # if empty email
        percentage = 0.0
    else:
        percentage = round(float(m_count) / word_count, 2)  # round it to 2 decimal places
    f.close()
    return percentage # returns the percentage of misspelling