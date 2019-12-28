"""
Created by adam on 12/26/19
"""
from unittest import TestCase

from CanvasHacks.PeerReviewed.Submissions import *
from tests.factories.CanvasApiFactories import *
from tests.factories.ModelFactories import *
from tests.factories.PeerReviewedFactories import *

__author__ = 'adam'

if __name__ == '__main__':
    pass

# class TestSubmission( TestCase ):
#     def test_on_time( self ):
#         self.fail()


class TestInitialSubmission( TestCase ):
    def setUp( self ):
        self.test_data = activity_data_factory()
        self.activity = InitialWork( **self.test_data )
        self.student = student_factory()
        self.query_result = submission_result_factory( self.activity, self.student )

    def test_on_time( self ):
        obj = InitialSubmission( self.activity, self.query_result )
        self.assertTrue( obj.on_time, "Returns true when on time" )

        query_result = submission_result_factory( self.activity, self.student, on_time=False )
        obj = InitialSubmission( self.activity, query_result )
        self.assertFalse( obj.on_time, "Returns false when late" )

    def test_submitter_points( self ):
        obj = InitialSubmission( self.activity, self.query_result )
        self.assertEqual( obj.submitter_points, self.activity.completion_points,
                          "Assigns completion points when on time" )

    def test_process( self ):
        obj = InitialSubmission( self.activity, self.query_result )
        self.assertTrue( obj.submitter == self.student, "Submitting student sets properly" )
        self.assertEqual( obj.completion_date, self.query_result[ 'submitted_at' ], "completino date sets properly" )


class TestReviewSubmission( TestCase ):

    def setUp( self ):
        self.reviewer = student_factory()
        self.student = student_factory()
        self.test_data = activity_data_factory()
        self.activity = Review( **self.test_data )
        self.query_result = peer_review_result_factory( self.student, self.reviewer )

    def test_process( self ):
        obj = ReviewSubmission( self.activity, self.query_result )
        self.assertTrue( obj.submitter == self.student, "Submitting student sets properly" )
        self.assertTrue( obj.reviewer == self.reviewer, "Reviewing student sets properly" )
        # self.assertEqual(obj.completion_date, self.query_result['submitted_at'], "completino date sets properly")

    def test_is_complete( self ):
        # self.query_result['workflow_state'] = 'completed'
        obj = ReviewSubmission( self.activity, self.query_result )
        self.assertTrue( obj.is_complete, "Returns true when workflow state is completed" )

        query_result = peer_review_result_factory( self.student, self.reviewer, completed=False )
        # self.query_result['workflow_state'] = 'assigned'
        obj = ReviewSubmission( self.activity, query_result )
        self.assertFalse( obj.is_complete, "Returns false when workflow state is not completed" )

    def test_reviewer_points( self ):
        obj = ReviewSubmission( self.activity, self.query_result )
        self.assertEqual( obj.reviewer_points, self.activity.completion_points,
                          "Assigns completion points when the review is complete" )

        query_result = peer_review_result_factory( self.student, self.reviewer, completed=False )
        obj = ReviewSubmission( self.activity, query_result )
        self.assertEqual( obj.reviewer_points, 0, "Assigns 0 when the review is incomplete" )

    def test_submitter_points( self ):
        score = random.randint( 0, 100 )

        obj = ReviewSubmission( self.activity, self.query_result )
        obj.assigned_score = score
        self.assertEqual( obj.submitter_points, score, "Gives assigned score when the reviewer did their job" )

        query_result = peer_review_result_factory( self.student, self.reviewer, completed=False )
        obj = ReviewSubmission( self.activity, query_result )
        obj.assigned_score = score
        self.assertEqual( obj.submitter_points, self.activity.assignable_points,
                          "Gives max assignable points when the reviewer did not do their job" )
