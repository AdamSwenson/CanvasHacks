"""
Created by adam on 4/6/20
"""
__author__ = 'adam'

from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.GradingCorrections.penalities import NoLatePenalty
from CanvasHacks.GradingMethods.nonempty import CreditForNonEmptyOLD

if __name__ == '__main__':
    pass


class GenericCreditNoCredit( Activity ):
    """Representation of a generic assignment which is graded credit / no credit
    with no late penalties
    Not related to assignments within a Unit
    """
    creation_type = 'assignment'

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        self.corrections = [ ]

        # The objects which will be used to penalize late assignments
        self.penalizers = [NoLatePenalty(  )]
        # The object which will be used to penalize late assignments
        # todo deprecated
        self.penalizer = self.penalizers[ 0 ]

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        # The object which will be used to assign the score
        self.grade_methods = [ CreditForNonEmptyOLD( min_words=2, count_stopwords=True ) ]
        self.grade_method = self.grade_methods[ 0 ]

