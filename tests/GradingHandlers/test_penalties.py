"""
Created by adam on 5/6/19
"""
from unittest import TestCase

from CanvasHacks.GradingCorrections.penalities import get_penalty, HalfLate, QuarterLate, NoLatePenalty
import pandas as pd

__author__ = 'adam'

from TestingBase import TestingBase


class TestNoLatePenalty(TestingBase):
    def setUp(self):
        self.config_for_test()
        self.due_date = pd.to_datetime('2019-02-23 07:59:00')
        self.grace_period = None
        self.obj = NoLatePenalty(self.due_date, self.grace_period)

    def test_get_penalty( self ):
        result = self.obj.get_penalty(self.fake.date_time_this_century())
        self.assertEqual(0, result, "get penalty returns 0")

    def test_get_penalized_score( self ):
        original_score = self.fake.random.randint(1, 111111)
        result = self.obj.get_penalized_score( self.fake.date_time_this_century(), original_score )
        self.assertEqual( original_score, result, "get penalized score returns original score" )

    def test_get_fudge_points( self ):
        original_score = self.fake.random.randint( 1, 111111 )
        result = self.obj.get_fudge_points( self.fake.date_time_this_century(), original_score, {} )
        self.assertEqual( 0, result, "get fudge points returns 0" )


class TestHalfLate(TestingBase):

    def setUp(self):
        self.config_for_test()

        self.due_date = pd.to_datetime('2019-02-23 07:59:00')
        self.grace_period = None
        self.obj = HalfLate(self.due_date, self.grace_period)

    def test_get_penalty( self ):
        test_cases = [
            {
                # full credit case
                'submitted': '2019-02-22 07:59:00',
                # 'due': '2019-02-23 07:59:00',
                'half': '2019-03-01 07:59:00',
                'expect': 0
            },
            {
                # half credit case
                'submitted': '2019-02-24 07:59:00',
                # 'due': '2019-02-23 07:59:00',
                'half': '2019-03-01 07:59:00',
                'expect': .5
            }

        ]

        for t in test_cases:
            self.assertEquals( self.obj.get_penalty( t[ 'submitted' ]), t[ 'expect' ], "Returns expected penalty" )

    def test_get_penalized_score( self ):
        original_score = self.fake.random.randint(1, 2402)
        test_cases = [
            {
                # full credit case
                'submitted': '2019-02-22 07:59:00',
                # 'due': '2019-02-23 07:59:00',
                'half': '2019-03-01 07:59:00',
                'expect': original_score
            },
            {
                # half credit case
                'submitted': '2019-02-24 07:59:00',
                # 'due': '2019-02-23 07:59:00',
                'half': '2019-03-01 07:59:00',
                'expect': original_score * .5
            }
        ]

        for t in test_cases:
            self.assertEquals(t[ 'expect' ], self.obj.get_penalized_score( t[ 'submitted' ], original_score),  "Returns expected score" )

    def test_get_fudge_points_no_penalty( self ):
        submitted_date = self.due_date - pd.Timedelta('{} days'.format(self.fake.random.randint(1, 200)))
        original_score = self.fake.random.randint(1, 2222)
        row = {'submitted' : 'taco'}

        # call
        result = self.obj.get_fudge_points(submitted_date, original_score, row)

        # check
        self.assertEqual(result, 0, "zero fudge points returned")
        self.assertNotIn( row, self.obj.penalized_records, "Row not added to penalized rows" )

    def test_get_fudge_points_penalty( self ):
        submitted_date = self.due_date + pd.to_timedelta( '{} days'.format( self.fake.random.randint( 1, 200 ) ) )
        # not randomizing so don't need to deal with float in checking record
        original_score = 100
        row = { 'submitted': 'taco' }

        # call
        result = self.obj.get_fudge_points( submitted_date, original_score, row )

        # check
        self.assertEqual(result, -50, "fudge points of 50% original returned" )
        expected_rec = {'record': row, 'penalty': 0.5, 'fudge_points': -50}
        self.assertIn( expected_rec, self.obj.penalized_records, "Row added to penalized rows" )


class TestQuarterLate(TestingBase):

    def setUp(self):
        self.config_for_test()

        self.due_date = pd.to_datetime('2019-02-23 07:59:00')
        self.last_half_date = pd.to_datetime('2019-03-01 07:59:00')
        self.grace_period = None
        self.obj = QuarterLate(self.due_date, last_half_credit_date=self.last_half_date, grace_period=self.grace_period)

    def test_get_penalty( self ):
        test_cases = [
            {
                # full credit case
                'submitted': '2019-02-22 07:59:00',
                # 'due': '2019-02-23 07:59:00',
                # 'half': '2019-03-01 07:59:00',
                'expect': 0
            },
            {
                # half credit case
                'submitted': '2019-02-24 07:59:00',
                # 'due': '2019-02-23 07:59:00',
                # 'half': '2019-03-01 07:59:00',
                'expect': .5
            },
            {
                # quarter credit case
                'submitted': '2019-03-02 07:59:00',
                # 'due': '2019-02-23 07:59:00',
                # 'half': '2019-03-01 07:59:00',
                'expect': .25
            },
        ]

        for t in test_cases:
            self.assertEquals( self.obj.get_penalty( t[ 'submitted' ]), t[ 'expect' ], "Returns expected penalty" )

    def test_get_fudge_points_no_penalty( self ):
        submitted_date = self.due_date - pd.Timedelta( '{} days'.format( self.fake.random.randint( 1, 200 ) ) )
        original_score = self.fake.random.randint( 1, 2222 )
        row = { 'submitted': 'taco' }

        # call
        result = self.obj.get_fudge_points( submitted_date, original_score, row )

        # check
        self.assertEqual( result, 0, "zero fudge points returned" )
        self.assertEqual(0, len(self.obj.penalized_records), "Row not added to penalized records")
        # self.assertNotIn( row, self.obj.penalized_records, "Row not added to penalized rows" )

    def test_get_fudge_points_quarter_penalty( self ):
        submitted_date = self.last_half_date + pd.to_timedelta( '1 days')
        original_score = 100
        row = { 'submitted': 'taco' }

        # call
        result = self.obj.get_fudge_points( submitted_date, original_score, row )

        # check
        self.assertEqual( result, -25, "fudge points of 25% original returned" )
        expected_rec = {'record': row, 'penalty': 0.25, 'fudge_points': -25}
        self.assertIn( expected_rec, self.obj.penalized_records, "Record added to penalized rows" )

    def test_get_fudge_points_half_penalty( self ):
        submitted_date = self.due_date + pd.to_timedelta( '1 days' )
        original_score = 100
        row = { 'submitted': 'taco' }

        # call
        result = self.obj.get_fudge_points( submitted_date, original_score, row )

        # check
        self.assertEqual( result, -50, "fudge points of 50% original returned" )
        expected_rec = { 'record': row, 'penalty': 0.5, 'fudge_points': -50 }
        self.assertIn( expected_rec, self.obj.penalized_records, "Record added to penalized rows" )

    # def test_get_penalized_score( self ):
    #     original_score = self.fake.random.randint(1, 2402)
    #     test_cases = [
    #         {
    #             # full credit case
    #             'submitted': '2019-02-22 07:59:00',
    #             # 'due': '2019-02-23 07:59:00',
    #             'half': '2019-03-01 07:59:00',
    #             'expect': original_score
    #         },
    #         {
    #             # half credit case
    #             'submitted': '2019-02-24 07:59:00',
    #             # 'due': '2019-02-23 07:59:00',
    #             'half': '2019-03-01 07:59:00',
    #             'expect': original_score * .5
    #         }
    #     ]

# ------------------------- older
class TestGet_penalty( TestCase ):
    def test_get_penalty( self ):
        test_cases = [
            {
                # full credit case
                'submitted': '2019-02-22 07:59:00',
                'due': '2019-02-23 07:59:00',
                'half': '2019-03-01 07:59:00',
                'expect': 0
            },
            {
                # half credit case
                'submitted': '2019-02-24 07:59:00',
                'due': '2019-02-23 07:59:00',
                'half': '2019-03-01 07:59:00',
                'expect': .5
            },
            {
                # quarter credit case
                'submitted': '2019-03-02 07:59:00',
                'due': '2019-02-23 07:59:00',
                'half': '2019-03-01 07:59:00',
                'expect': .25
            },
        ]

        for t in test_cases:
            self.assertEquals( get_penalty( t[ 'submitted' ], t[ 'due' ], t[ 'half' ] ), t[ 'expect' ] )
