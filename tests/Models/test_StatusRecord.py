"""
Created by adam on 2/23/20
"""
from unittest import TestCase

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from tests.TestingBase import TestingBase
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import activity_data_factory
from faker import Faker
fake = Faker()
import datetime
import pytz
from CanvasHacks.Models.status_record import ComplexStatusRecord
from CanvasHacks.TimeTools import current_utc_timestamp


__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestStatusRecord( TestingBase ):

    def setUp(self):
        self.config_for_test()
        self.dao = SqliteDAO()
        print("Connected to testing db")
        self.session = self.dao.session

        self.activity_data = activity_data_factory()
        self.target_student = student_factory()
        self.reviewing_student = student_factory()
        self.reviewed_student = student_factory()
        self.activity_id = fake.random.randint(1111, 99999)

    def test_initial_record_creation( self ):
        rec = ComplexStatusRecord( student_id=self.target_student.id, content_assignment_id=self.activity_id )
        self.session.add( rec )
        self.session.commit()

        self.assertIsInstance( rec, ComplexStatusRecord )

        # Check
        r = self.session.query( ComplexStatusRecord ) \
            .filter( ComplexStatusRecord.content_assignment_id == self.activity_id ) \
            .all()
        self.assertEqual(len(r), 1, "One record returned")
        self.assertEqual(r[0].student_id, self.target_student.id)
        self.assertEqual(r[0].content_assignment_id, self.activity_id)

    def test_is_under_review( self ):
        rec = ComplexStatusRecord( student_id=self.target_student.id, content_assignment_id=self.activity_id )
        self.session.add( rec )
        self.session.commit()

        self.assertIsInstance( rec, ComplexStatusRecord )
        self.assertFalse(rec.is_under_review())

        rec.reviewed_by = self.reviewing_student.id
        self.assertTrue(rec.is_under_review())

    def test_add_reviewee( self ):
        # prep
        rec = ComplexStatusRecord( student_id=self.target_student.id, content_assignment_id=self.activity_id )
        self.assertTrue(rec.reviewer_of is None)
        self.assertTrue(rec.reviewer_assigned_on is None)

        # call
        rec.add_reviewee(self.reviewed_student)

        # check
        self.assertIsInstance(rec.reviewer_assigned_on, datetime.datetime)
        self.assertEqual(rec.reviewer_of, self.reviewed_student.id)

    def test_add_reviewer( self ):
        # prep
        rec = ComplexStatusRecord( student_id=self.target_student.id, content_assignment_id=self.activity_id )
        self.assertTrue(rec.reviewed_by is None)

        # call
        rec.add_reviewer(self.reviewing_student)

        # check
        self.assertEqual(rec.reviewed_by, self.reviewing_student.id)

    def test_record_content_assignment_submission_no_date_provided( self ):
        rec = ComplexStatusRecord( student_id=self.target_student.id, content_assignment_id=self.activity_id )
        self.assertTrue(rec.content_assignment_submitted is None)

        # call
        rec.record_content_assignment_submission()

        # check
        self.assertIsInstance(rec.content_assignment_submitted, datetime.datetime)
        self.assertEqual(rec.content_assignment_submitted.tzinfo, pytz.utc, "Timestamp is utc")

    def test_record_content_assignment_submission_date_provided( self ):
        rec = ComplexStatusRecord( student_id=self.target_student.id, content_assignment_id=self.activity_id )
        self.assertTrue(rec.content_assignment_submitted is None)

        submission_ts = current_utc_timestamp()

        # call
        rec.record_content_assignment_submission(submission_ts)

        # check
        self.assertIsInstance(rec.content_assignment_submitted, datetime.datetime)
        self.assertEqual(rec.content_assignment_submitted.tzinfo, pytz.utc, "Timestamp is utc")
        self.assertEqual(rec.content_assignment_submitted, submission_ts, "Passed-in timestamp set")

    def test_record_sending_metareview_results( self ):
        rec = ComplexStatusRecord( student_id=self.target_student.id, content_assignment_id=self.activity_id )
        self.assertTrue(rec.metareview_results_on is None)

        # call
        rec.record_sending_metareview_results()

        # check
        self.assertIsInstance(rec.metareview_results_on, datetime.datetime)
        self.assertEqual(rec.metareview_results_on.tzinfo, pytz.utc, "Timestamp is utc")

    def test_record_sending_review_results( self ):
        rec = ComplexStatusRecord( student_id=self.target_student.id, content_assignment_id=self.activity_id )
        self.assertTrue(rec.review_results_on is None)

        # call
        rec.record_sending_review_results()

        # check
        self.assertIsInstance(rec.review_results_on, datetime.datetime)
        self.assertEqual(rec.review_results_on.tzinfo, pytz.utc, "Timestamp is utc")

    def test_record_wait_notification( self ):
        rec = ComplexStatusRecord( student_id=self.target_student.id, content_assignment_id=self.activity_id )
        self.assertTrue(rec.wait_notification_on is None)

        # call
        rec.record_wait_notification()

        # check
        self.assertIsInstance(rec.wait_notification_on, datetime.datetime)
        self.assertEqual(rec.wait_notification_on.tzinfo, pytz.utc, "Timestamp is utc")

