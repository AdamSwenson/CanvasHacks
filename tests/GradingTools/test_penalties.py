"""
Created by adam on 5/6/19
"""
from unittest import TestCase

from CanvasHacks.GradingTools.penalities import get_penalty

__author__ = 'adam'


class TestEnsure_timestamps( TestCase ):
    def test_ensure_timestamps( self ):
        self.skipTest('todo')


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
