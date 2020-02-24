"""
Created by adam on 2/24/20
"""
from unittest import TestCase

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.PeerReviewed.Definitions import Unit
from tests import TestingBase

from unittest.mock import MagicMock, patch

from CanvasHacks.Repositories.status import StatusRepository


from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import activity_data_factory
from faker import Faker
fake = Faker()
import datetime
import pytz
from CanvasHacks.TimeTools import current_utc_timestamp


__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestStatusRepository( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.dao = SqliteDAO()
        print("Connected to testing db")
        self.session = self.dao.session

        self.activity_data = activity_data_factory()
        self.target_student = student_factory()
        self.reviewing_student = student_factory()
        self.reviewed_student = student_factory()
        self.activity_id = fake.random.randint(1111, 99999)
        self.unit = Unit(**self.activity_data)

        self.obj = StatusRepository(MagicMock(), self.unit)

    def test__handle_id( self ):
        self.fail()

    def test_load( self ):
        self.fail()

    def test_get_unit_records( self ):
        self.fail()

    def test_get_student( self ):
        self.fail()

    def test_create_record( self ):
        self.fail()

    def test_record_review_assignments_both_records_exist( self ):
        self.obj.get_student_record = MagicMock( return_value=self.reviewing_student )

        self.obj.record_review_assignments((self.reviewing_student.student_id,self.reviewing_student.student_id ))


    def test_record_review_assignments_reviewer_record_exists( self ):
        self.fail()

    def test_record_peer_review_results_sent( self ):
        self.fail()

    def test_record_metareview_results_sent( self ):
        self.fail()
