"""
Created by adam on 12/24/19
"""
import pandas as pd
from unittest import TestCase
from tests.factories.PeerReviewedFactories import test_data_factory, unit_factory
from CanvasHacks.Models.model import Model
from CanvasHacks.Definitions.skaa import InitialWork, Review, MetaReview
from CanvasHacks.Definitions.journal import Journal
from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.Definitions.unit import Unit

__author__ = 'adam'

if __name__ == '__main__':
    pass


class DummyAssignment( Model ):
    def __init__( self, **kwargs ):
        self.attributes = { }
        super().__init__( **kwargs )

        for key, value in kwargs.items():
            self.attributes[ key ] = value


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
        self.assertIsInstance( obj.due_at, pd.Timestamp, "due date is timestamp" )
        self.assertIsInstance( obj.open_at, pd.Timestamp, "open date is timestamp" )
        pts = test_data[ 'initial' ][ 'max_points' ] - test_data[ 'initial' ][ 'completion_points' ]
        self.assertEqual( obj.assignable_points, pts, 'assignable points correctly calculated' )


class TestUnit( TestCase ):
    def setUp( self ):
        self.obj = Unit( { }, 1 )

    def test_find_for_unit( self ):
        good = [ DummyAssignment( name="tacos are unit 1 best" ), DummyAssignment( name="Unit 1" ),
                 DummyAssignment( name='tacos are UNIT 1 best' ) ]
        bad = [ DummyAssignment( name="tacos are best" ), DummyAssignment( name="Unit 2" ),
                DummyAssignment( name="unit 10" ), DummyAssignment( name="tacos are UNIT" ) ]
        tests = good + bad
        results = self.obj.find_for_unit( 1, tests )
        self.assertTrue( len( results ) == len( good ) )
        # for r in results:
        #     self.assertIn( r, good )

    def test_find_components( self ):
        # assigns = []
        # vs = ['Unit 1 Content unit','Unit 1 metareview''Unit 1 review']
        # for v in vs:
        #     a = canvasapi.unit.Assignment()
        #     a.name = v
        #     assigns.append(a)
        assigns = [ DummyAssignment( name='Unit 1 Essay', id=5, due_at= pd.to_datetime( '2019-01-06' ) ),
                    DummyAssignment( name='Unit 1 metareview', id=4, due_at= pd.to_datetime( '2019-01-06' ) ),
                    DummyAssignment( name='Unit 1 peer review', id=3, due_at= pd.to_datetime( '2019-01-06' ) )
                    ]
        self.obj.find_components( assigns )
        self.assertEqual( len( self.obj.components ), 3 )

    def test__set_access_code_for_next( self ):
        unit = unit_factory()
        for c in unit.components:
            unit._set_access_code_for_next(c)

        # check
        self.assertEqual(unit.initial_work.access_code_for_next, unit.review.access_code)
        self.assertEqual(unit.review.access_code_for_next, unit.metareview.access_code)


class TestInitialWork( TestCase ):
    def setUp( self ):
        self.test_data = test_data_factory()
        # Create the unit
        # self.initial = InitialWork( **self.test_data[ 'initial' ] )
        # self.review = Review( **self.test_data[ 'review' ] )
        # self.meta = MetaReview( **self.test_data[ 'metareview' ] )
        # self.obj = Assignment( self.initial, self.review, self.meta )

    def test_is_activity_type( self ):
        # Create the unit
        self.assertFalse( InitialWork.is_activity_type( 'Unit 24 metareview' ) )
        self.assertTrue( InitialWork.is_activity_type( 'Unit 24 essay' ) )


class TestReview( TestCase ):
    def setUp( self ):
        self.test_data = test_data_factory()
        # Create the unit
        # self.initial = InitialWork( **self.test_data[ 'initial' ] )
        # self.review = Review( **self.test_data[ 'review' ] )
        # self.meta = MetaReview( **self.test_data[ 'metareview' ] )
        # self.obj = Assignment( self.initial, self.review, self.meta )

    def test_is_activity_type( self ):
        # Create the unit
        self.assertFalse( Review.is_activity_type( 'Unit 24 metareview' ) )
        self.assertTrue( Review.is_activity_type( 'Unit 24 peer review' ) )


class TestMetaReview( TestCase ):
    def setUp( self ):
        self.test_data = test_data_factory()
        # Create the unit
        # self.initial = InitialWork( **self.test_data[ 'initial' ] )
        # self.review = Review( **self.test_data[ 'review' ] )
        # self.meta = MetaReview( **self.test_data[ 'metareview' ] )
        # self.obj = Assignment( self.initial, self.review, self.meta )

    def test_is_activity_type( self ):
        # Create the unit
        self.assertTrue( MetaReview.is_activity_type( 'Unit 24 metareview' ) )
        self.assertFalse( MetaReview.is_activity_type( 'Unit 24 peer review' ) )

# class TestAssignment( TestCase ):
#     def setUp( self ):
#         self.test_data = test_data_factory()
#         # Create the unit
#         self.initial = InitialWork( **self.test_data[ 'initial' ] )
#         self.review = Review( **self.test_data[ 'review' ] )
#         self.meta = MetaReview( **self.test_data[ 'metareview' ] )
#         self.obj = Assignment( self.initial, self.review, self.meta )
#
#     def test_setup( self ):
#         # Create the unit
#         initial = InitialWork( **self.test_data[ 'initial' ] )
#         review = Review( **self.test_data[ 'review' ] )
#         meta = MetaReview( **self.test_data[ 'metareview' ] )
#         obj = Assignment( initial, review, meta )
#
#         self.assertIsInstance( obj.review, Review )

class TestJournal( TestCase ):
    def setUp( self ):
        pass
        # self.test_data = test_data_factory()
        # Create the unit
        # self.initial = InitialWork( **self.test_data[ 'initial' ] )
        # self.review = Review( **self.test_data[ 'review' ] )
        # self.meta = MetaReview( **self.test_data[ 'metareview' ] )
        # self.obj = Assignment( self.initial, self.review, self.meta )

    def test_is_activity_type( self ):
        # Create the unit
        self.assertTrue( Journal.is_activity_type( 'Journal (week 4)' ) )
        self.assertFalse( Journal.is_activity_type( 'Unit 24 peer review' ) )

