"""
Created by adam on 9/28/20
"""
__author__ = 'adam'

from unittest.mock import MagicMock, create_autospec

import pandas as pd

from CanvasHacks.GradingHandlers.assignment import AssignmentGraderPoints
from CanvasHacks.GradingHandlers.records import PointsRecord
from CanvasHacks.GradingMethods.base import IGradingMethod, IGradingMethodPoints
from CanvasHacks.GradingMethods.review import ReviewBasedPoints
from CanvasHacks.Repositories.assignments import AssignmentRepository
from CanvasHacks.Repositories.interfaces import ISubmissionRepo
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from TestingBase import TestingBase
from factories.PeerReviewedFactories import unit_factory

if __name__ == '__main__':
    pass


class TestAssignmentGraderPoints( TestingBase ):

    def setUp( self ):
        self.config_for_test()

        self.unit = unit_factory()
        self.activity = self.unit.initial_work
        self.activity.corrections = [ ]
        self.activity.penalizers = [ ]
        self.activity.grade_methods = [ ]

        # self.workRepo.activity = self.workRepo

        self.submissionRepo = create_autospec( ISubmissionRepo )
        self.associationRepo = create_autospec( AssociationRepository )

        self.submissions = [ self.make_submission_row() for _ in range( 0, self.fake.random.randint( 2, 30 ) ) ]

        self.blank_submissions = [ self.make_submission_row( is_blank=True ) for _ in
                                   range( 0, self.fake.random.randint( 2, 30 ) ) ]

        data = pd.DataFrame( self.submissions + self.blank_submissions )

        self.workRepo = create_autospec( AssignmentRepository,
                                         activity=self.activity, data=data)

        self.obj = AssignmentGraderPoints( work_repo=self.workRepo,
                                           submission_repo=self.submissionRepo, association_repo=self.associationRepo )

    def make_submission_row( self, is_blank=False ):
        return {
            'student_id': self.fake.random.randint( 1, 10000 ),
            'body': None if is_blank else self.fake.text()
        }

    def test_max_points( self ):
        # prep
        pts = self.fake.random.randint( 1, 100 )
        cnt = self.fake.random.randint( 1, 10 )
        at = { 'max_possible_points': pts }
        methods = [ MagicMock(**at) for i in range( 0, cnt ) ]

        self.obj.grade_methods = methods

        # call
        # for m in methods:
        #     self.assertEqual(pts, m.grade())
        result = self.obj.max_points

        # # check
        self.assertEqual(pts * cnt, result, "Expected max possible points")


    def test__compute_score_review_based_points( self ):

        # prep
        pts = self.fake.random.randint( 1, 100 )
        cnt = self.fake.random.randint( 1, 10 )
        at = { 'grade.return_value': pts }
        methods = [ create_autospec( ReviewBasedPoints, **at ) for i in range( 0, cnt ) ]
        self.obj.grade_methods = methods

        content = self.fake.text()
        author_id = self.fake.random.randint( 1, 111111 )
        record = PointsRecord( student_id=author_id )

        # call
        result = self.obj._compute_score( record, content )

        # check
        # The author id was passed rather than the content
        for method in methods:
            method.grade.assert_called_once_with( author_id )

        # A points record object was returned which contains
        # the expected student id and correct number of entries
        self.assertIsInstance( result, PointsRecord )
        self.assertEqual( result.student_id, author_id )
        self.assertEqual( len( result.grade_dict.keys() ), cnt )

    def test__compute_score_other_points( self ):
        # prep
        pts = self.fake.random.randint( 1, 100 )
        cnt = self.fake.random.randint( 1, 10 )
        methods = [ create_autospec( IGradingMethodPoints, **{ 'grade.return_value': pts } ) for i in range( 0, cnt ) ]
        self.obj.grade_methods = methods

        content = self.fake.text()
        author_id = self.fake.random.randint( 1, 111111 )
        record = PointsRecord( student_id=author_id )

        # call
        result = self.obj._compute_score( record, content )

        # check
        # The content was passed rather than the author id
        for method in methods:
            method.grade.assert_called_once_with( content )

        # A points record object was returned which contains
        # the expected student id and correct number of entries
        self.assertIsInstance( result, PointsRecord )
        self.assertEqual( result.student_id, author_id )
        self.assertEqual( len( result.grade_dict.keys() ), cnt )

    def test__compute_penalty( self ):
        self.fail()

    def test__compute_correction( self ):
        self.fail()

    # def test__compute_initial_total( self ):
    #     self.fail()

    def test_grade( self ):
        # prep
        cnt = self.fake.random.randint( 1, 10 )
        pts = self.fake.random.randint( 1, 100 )
        attrs = {'grade.return_value': pts}

        review_methods = [ create_autospec( ReviewBasedPoints, **attrs) for _ in range( 0, cnt ) ]

        non_review_methods = [
            create_autospec( IGradingMethodPoints, **attrs ) for _ in range( 0, cnt ) ]

        self.obj.grade_methods = review_methods + non_review_methods

        # call
        graded, graded_records = self.obj.grade()

        # check
        submitter_ids = [ r['student_id'] for r in self.submissions ]

        # Graded_records list
        # Graded records contains correct number of PointsRecords
        self.assertEqual( len( graded_records ), len( self.submissions ),
                          "Correct number of records which excludes blank submissions" )

        # A points record object was returned which contains
        # the expected student id and correct number of entries
        for record in graded_records:
            self.assertIsInstance( record, PointsRecord, "list holds expected objects" )
            self.assertIn( record.student_id, submitter_ids, "student id recorded correctly" )
            self.assertEqual( len( record.grade_dict.keys() ), len(self.obj.grade_methods), "Correct number of entries in grade record" )

        # graded list
        self.assertEqual( len( graded ), len( self.submissions ),
                          "Correct number of items which excludes blank submissions" )

        # The expected tuple was returned
        for submission, total_points in graded:
            self.assertEqual(cnt * 2 * pts, total_points, "Graded tuple contains correct points")
            # self.assertIn( submission, self.submissions )

    def test_report_late_penalties( self ):
        self.skipTest()
