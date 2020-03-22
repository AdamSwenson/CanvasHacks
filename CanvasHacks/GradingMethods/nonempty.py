"""
Created by adam on 1/29/19
"""
__author__ = 'adam'

from CanvasHacks.Errors.grading import NonStringInContentField
from CanvasHacks.GradingAnalyzers.nonempty import NonEmpty
from CanvasHacks.GradingMethods.base import IGradingMethod
from CanvasHacks.Text.process import make_wordbag
from nltk.corpus import stopwords
import string
from CanvasHacks.GradingCorrections.penalities import get_penalty
from CanvasHacks.Text.stats import WordCount


class CreditForNonEmptyOLD( IGradingMethod ):
    """Returns full credit for a literally non-empty answer"""

    def __init__(self, min_words=2, count_stopwords=True):
        # self.score = 100
        # params
        self.min_words = min_words
        self.count_stopwords = count_stopwords

        # The object which will handle the actual processing and computation
        self.analyzer = NonEmpty
        # self.analyzer = WordCount(count_stopwords=count_stopwords)

    def grade( self, content, **kwargs ):
        """Returns the pct credit as an integer"""
        # Aliasing the pct int to leave room for
        # alternative output could go here

        return self.grade_pct_int(content, **kwargs)

    def grade_pct_int( self, content, on_credit=100, on_no_credit=None ):
        """Returns the pct credit as an integer
        Returns None if not getting any credit, which can be overridden
        by the value in on_no_credit
        """
        return on_credit if self.analyzer.analyze(content) else on_no_credit

        # if content is not None:
        #     if isinstance(content, (int, float)):
        #         return on_credit
        #
        #     if len(content) >0:
        #         return on_credit
        #
        # return on_no_credit

        # too processor intensive and duplicative
        # word_count = self.analyzer.analyze(content)
        # credit = word_count >= self.min_words
        #
        # # credit = receives_credit(content, self.min_words, self.count_stopwords)
        # if credit:
        #     return on_credit
        # elif on_no_credit is not None:
        #     return on_no_credit




class CreditForNonEmpty( IGradingMethod ):
    """Returns full credit for a literally non-empty answer"""

    def __init__(self, pct_of_score=1):
        # self.score = 100
        # params
        self.pct_of_score = pct_of_score

        # The object which will handle the actual processing and computation
        self.analyzer = NonEmpty
        # self.analyzer = WordCount(count_stopwords=count_stopwords)

    def grade( self, content, **kwargs ):
        """Returns the pct creditr"""
        return self.pct_of_score if self.analyzer.analyze(content) else 0

        # Aliasing the pct int to leave room for
        # alternative output could go here

        # return self.grade_pct_int(content, **kwargs)

    def grade_pct_int( self, content, on_credit=100, on_no_credit=None ):
        """Returns the pct credit as an integer
        Returns None if not getting any credit, which can be overridden
        by the value in on_no_credit
        """
        return on_credit if self.analyzer.analyze(content) else on_no_credit


# --------------------------- old

def receives_credit( content: str, min_words=2, count_stopwords=True ):
    """
    Given a piece of text written by a student, determines
    whether to assign credit or no credit

    :param content: The text to analyze
    :param min_words: The minimum word count to give credit for
    :param count_stopwords: Whether stopwords should count toward word count
    :return: Boolean
    """
    if not isinstance(content, str):
        raise NonStringInContentField
    remove = [ '``', "''", "'s"]
    remove += string.punctuation
    if not count_stopwords:
        remove += stopwords.words('english')
    remove = set(remove)
    bag = make_wordbag(content, remove)
    return len(bag) >= min_words


def scored_non_empty(content, max_score, on_empty=None):
    """
    Returns a dictionary with key 'score'
    :param content:
    :param max_score:
    :param on_empty: If none, will return no value if empty.
    :return:
    """
    if receives_credit( content ):
        return { 'score': max_score }
    else:
        if on_empty is not None:
            { 'score': on_empty }

        # questions[ qid ] = { 'score': 4.0 }
        # total_score += 4

def determine_credit(submissions):
    """
    OLD
    Adds submissions of zero length to the no-credit list.
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
    """
    OLD
    Determines how much credit potentially late credit/no credit
    assignments should recieve.
    Created in CAN-24; moved into JournalGrader in CAN-40
    """
    results = []
    for submission in submissionRepo.data:
        if submission.body is not None:
            credit = receives_credit( submission.body )
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



if __name__ == '__main__':
    pass