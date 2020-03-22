"""
Created by adam on 3/22/20
"""
__author__ = 'adam'

from unittest import TestCase

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Models.submission_record import SubmissionRecord
from CanvasHacks.Repositories.submission_records import SubmissionRecordRepository
from TestingBase import TestingBase
from factories.PeerReviewedFactories import unit_factory

if __name__ == '__main__':
    pass


class TestSubmissionRecordRepository( TestingBase ):
    def setUp(self):
        self.config_for_test()
        self.unit = unit_factory()
        self.activity = self.unit.discussion_forum
        self.activity_id = self.activity.id

        self.dao = SqliteDAO()
        self.session = self.dao.session
        self.create_new_and_preexisting_students()
        # self.create_preexisting_review_pairings(self.activity_id, self.students)

        # ids of authors previously notified
        self.previously_submitted = []
        # ids of reviewers corresponding to previously notified authors

        self.obj = SubmissionRecordRepository( self.dao, self.activity )


    def test_record( self ):
        # Using id as input
        result = self.obj.record(self.student_ids[0])
        self.assertIsInstance(result, SubmissionRecord, "Correct type returned")
        self.assertEqual(self.student_ids[0], result.student_id, "Correct id set")
        self.assertIsNotNone( result.submitted_at, "Timestamp automatically added" )

        # Using student object as input
        result = self.obj.record(self.students[1])
        self.assertIsInstance(result, SubmissionRecord, "Correct type returned")
        self.assertEqual(self.students[1].id, result.student_id, "Correct id set")
        self.assertIsNotNone( result.submitted_at, "Timestamp automatically added" )



    def test_has_submitted( self ):
        num_previous = 2
        self.make_submitted_records( num_previous )

        others = [sid for sid in self.student_ids if sid not in self.previously_submitted]

        # Check
        for sid in self.previously_submitted:
            self.assertTrue(self.obj.has_submitted(sid), "Returns true for notified students")

        for sid in others:
            self.assertFalse(self.obj.has_submitted(sid), "Returns false for non-notified students")


    def test_previously_submitted( self ):
        num_previous = 2
        self.make_submitted_records( num_previous )

        others = [sid for sid in self.student_ids if sid not in self.previously_submitted]

        # call
        result = self.obj.previously_submitted

        # Check
        for r in result:
            self.assertIsInstance(r, SubmissionRecord, "Returns expected object")
            self.assertIn(r.student_id, self.previously_submitted, "id in previously submitted")
            self.assertNotIn(r.student_id, others, "no unexpected returned")

    def test_previously_submitted_ids( self ):
        num_previous = 2
        self.make_submitted_records( num_previous )
        others = [sid for sid in self.student_ids if sid not in self.previously_submitted]

        # call
        result = self.obj.previously_submitted_ids

        # Check
        for r in result:
            self.assertIsInstance( r, int, "Returns expected type" )
            self.assertIn( r, self.previously_submitted, "id in previously submitted" )
            self.assertNotIn( r, others, "no unexpected returned" )

    def test_get( self ):
        num_previous = 2
        self.make_submitted_records( num_previous )

        # call
        others = [sid for sid in self.student_ids if sid not in self.previously_submitted]

        for sid in others:
            result = self.obj.get(sid)
            self.assertIsNone(result, "Returns none for unsubmitted")

        for sid in self.previously_submitted:
            result = self.obj.get(sid)
            self.assertIsInstance(result, SubmissionRecord, "Correct type returned")
            self.assertEqual(result.student_id, sid, "Correct sid")
            self.assertIsNotNone(result.submitted_at, "Timestamp not empty")

    # def test_reviewers_with_notified_authors( self ):
    #     num_previous = 2
    #     self.make_invitation_submitted_records( num_previous )
    #
    #     reviewers_with_authors_submitted_feedback = [ r.assessor_id for r in self.pairings if
    #                                         r.assessee_id in self.previously_submitted ]
    #
    #     # ra = self.session.query(ReviewAssociation).all()
    #     # fb = self.session.query(FeedbacksubmittedRecord).all()
    #
    #     # try with all students to make it easy to check missing
    #     result = self.obj.reviewers_with_authors_submitted_feedback
    #
    #     self.assertEqual( num_previous, len( result ), "Correct number of records returned" )
    #     for sid in result:
    #         self.assertIn( sid, reviewers_with_authors_submitted_feedback, "Returned for previously notified authors" )
    #
    # def test_remove_reviewers_with_notified_authors( self ):
    #     num_previous = 2
    #     self.make_invitation_submitted_records( num_previous )
    #
    #     reviewers_with_authors_submitted_feedback = [r.assessor_id for r in self.pairings if r.assessee_id in self.previously_submitted]
    #
    #     # ra = self.session.query(ReviewAssociation).all()
    #     # fb = self.session.query(FeedbacksubmittedRecord).all()
    #
    #     # try with all students to make it easy to check missing
    #     result = self.obj.remove_reviewers_with_notified_authors(self.students)
    #
    #     self.assertEqual(len(self.student_ids) - num_previous, len(result), "Correct number of records returned")
    #     for sid in result:
    #         self.assertNotIn(sid, reviewers_with_authors_submitted_feedback, "Author not previously notified")


    # def test_get( self ):
    #     self.fail()
    #
    # def test_has_submitted( self ):
    #     self.fail()
    #
    # def test_submitted_at( self ):
    #     self.fail()
    #
    # def test_previously_submitted( self ):
    #     self.fail()
    #
    # def test_previously_submitted_ids( self ):
    #     self.fail()
    #
    # def test_record( self ):
    #     self.fail()
