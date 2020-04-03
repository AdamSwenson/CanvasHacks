"""
Created by adam on 2/23/20
"""

__author__ = 'adam'

from CanvasHacks.Models.student import get_first_name
from CanvasHacks.Repositories.status import FeedbackStatusRepository

if __name__ == '__main__':
    pass

"""
Created by adam on 2/22/20
"""
from tests.TestingBase import TestingBase
from unittest.mock import MagicMock, patch, create_autospec

from faker import Faker

from CanvasHacks.Messaging.templates import METAREVIEW_CONTENT_TEMPLATE
from CanvasHacks.Repositories.students import StudentRepository

from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory
from tests.factories.RepositoryMocks import ContentRepositoryMock

from CanvasHacks.Messaging.skaa import FeedbackFromMetareviewMessenger

fake = Faker()

__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestFeedbackFromMetareviewMessenger( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        # self.activity_data = activity_data_factory()
        self.activity = self.unit.metareview #InitialWork( **self.activity_data )

        self.author = student_factory()
        # student receiving the message (we are sending the feedback
        # created by the author of the content assignment)
        self.reviewer = student_factory()

        # This would be metareview feedback on the review
        self.work = fake.text()

        self.studentRepo = StudentRepository()
        self.studentRepo.get_student = MagicMock( return_value=self.reviewer )
        self.contentRepo = ContentRepositoryMock()
        self.contentRepo.get_formatted_work_by = MagicMock( return_value=self.work )

        self.review_assign = MagicMock( assessor_id=self.reviewer.id, assessee_id=self.author.id )
        self.statusRepo = create_autospec(FeedbackStatusRepository)

    def test_prepare_message( self ):
        obj = FeedbackFromMetareviewMessenger( self.unit, self.studentRepo, self.contentRepo, self.statusRepo )

        # call
        message_data = obj.prepare_message( self.review_assign )

        # check
        self.assertEqual( obj.message_template, METAREVIEW_CONTENT_TEMPLATE, "Working off expected template" )
        self.assertEqual( message_data[ 'student_id' ], self.reviewer.id, "Message is going to reviewer (it contains the feedback from the original author)" )
        self.assertEqual( message_data[ 'subject' ], FeedbackFromMetareviewMessenger.subject.format(self.unit.unit_number), "Sent with expected subject line (This is different from the tests of its siblings" )

        self.assertTrue( len( message_data[ 'body' ] ) > 0 )

        d = {
            'intro': FeedbackFromMetareviewMessenger.intro,
            # the person who did the review is getting feedback from the author
            'name': get_first_name( self.reviewer ),

            # Formatted work for sending
            'responses': self.work,

            # Add any materials from me
            'other': "",
        }
        expected_content = METAREVIEW_CONTENT_TEMPLATE.format( **d )

        self.assertEqual( expected_content, message_data[ 'body' ], "Expected message body" )

        # Super important: makes sure going to right person
        # This is for the metareview, so the receipient should be the REVIEWER
        self.studentRepo.get_student.assert_called_with(self.reviewer.id )

    @patch( 'CanvasHacks.Messaging.SendTools.ConversationMessageSender.send' )
    def test_notify( self, sendMock ):
        sendMock.return_value = 'taco'
        self.obj = FeedbackFromMetareviewMessenger( self.unit, self.studentRepo, self.contentRepo, self.statusRepo )

        # Call
        result = self.obj.notify( [ self.review_assign ], send=True )

        # Check
        # Intermediate things were called
        self.assertTrue(self.contentRepo.get_formatted_work_by.called, "Content repo method called")
        self.assertTrue(self.studentRepo.get_student.called, "Student repo method called")
        # Returned expected stuff
        self.assertTrue( len( result ) == 1, "Something was returned" )

        # Check that the sender was given the expected content
        sendMock.assert_called()
        kwargs = sendMock.call_args[1 ]
        self.assertEqual( kwargs['student_id'], self.reviewer.id, "Sent to reviewer" )
        self.assertEqual(kwargs['subject'], FeedbackFromMetareviewMessenger.subject.format(self.unit.unit_number), "Sent with expected subject line (This is different from the tests of its siblings" )
        d = {
            'intro': FeedbackFromMetareviewMessenger.intro,
            # the person who did the review is getting feedback from the author
            'name': get_first_name( self.reviewer ),

            # Formatted work for sending
            'responses': self.work,

            # Add any materials from me
            'other': "",
        }
        # d = self.obj._make_template_input( self.work, None, self.reviewer )
        b = METAREVIEW_CONTENT_TEMPLATE.format(**d)
        self.assertEqual(kwargs['body'], b, "Sent with expected body")

        # Super important: makes sure going to right person
        # This is for the metareview, so the receipient should be the REVIEWER
        self.studentRepo.get_student.assert_called_with(self.reviewer.id )

        # Check that status repo called
        self.statusRepo.record.assert_called()
        self.statusRepo.record.assert_called_with( self.reviewer.id )
