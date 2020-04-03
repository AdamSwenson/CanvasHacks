"""
Created by adam on 3/16/20
"""
__author__ = 'adam'

import re

import pandas as pd

from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.GradingCorrections.penalities import HalfLate, NoLatePenalty
from CanvasHacks.GradingMethods.nonempty import CreditForNonEmptyOLD
from CanvasHacks.Models.QuizModels import QuizDataMixin, StoredDataFileMixin

if __name__ == '__main__':
    pass


class TopicalAssignment( Activity, QuizDataMixin, StoredDataFileMixin ):
    title_base = 'Topical assignment'
    instructions_filename = 'topical-assignment-instructions.txt'
    creation_type = 'quiz'

    regex = re.compile( r"\bwarm up\b" )

    # regex = re.compile( r"\btopical assignment\b" )

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self.grace_period = pd.Timedelta( '2 days' )

        self.corrections = [ ]

        # The objects which will be used to penalize late assignments
        self.penalizers = [  HalfLate( self.due_at, self.grace_period ) ]
        # The object which will be used to penalize late assignments
        # todo deprecated
        self.penalizer = self.penalizers[ 0 ]

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        # The object which will be used to assign the score
        self.grade_methods = [ CreditForNonEmptyOLD( min_words=2, count_stopwords=True ) ]
        self.grade_method = self.grade_methods[ 0 ]


class UnitEndSurvey( Activity ):
    """Representation of the survey at the end of each unit"""
    title_base = "Unit-end survey"
    instructions_filename = 'unit-end-survey-instructions.txt'
    regex = re.compile( r"\bunit-end survey\b" )
    creation_type = 'survey'

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )


        self.corrections = [ ]

        # The objects which will be used to penalize late assignments
        self.penalizers = [ NoLatePenalty(  ) ]
        # The object which will be used to penalize late assignments
        # todo deprecated
        self.penalizer = self.penalizers[ 0 ]

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        # The object which will be used to assign the score
        self.grade_methods = [ CreditForNonEmptyOLD( min_words=2, count_stopwords=True ) ]
        self.grade_method = self.grade_methods[ 0 ]
