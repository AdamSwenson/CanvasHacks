"""
Objects which define the parameters/ values for the entire unit

Created by adam on 12/24/19
"""
from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.Definitions.base import BlockableActivity
from CanvasHacks.Definitions.groups import SkaaReviewGroup, ReviewType
from CanvasHacks.GradingCorrections.penalities import HalfLate, NoLatePenalty
from CanvasHacks.GradingMethods.nonempty import CreditForNonEmptyOLD

__author__ = 'adam'

import re

import pandas as pd
from CanvasHacks.Models.QuizModels import StoredDataFileMixin, QuizDataMixin

if __name__ == '__main__':
    pass


class InitialWork( SkaaReviewGroup, Activity, QuizDataMixin, StoredDataFileMixin ):
    title_base = "Essay"

    # title_base = "Content assignment"
    instructions_filename = 'content-assignment-instructions.txt'
    creation_type = 'assignment'

    # regex = re.compile( r"\bcontent assignment\b" )
    regex = re.compile( r"\bessay\b|\bcontent assignment\b" )

    def __init__( self, **kwargs ):
        self.question_columns = [ ]
        super().__init__( **kwargs )

        # Code for accessing the subsequent unit
        self.access_code_for_next_on = Review
        self.access_code_for_next = None

        # Tools which handle the grade
        self.grace_period = pd.Timedelta( '2 days' )

        self.corrections = [ ]

        # The objects which will be used to penalize late assignments
        self.penalizers = [ HalfLate( self.due_at, self.grace_period ) ]
        # The object which will be used to penalize late assignments

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        # The object which will be used to assign the score
        self.grade_methods = [ CreditForNonEmptyOLD( min_words=2, count_stopwords=True ) ]

        try:
            # todo deprecated
            self.penalizer = self.penalizers[ 0 ]
            self.grade_method = self.grade_methods[ 0 ]
        except AttributeError as e:
            print(e)
        #
        # self.composition
        #     (NonEmpty, 0.25),
        #     (WordCount, 0.50),
        #     (ReviewBased, 0.25)
        #
        # ]


class Review( SkaaReviewGroup, Activity, QuizDataMixin, StoredDataFileMixin, ReviewType ):
    """Representation of the peer review component of the
     unit """
    title_base = "Peer review"
    instructions_filename = 'peer-review-instructions.txt'
    creation_type = 'survey'

    regex = re.compile( r"\bpeer review\b" )

    def __init__( self, **kwargs ):
        # Code used to open the review unit
        self.access_code = None

        # todo access_code_for_next_on probably not needed; created without looking at what already have
        self.access_code_for_next_on = MetaReview
        self.access_code_for_next = None

        # Link to the activity_inviting_to_complete on canvas so students can click
        # directly to it
        self.activity_link = None

        self.corrections = [ ]

        # The objects which will be used to penalize late assignments
        self.penalizers = [ NoLatePenalty() ]
        # The object which will be used to penalize late assignments
        # todo deprecated
        # self.penalizer = self.penalizers[ 0 ]

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        # The object which will be used to assign the score
        self.grade_methods = [ CreditForNonEmptyOLD( min_words=2, count_stopwords=True ) ]
        # self.grade_method = self.grade_methods[ 0 ]

        try:
            # todo deprecated
            self.penalizer = self.penalizers[ 0 ]
            self.grade_method = self.grade_methods[ 0 ]
        except AttributeError as e:
            print(e)

        super().__init__( **kwargs )
        self.email_intro = "Here is another student's assignment for you to review:"

    @property
    def email_subject( self ):
        """Since unit number will be set after initialization
        we need to do this as a property"""
        return "Unit {} peer-review of content unit".format( self.unit_number )


class MetaReview( SkaaReviewGroup, Activity, BlockableActivity, QuizDataMixin, StoredDataFileMixin, ReviewType ):
    """Representation of the peer review of
    another student's submission"""
    title_base = "Metareview"
    instructions_filename = 'metareview-instructions.txt'
    access_code_for_next_on = None
    creation_type = 'survey'

    regex = re.compile( r"\bmetareview\b" )

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        self.email_intro = "Here is the feedback on your assignment:"

        self.corrections = [ ]

        # The objects which will be used to penalize late assignments
        self.penalizers = [ NoLatePenalty() ]
        # The object which will be used to penalize late assignments
        # todo deprecated
        # self.penalizer = self.penalizers[ 0 ]

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        # The object which will be used to assign the score
        self.grade_methods = [ CreditForNonEmptyOLD( min_words=2, count_stopwords=True ) ]
        # self.grade_method = self.grade_methods[ 0 ]

        try:
            # todo deprecated
            self.penalizer = self.penalizers[ 0 ]
            self.grade_method = self.grade_methods[ 0 ]
        except AttributeError as e:
            print(e)

    @property
    def email_subject( self ):
        """Since unit number will be set after initialization
        we need to do this as a property"""
        return "Unit {} metareview of peer-review".format( self.unit_number )

# class Assignment( StoreMixin ):
#     """Defines all constant values for the unit"""
#
#     def __init__( self, initial_work: InitialWork, review: Review, meta_review: MetaReview, **kwargs ):
#         """
#         :param initial_work:
#         :param review:
#         :param meta_review:
#         """
#         self.initial_work = initial_work
#         self.meta_review = meta_review
#         self.review = review
#
#         self.handle_kwargs( kwargs )
