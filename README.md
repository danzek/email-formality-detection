email-formality-detection
=========================

Predict whether an email is formally or informally written. `data/prep_corpus.py` writes the emails to a SQLite
database. `process_corpus.py` creates a text file with extracted features in LibSVM format (for supervised machine
learning). `data/classifier_app` is a web application for framework validation and simplifying manual classification 
of each email as either formal or informal. The app is currently live at [http://cnit499nlt.pythonanywhere.com](http://cnit499nlt.pythonanywhere.com).

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

Database
--------

The `mysql` branch is the main branch with all of the features and up-to-date code. However, the `master` branch uses sqlite rather than MySQL, and is thus easier to run and develop locally. Initial development took place with sqlite, but eventually moved to MySQL since that is the most efficient supported database type on PythonAnywhere hosting service.

How to Test A Single Feature
----------------------------

Begin inside the directory where you've extracted this project. Using an interactive Python shell (symbolized by `>>>` below&mdash;**do not retype the prompt symbols**), do the following:

    >>> from data.models import Corpus
    
Next import your feature(s):

    >>> from features.myfeaturefile import myfeature

Now instantiate the corpus and select a specific email by its ID number:

    >>> c = Corpus()
    >>> email_generator_object = c.fetch_all_emails(column="id", query="120000", exact_match=True)
    >>> email = next(email_generator_object)

Now you have the email object with the specified id. You can pass it to your previously imported feature by using the feature function name:

    >>> myfeature(email)

The feature should return the specified metric.
