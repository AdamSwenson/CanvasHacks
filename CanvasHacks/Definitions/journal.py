"""
Created by adam on 3/16/20
"""
__author__ = 'adam'

import re

import pandas as pd

from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.GradingCorrections.penalities import HalfLate
from CanvasHacks.GradingMethods.nonempty import CreditForNonEmptyOLD

if __name__ == '__main__':
    pass


class Journal( Activity ):
    """Representation of a journal unit.
    Not related to assignments within a Unit
    """
    title_base = "Journal"

    regex = re.compile( r"\bjournal\b" )
    creation_type = 'assignment'

    def __init__( self, **kwargs ):
        self.grace_period = pd.Timedelta( '2 days' )
        super().__init__( **kwargs )

        self.corrections = [ ]

        # The objects which will be used to penalize late assignments
        self.penalizers = [HalfLate( self.due_at, self.grace_period )]
        # The object which will be used to penalize late assignments
        # todo deprecated
        self.penalizer = self.penalizers[ 0 ]

        # The object which will be used to assign the score
        # NB, min_words is 1 for now so as to not create problems with multiple-choice answers
        # This could be fixed in CAN-57
        # The object which will be used to assign the score
        self.grade_methods = [ CreditForNonEmptyOLD( min_words=2, count_stopwords=True ) ]
        self.grade_method = self.grade_methods[ 0 ]

