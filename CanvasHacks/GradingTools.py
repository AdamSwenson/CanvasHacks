"""
Created by adam on 1/29/19
"""
__author__ = 'adam'

from CanvasHacks.TextProcessing import make_wordbag
import nltk
from nltk.corpus import stopwords
import string


def determine_credit(submissions):
    """Adds submissions of zero length to the no-credit list.
    Adds others to the credit list.
    Returns a dictionary with keys credit and nocredit, with the lists as values
    """
    credit = []
    nocredit = []

    for s in submissions:
        if 'body' in s.keys() and s['body'] is not None and len(s['body']) > 2:
            credit.append(s['student_id'])
        else:
            nocredit.append(s['student_id'])

    return {'credit': credit, 'nocredit': nocredit}


def grade_credit_no_credit( content: str, min_words=2, count_stopwords=True ):
    """
    Given a piece of text written by a student, determines
    whether to assign credit or no credit

    :param content: The text to analyze
    :param min_words: The minimum word count to give credit for
    :param count_stopwords: Whether stopwords should count toward word count
    :return: Boolean
    """
    remove = [ '``', "''", "'s"]
    remove += string.punctuation
    if not count_stopwords:
        remove += stopwords.words('english')
    remove = set(remove)
    bag = make_wordbag(content, remove)
    return len(bag) >= min_words





if __name__ == '__main__':
    pass