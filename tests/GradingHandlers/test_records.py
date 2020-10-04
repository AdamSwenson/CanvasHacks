"""
Created by adam on 9/23/20
"""
__author__ = 'adam'


from unittest.mock import MagicMock, create_autospec, patch
from CanvasHacks import environment
from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.GradingHandlers.records import PointsRecord
# from CanvasHacks.GradingMethods.nonempty import CreditForNonEmptyPoints
# from CanvasHacks.GradingMethods.base import IGradingMethodPoints
from CanvasHacks.GradingMethods.nonempty import CreditForNonEmptyPoints
from CanvasHacks.GradingMethods.review import ReviewBasedPoints
# from CanvasHacks.GradingMethods.wordcount import GradeByWordCountPoints
from TestingBase import TestingBase
from factories.PeerReviewedFactories import unit_factory

if __name__ == '__main__':
    pass



class TestPointsRecord( TestingBase ):

    def setUp( self ):
        self.config_for_test()

        # todo using mock for second grader since these cause import errors
        # ,  GradeByWordCountPoints, CreditForNonEmptyPoints]

        self.unit = unit_factory()
        self.graded_activity = self.unit.initial_work
        self.review_activity = self.unit.review

        # rp = ReviewBasedPoints(graded_activity=self.graded_activity,
        #                        review_activity=self.review_activity,
        #                        review_columns=[], max_possible_points=None )
        rp = create_autospec(ReviewBasedPoints)
        rp.name = 'ReviewBasedPoints'
        ne = CreditForNonEmptyPoints(800)

        self.methods = [rp, ne ]

        self.method_points = []

        self.obj = PointsRecord()

    def test_total_points( self ):
        self.obj.grade_dict[ 'a'] = 10
        self.obj.grade_dict['b'] = 10
        self.obj.grade_dict['c'] = -5
        expected = 15

        self.assertEqual(self.obj.total_points, expected, "returns expected sum")

    def test_add_grade( self ):
        for m in self.methods:
            p = self.fake.random.randint( 1, 100 )
            self.method_points.append(p)
            self.obj.add_grade(m, p)

        # check
        for method in self.methods:
            self.assertIn(method.__class__.__name__, self.obj.grade_dict.keys())

        for p in self.method_points:
            self.assertIn(p, self.obj.grade_dict.values())


        # for i in range(0, len(self.methods)):
        #     self.methods[ i ], self.method_points[ i ]
        #
        # type( grade_method ).__name__ ] = points


    def test_add_grade_for_penalties( self ):
        for m in self.methods:
            p = - self.fake.random.randint( 1, 100 )
            self.method_points.append(p)
            self.obj.add_grade(m, p)

        # check
        for method in self.methods:
            self.assertIn(method.__class__.__name__, self.obj.grade_dict.keys())

        for p in self.method_points:
            self.assertIn(p, self.obj.grade_dict.values())

    def test_add_general_message( self ):
        cnt = 5
        messages = [self.fake.text() for _ in range(0, cnt)]

        for m in messages:
            self.obj.add_general_message(m)

        # check
        for i, m in enumerate(messages):
            k = f"{self.obj.GENERAL_MESSAGE_KEY} {i+1}"
            self.assertIn(k, self.obj.log_messages, "Has expected key")
            self.assertEqual(m, self.obj.log_messages[k])

