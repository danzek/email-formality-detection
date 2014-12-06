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
Time feature
"""
__author__ = "Robert Hinh"
__copyright__ = "Copyright 2014, Dan O'Day, Purdue University"
__credits__ = ["Dan O'Day", "Robert Hinh", "Upasita Jain", "Sangmi Shin", "Penghao Wang", "Julia Taylor"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Dan O'Day"
__email__ = "doday@purdue.edu"
__status__ = "Development"

# importing the libraries
import re
from simple_counts import word_count


# Counting the percentage of contractions relative to body count
def contraction(email):
    data = []

    for word in email.enumerate_words():
        data.append(word.lower())
    # this might change - but the idea is to convert the body of the email message into a list with each element
    # representing one word
    #data = list(data.split(' '))

    # using regex to capture time apostrophes in each word
    # the regex pattern - NOTE DAN, if you find another type of apostrophe, just stick it in anywhere in the square
    # brackets after the forward slash. It'll standardize it later
    apostropheCapture = re.compile("[\‘′’ʻ’ʼ'ʹ]{1}")
    contraction_count = 0

    # regex capture for each word
    for word in data:
        # search through each word and find the ones with the apostrophe and then standardize the apostrophe to '
        #apostrophe.append(list(apostropheCapture.findall(word)))
        #apostrophe = map(lambda i: re.sub(apostropheCapture, "'", apostrophe), apostrophe)
        word = re.sub(r"[\‘′’ʻ’ʼ'ʹ]{1}", "'", word)
        word = re.sub(r"[\']+", "'", word)  # janky, but fixes getting too many contiguous apostrophes

        # filtering each element in the list to find words with the apostrophe
        # NOTE - in the English language, double (and hell, even triple) contractions exist. But no matter how many
        # contraction parts are present in a word, that would just increase the contraction_count by 1
        if word.endswith("'t"):
            contraction_count += 1
        elif word.endswith("'ve"):
            contraction_count += 1
        elif word.endswith("'d"):
            contraction_count += 1
        elif word.endswith("'ll"):
            contraction_count += 1
        elif word.endswith("'s"):
            contraction_count += 1
        elif word.endswith("'m"):
            contraction_count += 1
        elif word.endswith("'am"):
            contraction_count += 1
        elif word.endswith("'re"):
            contraction_count += 1
        elif word.endswith("'all"):
            contraction_count += 1

    # obtaining the total number of words in the msg
    # UNTESTED - use simple_counts.py
    total_msg_count = word_count(email)

    # percentage - the result
    contraction = "%.2f" % ((float(contraction_count) / total_msg_count) * 100)

    return contraction


"""
#word.endswith()
broken_word = list(word)
all_apostrophes = [i for i, x in enumerate(broken_word) if x == "'"]
if (len(all_apostrophes) == 1):
    #if there's only one position of the apostrophe, then it should be the first in the list
    apostrophe_position = all_apostrophes[0]
    position_of_last_letter = (len(broken_word))
    
    #the letters from the apostrophe until the end
    end_part = word[apostrophe_position+1:position_of_last_letter]
    
    if end
    
    print(end_part)
    print(apostrophe_position)
    print(position_of_last_letter)
    print(type(position_of_last_letter))
else:
    pass
    #doubleContraction()
 """