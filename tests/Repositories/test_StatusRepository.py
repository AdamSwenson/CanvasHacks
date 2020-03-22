"""
Created by adam on 2/24/20
"""
import unittest
from tests.TestingBase import TestingBase

from faker import Faker

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Models.status_record import StatusRecord
from CanvasHacks.Repositories.status import StatusRepository
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory
fake = Faker()


class TestStatusRepository( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.dao = SqliteDAO()
        print( "Connected to testing db" )
        self.session = self.dao.session

        self.student = student_factory()
        self.unit = unit_factory()
        self.activity = fake.random.choice( self.unit.components )

        self.obj = StatusRepository( self.dao, self.activity )

    def _create_record( self ):
        rec = StatusRecord( student_id=self.student.student_id, activity_id=self.activity.id )
        self.session.add( rec )
        self.session.commit()
        return rec

    def test_get_or_create_record( self ):
        self.skipTest('todo')

    def test_get_record( self ):
        self.skipTest('todo')

    def test_create_record( self ):
        r = self.obj.create_record( self.student )

        # check
        self.assertIsInstance( r, StatusRecord )
        self.assertEqual( r.student_id, self.student.student_id )
        self.assertEqual( r.activity_id, self.activity.id )
        self.assertTrue( r.submitted is None, "Submission is empty" )
        self.assertTrue( r.notified is None, "Notification is empty" )
        self.assertTrue( r.results is None, "Sent results is empty" )

    def test_record_notified( self ):
        self.skipTest('todo')

    def test_record_submitted( self ):
        self.skipTest('todo')


# class TestComplexStatusRepository( TestingBase ):
#
#     def setUp( self ):
#         self.config_for_test()
#         self.dao = SqliteDAO()
#         print( "Connected to testing db" )
#         self.session = self.dao.session
#
#         self.activity_data = activity_data_factory()
#         self.target_student = student_factory()
#         self.reviewing_student = student_factory()
#         self.reviewed_student = student_factory()
#         self.activity_id = fake.random.randint( 1111, 99999 )
#         self.unit = unit_factory()
#
#         self.obj = ComplexStatusRepository( MagicMock(), self.unit )
#
#     def test__handle_id( self ):
#         self.fail()
#
#     def test_load( self ):
#         self.fail()
#
#     def test_get_unit_records( self ):
#         self.fail()
#
#     def test_get_student( self ):
#         self.fail()
#
#     def test_create_record( self ):
#         self.fail()
#
#     def test_record_review_assignments_both_records_exist( self ):
#         self.obj.get_student_record = MagicMock( return_value=self.reviewing_student )
#
#         self.obj.record_review_assignments( (self.reviewing_student.student_id, self.reviewing_student.student_id) )
#
#     def test_record_review_assignments_reviewer_record_exists( self ):
#         self.fail()
#
#     def test_record_peer_review_results_sent( self ):
#         self.fail()
#
#     def test_record_metareview_results_sent( self ):
#         self.fail()
#


if __name__ == '__main__':
    unittest.main()
