email-formality-detection
=========================

Detect whether an email is formally or informally written. `data/prep_corpus.py` writes the emails to a SQLite
database. `process_corpus.py` creates a text file with extracted features in LibSVM format (for supervised machine
learning). `data/classifier_app` is a web application for simplifying manual classification of each email as being
either formal or informal.

This project uses the Enron email corpus, retrieved 
from [https://www.cs.cmu.edu/~./enron/](https://www.cs.cmu.edu/~./enron/). This is a group project for CNIT499NLT 
Natural Language Technologies at Purdue University. The course instructor is Dr. Julia Taylor. 

Group Members
-------------

 - Dan O'Day
 - Robert Hinh
 - Upasita Jain
 - Sangmi Shin
 - Penghao Wang

License
-------

[MIT](https://github.com/danzek/email-formality-detection/blob/master/LICENSE)
