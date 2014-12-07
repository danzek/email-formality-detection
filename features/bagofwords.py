__author__ = 'danoday'


import string
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures


"""
# this extracted unigrams and bigrams but created too large of a sample file with bigrams
def extract_words_as_features(text):
    # extract words
    text = text.replace('\n', ' ').replace('\r', '')
    text = text.translate(string.maketrans("",""), string.punctuation)  # eliminates punctuation
    tokenizer = WordPunctTokenizer()
    tokens = tokenizer.tokenize(text)

    # extract bigrams
    bigram_finder = BigramCollocationFinder.from_words(tokens)
    bigrams = bigram_finder.nbest(BigramAssocMeasures.chi_sq, 500)

    for bigram_tuple in bigrams:
        x = "%s %s" % bigram_tuple
        tokens.append(x)

    unigram_and_bigram_set = set([x.lower() for x in tokens if x not in stopwords.words('english') and len(x) > 2])
    return list(unigram_and_bigram_set)
"""


def extract_words_as_features(text):
    # extract ONLY unigrams
    text = text.replace('\n', ' ').replace('\r', '')
    text = text.translate(string.maketrans("",""), string.punctuation)  # eliminates punctuation
    tokenizer = WordPunctTokenizer()
    tokens = tokenizer.tokenize(text)
    unigrams = set([x.lower() for x in tokens if x not in stopwords.words('english') and len(x) > 2])
    return list(unigrams)