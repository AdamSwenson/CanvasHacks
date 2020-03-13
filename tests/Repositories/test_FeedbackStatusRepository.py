"""
Created by adam on 3/4/20
"""
__author__ = 'adam'

from unittest import TestCase
from unittest.mock import MagicMock

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Models.review_association import ReviewAssociation
from CanvasHacks.Models.status_record import FeedbackReceivedRecord
from CanvasHacks.Repositories.status import FeedbackStatusRepository
from TestingBase import TestingBase
from factories.ModelFactories import student_factory
from factories.PeerReviewedFactories import unit_factory

if __name__ == '__main__':
    pass


class TestFeedbackStatusRepository( TestingBase ):
    def setUp(self):
        self.config_for_test()
        self.unit = unit_factory()
        self.activity = self.unit.discussion_forum
        self.activity_id = self.activity.id

        self.dao = SqliteDAO()
        self.session = self.dao.session
        self.create_new_and_preexisting_students()
        self.create_preexisting_review_pairings(self.activity_id, self.students)

        # ids of authors previously notified
        self.previously_sent = []
        # ids of reviewers corresponding to previously notified authors

        self.obj = FeedbackStatusRepository( self.dao, self.activity )


    def test_record( self ):
        # Using id as input
        result = self.obj.record(self.student_ids[0])
        self.assertIsInstance(result, FeedbackReceivedRecord, "Correct type returned")
        self.assertEqual(self.student_ids[0], result.student_id, "Correct id set")
        self.assertIsNotNone( result.sent_at, "Timestamp automatically added" )

        # Using student object as input
        result = self.obj.record(self.students[1])
        self.assertIsInstance(result, FeedbackReceivedRecord, "Correct type returned")
        self.assertEqual(self.students[1].id, result.student_id, "Correct id set")
        self.assertIsNotNone( result.sent_at, "Timestamp automatically added" )


    def test_has_received( self ):
        num_previous = 2
        self.make_feedback_received_records( num_previous )
        self.assertEqual( num_previous, len( self.previously_sent ) )

        others = [sid for sid in self.student_ids if sid not in self.previously_sent]

        # Check
        for sid in self.previously_sent:
            self.assertTrue(self.obj.has_received(sid), "Returns true for notified students")

        for sid in others:
            self.assertFalse(self.obj.has_received(sid), "Returns false for non-notified students")


    def test_previously_received( self ):
        num_previous = 2
        self.make_feedback_received_records( num_previous )
        others = [sid for sid in self.student_ids if sid not in self.previously_sent]

        # call
        result = self.obj.previously_received

        # Check
        for r in result:
            self.assertIsInstance(r, FeedbackReceivedRecord, "Returns expected object")
            self.assertIn(r.student_id, self.previously_sent, "id in previously sent")
            self.assertNotIn(r.student_id, others, "no unexpected returned")

    def test_previously_received_ids( self ):
        num_previous = 2
        self.make_feedback_received_records( num_previous )
        others = [sid for sid in self.student_ids if sid not in self.previously_sent]

        # call
        result = self.obj.previously_received_ids

        # Check
        for r in result:
            self.assertIsInstance( r, int, "Returns expected type" )
            self.assertIn( r, self.previously_sent, "id in previously sent" )
            self.assertNotIn( r, others, "no unexpected returned" )

    def test_get( self ):
        num_previous = 2
        self.make_feedback_received_records( num_previous )
        self.assertEqual( num_previous, len( self.previously_sent ) )

        # call
        others = [sid for sid in self.student_ids if sid not in self.previously_sent]

        for sid in others:
            result = self.obj.get(sid)
            self.assertIsNone(result, "Returns none for unsent")

        for sid in self.previously_sent:
            result = self.obj.get(sid)
            self.assertIsInstance(result, FeedbackReceivedRecord, "Correct type returned")
            self.assertEqual(result.student_id, sid, "Correct sid")
            self.assertIsNotNone(result.sent_at, "Timestamp not empty")

    def test_reviewers_with_authors_sent_feedback( self ):
        num_previous = 2
        self.make_feedback_received_records( num_previous )
        self.assertEqual( num_previous, len( self.previously_sent ) )

        reviewers_with_notified_authors = [ r.assessor_id for r in self.pairings if
                                            r.assessee_id in self.previously_sent ]

        # ra = self.session.query(ReviewAssociation).all()
        # fb = self.session.query(FeedbackReceivedRecord).all()

        # try with all students to make it easy to check missing
        result = self.obj.reviewers_with_authors_sent_feedback

        self.assertEqual( num_previous, len( result ), "Correct number of records returned" )
        for sid in result:
            self.assertIn( sid, reviewers_with_notified_authors, "Returned for previously notified authors" )

        # self.create_preexisting_review_pairings(self.activity_id, self.students)

    def test_reviewers_with_authors_sent_feedback_different_activities( self ):
        num_previous = 2
        self.make_feedback_received_records( num_previous )

        reviewers_with_notified_authors = [ r.assessor_id for r in self.pairings if
                                            r.assessee_id in self.previously_sent ]

        pairing_activity_id = self.fake.random.randint(1, 9999)
        self.create_preexisting_review_pairings(pairing_activity_id, self.students, check_db_before_run=False)

        pairing_activity = MagicMock(id=pairing_activity_id)

        self.obj = FeedbackStatusRepository( self.dao, self.activity,  pairing_activity)

        # try with all students to make it easy to check missing
        result = self.obj.reviewers_with_authors_sent_feedback

        self.assertEqual( num_previous, len( result ), "Correct number of records returned when pairing activity id is different" )
        for sid in result:
            self.assertIn( sid, reviewers_with_notified_authors, "Returned for previously notified authors when pairing activity id is different" )



    def test_reviewers_with_notified_authors( self ):
        num_previous = 2
        self.make_feedback_received_records( num_previous )
        self.assertEqual( num_previous, len( self.previously_sent ) )

        reviewers_with_notified_authors = [ r.assessor_id for r in self.pairings if
                                            r.assessee_id in self.previously_sent ]

        # ra = self.session.query(ReviewAssociation).all()
        # fb = self.session.query(FeedbackReceivedRecord).all()

        # try with all students to make it easy to check missing
        result = self.obj.reviewers_with_authors_sent_feedback

        self.assertEqual( num_previous, len( result ), "Correct number of records returned" )
        for sid in result:
            self.assertIn( sid, reviewers_with_notified_authors, "Returned for previously notified authors" )

    def test_remove_reviewers_with_notified_authors( self ):
        num_previous = 2
        self.make_feedback_received_records( num_previous )
        self.assertEqual(num_previous, len(self.previously_sent))

        reviewers_with_notified_authors = [r.assessor_id for r in self.pairings if r.assessee_id in self.previously_sent]

        # ra = self.session.query(ReviewAssociation).all()
        # fb = self.session.query(FeedbackReceivedRecord).all()

        # try with all students to make it easy to check missing
        result = self.obj.remove_reviewers_with_notified_authors(self.students)

        self.assertEqual(len(self.student_ids) - num_previous, len(result), "Correct number of records returned")
        for sid in result:
            self.assertNotIn(sid, reviewers_with_notified_authors, "Author not previously notified")
