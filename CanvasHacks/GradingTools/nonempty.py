"""
Created by adam on 1/29/19
"""
__author__ = 'adam'

from CanvasHacks.TextProcessing import make_wordbag
from nltk.corpus import stopwords
import string
from CanvasHacks.GradingTools.quiz import get_penalty


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


def new_determine_journal_credit(activity, submissionRepo):
    """Determines how much credit potentially late credit/no credit
    assignments should recieve.
    Created in CAN-24
    """
    results = []
    for submission in submissionRepo.data:
        if submission.body is not None:
            credit = grade_credit_no_credit(submission.body)
            if credit:
                score = 100
            # Now check whether need to penalize for lateness
            penalty = get_penalty(submission.submitted_at, activity.due_at, activity.lock_at, activity.grace_period)
            # penalty was set up for uploading where have to use fudge points.
            # so we need to interpret it a bit here.
            # It will have returned 0 for no penalty and .5 for half credit
            penalty = 100 * penalty
            score = score - penalty
            results.append( (submission, int(score) ) )
    return results


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