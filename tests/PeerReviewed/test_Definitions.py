"""
Created by adam on 12/24/19
"""
from unittest import TestCase

from CanvasHacks.PeerReviewed.Definitions import Activity
from CanvasHacks.PeerReviewed.PeerReviewTools import *
from tests.factories.PeerReviewedFactories import *

__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestActivity( TestCase ):
    # def test_assignable_points( self ):
    #     self.fail()

    def test_check_date( self ):
        # is date case
        self.assertIsInstance( Activity._check_date( pd.to_datetime( '2019-01-06' ) ), pd.Timestamp )
        # string case
        self.assertIsInstance( Activity._check_date( '2019-01-06' ), pd.Timestamp )

    def test_instantiates_properly( self ):
        test_data = test_data_factory()
        obj = Activity( **test_data[ 'initial' ] )
        self.assertIsInstance( obj.due_date, pd.Timestamp, "due date is timestamp" )
        self.assertIsInstance( obj.open_date, pd.Timestamp, "open date is timestamp" )
        pts = test_data[ 'initial' ][ 'max_points' ] - test_data[ 'initial' ][ 'completion_points' ]
        self.assertEqual( obj.assignable_points, pts, 'assignable points correctly calculated' )


class TestAssignment( TestCase ):
    def setUp( self ):
        self.test_data = test_data_factory()
        # Create the assignment
        self.initial = InitialWork( **self.test_data[ 'initial' ] )
        self.review = Review( **self.test_data[ 'review' ] )
        self.meta = MetaReview( **self.test_data[ 'metareview' ] )
        self.obj = Assignment( self.initial, self.review, self.meta )

    def test_setup( self ):
        # Create the assignment
        initial = InitialWork( **self.test_data[ 'initial' ] )
        review = Review( **self.test_data[ 'review' ] )
        meta = MetaReview( **self.test_data[ 'metareview' ] )
        obj = Assignment( initial, review, meta )

        self.assertIsInstance( obj.review, Review )
