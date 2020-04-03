"""
Created by adam on 3/16/20
"""
__author__ = 'adam'

import re

from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.Definitions.base import DiscussionType
from CanvasHacks.Definitions.groups import DiscussionGroup, ReviewType
from CanvasHacks.GradingCorrections.penalities import NoLatePenalty
from CanvasHacks.GradingMethods.nonempty import CreditForNonEmptyOLD
from CanvasHacks.Models.QuizModels import QuizDataMixin, StoredDataFileMixin

if __name__ == '__main__':
    pass


class DiscussionForum(Activity, DiscussionType,  DiscussionGroup,  StoredDataFileMixin ):
    """Representation of the main discussion forum"""
    title_base = "Main discussion"
    instructions_filename = 'discussion-forum-instructions.txt'
    regex = re.compile( r"\bforum\b" )
    creation_type = 'discussion'

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        # The objects which will be used to penalize late assignments
        self.penalizers = [NoLatePenalty()]

        self.corrections = []

        # The object which will be used to penalize late assignments
        # todo deprecated
        # self.penalizer = self.penalizers[0]

        # The object which will be used to assign the score
        self.grade_methods = [CreditForNonEmptyOLD( min_words=2, count_stopwords=True )]
        # self.grade_method = self.grade_method[0]

        try:
            # todo deprecated
            self.penalizer = self.penalizers[ 0 ]
            self.grade_method = self.grade_methods[ 0 ]
        except AttributeError as e:
            print(e)

    def create_on_canvas( self, course ):
        course.create_quiz()

    @property
    def topic_id( self ):
        try:
            return self.discussion_topic[ 'id' ]
        except KeyError:
            print( "No topic id set on discussion " )


class DiscussionReview( Activity, DiscussionType,  ReviewType, DiscussionGroup, QuizDataMixin, StoredDataFileMixin ):
    """Representation of the peer review of the main discussion forum"""
    title_base = "Discussion review"
    instructions_filename = 'discussion-review-instructions.txt'
    regex = re.compile( r"\bdiscussion review\b" )
    creation_type = 'survey'

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self.email_intro = "Here are the discussion forum posts from another student for you to review:"

        self.corrections = [ ]

        # The objects which will be used to penalize late assignments
        self.penalizers = [ NoLatePenalty() ]

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

    @property
    def email_subject( self ):
        """Since unit number will be set after initialization
        we need to do this as a property"""
        return "Unit {} peer-review of discussion forum posts".format( self.unit_number )