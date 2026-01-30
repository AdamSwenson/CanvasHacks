"""
Created by adam on 10/18/20
"""
__author__ = 'adam'
from unittest.mock import MagicMock, patch
from unittest import TestCase

import CanvasHacks.testglobals
from CanvasHacks.Models.review_association import ReviewAssociation
from CanvasHacks.Repositories.status import InvitationStatusRepository
from CanvasHacks.StudentNaggers.skaa_review import SkaaReviewNagger
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory
from tests.factories.RepositoryMocks import ContentRepositoryMock

CanvasHacks.testglobals.use_api = False
from CanvasHacks.Errors.review_pairings import AllAssigned, NoAvailablePartner

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from tests.TestingBase import TestingBase

from CanvasHacks.SkaaSteps.SendInitialWorkToReviewer import SendInitialWorkToReviewer
from faker import Faker

fake = Faker()


if __name__ == '__main__':
    pass



class TestSkaaReviewNagger( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.unit_number = fake.random_int()
        self.dao = SqliteDAO(self.unit_number)

        self.course = MagicMock()
        # review = Review(**activity_data_factory())
        self.unit = unit_factory()
        # self.unit.components.append(review)

        # _____________
        self.number_students = 3
        sr = { 'get_student_first_name.return_value': fake.first_name() }
        self.studentRepo = MagicMock( **sr )

        self.sids = [ fake.random.randint( 111111, 999999 ) for _ in range( 0, self.number_students ) ]
        ovr = { 'non_reviewed.reviewed_by_id.tolist.return_value': self.sids,
                'studentRepo': self.studentRepo }
        self.overviewRepo = MagicMock( **ovr )


    def test_recipients( self ):
        # passing in unit because won't get from the environment config as normal
        self.obj = SkaaReviewNagger( self.overviewRepo, unit=self.unit, is_test=True )

        result = self.obj.recipients

        self.assertEqual(len(result), self.number_students, "Correct number of receipents returned")


    @patch('CanvasHacks.StudentNaggers.skaa_review.ReviewNonSubmittersMessaging')
    def test_run( self, messenger ):
        send = False

        # passing in unit because won't get from the environment config as normal
        self.obj = SkaaReviewNagger( self.overviewRepo, course=self.course, unit=self.unit, is_test=True, send=send )

        # call
        self.obj.run()

        # Check
        # messenger created as expected
        self.assertEqual(self.unit, messenger.call_args[1]['unit'])
        self.assertEqual( self.obj.dao, messenger.call_args[ 1 ]['dao'], "Dao passed in as parameter"  )
        self.assertEqual( messenger.call_args[ 1 ]['send'], send, "Default "  )

        # messenger called expected times
        self.obj.messenger.send_message_to_student.assert_called()
        self.assertEqual(self.obj.messenger.send_message_to_student.call_count, self.number_students, "messenger called expected times")

