"""
Objects which define the parameters/ values for the entire assignment

Created by adam on 12/24/19
"""
import pandas as pd

__author__ = 'adam'

if __name__ == '__main__':
    pass

from CanvasHacks.Models.IModel import StoreMixin


class Activity( StoreMixin ):
    """A component of the assignment.
    NOT SPECIFIC TO ANY GIVEN STUDENT
    """

    def __init__( self, open_date, due_date, completion_points=0, max_points=0, **kwargs ):
        """
        open_date: The date that the review could begin reviewing
        due_date: The date by which the reviewer must complete the review
        completion_date: The date at which the student submitted the thing
        """
        self.id = None
        self.max_points = max_points
        # The points received for just turning in the activity non-empty
        self.completion_points = completion_points

        self.due_date = type( self )._check_date( due_date )
        self.open_date = type( self )._check_date( open_date )

    @property
    def assignable_points( self ):
        """How many points are assigned by the reviewer"""
        return self.max_points - self.completion_points

    @staticmethod
    def _check_date( date ):
        """Checks that a value is a pd.Timestamp
        if not, it tries to make it into one"""
        return date if isinstance( date, pd.Timestamp ) else pd.to_datetime( date )


class InitialWork( Activity ):

    def __init__( self, open_date, due_date, completion_points, max_points, **kwargs ):
        super().__init__(  open_date, due_date, completion_points, max_points, **kwargs )


class Review( Activity ):
    """Representation of the peer review component of the
     assignment """

    def __init__( self, open_date, due_date, completion_points, max_points, **kwargs ):
        """
        :param open_date: The date that the review could begin reviewing
        :param due_date: The date by which the reviewer must complete the review
        """
        super().__init__( open_date, due_date, completion_points, max_points, **kwargs )


class MetaReview( Activity ):
    """The review review"""
    """Representation of the peer review of 
    another student's submission"""

    def __init__( self, open_date, due_date, completion_points, max_points, **kwargs ):
        """
        :param open_date: The date that the review could begin reviewing
        :param due_date: The date by which the reviewer must complete the review
        """
        # we use the same values for both completion pints and max points
        # since there are no assignable points
        super().__init__( open_date, due_date, completion_points, max_points, **kwargs )


class Assignment( StoreMixin ):
    """Defines all constant values for the assignment"""

    def __init__( self, initial_work: InitialWork, review: Review, meta_review: MetaReview, **kwargs ):
        """
        :param initial_work:
        :param review:
        :param meta_review:
        """
        self.initial_work = initial_work
        self.meta_review = meta_review
        self.review = review

        self.handle_kwargs( kwargs )
