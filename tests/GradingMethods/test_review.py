"""
Created by adam on 3/20/20
"""
__author__ = 'adam'

from unittest import TestCase
from unittest.mock import patch, MagicMock
import pandas as pd

from CanvasHacks.GradingMethods.review import ReviewBasedLikert, ReviewBasedPoints
from TestingBase import TestingBase
from factories.PeerReviewedFactories import unit_factory
from factories.RepositoryMocks import ContentRepositoryMock

if __name__ == '__main__':
    pass


class TestReviewBasedLikert( TestingBase ):

    def setUp(self) -> None:
        self.config_for_test()
        self.create_new_and_preexisting_students()
        self.unit = unit_factory()
        self.graded_activity = self.unit.initial_work
        self.review_activity = self.unit.review
        self.column_names = ['taco']

        # self.reviewRepo = ContentRepositoryMock()

    def test__initialize( self ):
        self.skipTest('todo')

    @patch('CanvasHacks.GradingMethods.review.WorkRepositoryLoaderFactory')
    def test_grade( self, workRepoMock ):
        # 'strongly agree': 1,
        # 'agree': 0.9,
        # 'disagree': 0.5,
        # 'strongly disagree': 0.1
        p = {'get_student_work.return_value': pd.DataFrame([
            {'student_id': self.students[0].student_id,
             self.column_names[0]: 'Strongly Agree'
             }]
        ).iloc[0]}

        reviewRepo = MagicMock(**p)
        workRepoMock.make = MagicMock(return_value=reviewRepo)

        self.obj = ReviewBasedLikert( graded_activity=self.graded_activity,
                                      review_activity=self.review_activity,
                                      pct_of_score=1,
                                      review_columns=self.column_names )
        self.session = self.obj.dao.session
        self.create_preexisting_review_pairings(activity_id=self.graded_activity.id,
                                                preexisting_students=self.students)

        # call
        result = self.obj.grade(self.students[0].student_id)

        # check
        self.assertEqual(result, 1, "returns expected pct")


    def test_grade_portion_of_total_score( self ):
        self.skipTest('todo')

    def test_grade_reviewing_student_not_turned_in( self ):
        self.skipTest('todo')



class TestReviewBasedPoints( TestingBase ):

    def setUp(self) -> None:
        self.config_for_test()
        self.create_new_and_preexisting_students()
        self.unit = unit_factory()
        self.max_activity_points = 6
        self.unit.initial_work.points_possible = self.max_activity_points
        self.graded_activity = self.unit.initial_work
        self.pct_reviewer_assigned = 0.5
        self.review_activity = self.unit.review
        self.column_names = ['taco']

        # self.reviewRepo = ContentRepositoryMock()

    def test__initialize( self ):
        self.skipTest('todo')

    @patch('CanvasHacks.GradingMethods.review.WorkRepositoryLoaderFactory')
    def test_grade( self, workRepoMock ):
        max_points = 3
        possible_scores = [ i for i in range(0, max_points)]

        for reviewer_score in possible_scores:
            print("checking reviewer score: ", reviewer_score)
            expected = reviewer_score #/ (self.pct_reviewer_assigned * self.max_activity_points)

            p = {'get_student_work.return_value': pd.DataFrame([
                {'student_id': self.students[0].student_id,
                 self.column_names[0]: reviewer_score
                 }]
            ).iloc[0]}

            reviewRepo = MagicMock(**p)
            workRepoMock.make = MagicMock(return_value=reviewRepo)

            self.obj = ReviewBasedPoints( graded_activity=self.graded_activity,
                                          review_activity=self.review_activity,
                                          pct_of_score=self.pct_reviewer_assigned,
                                          review_columns=self.column_names,
                                          max_possible_points=max_points +1)
            self.session = self.obj.dao.session
            self.create_preexisting_review_pairings(activity_id=self.graded_activity.id,
                                                    preexisting_students=self.students)

            # call
            result = self.obj.grade(self.students[0].student_id)

            # check

            print(expected, expected) # * self.max_activity_points)
            self.assertEqual(result, expected, "returns expected pct: {}".format(expected))


    def test_grade_portion_of_total_score( self ):
        self.skipTest('todo')
