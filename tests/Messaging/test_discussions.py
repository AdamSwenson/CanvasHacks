"""
Created by adam on 3/2/20
"""
__author__ = 'adam'

from unittest.mock import MagicMock, create_autospec, patch

from CanvasHacks.Messaging.discussions import DiscussionReviewInvitationMessenger
from CanvasHacks.Repositories.status import StatusRepository
from CanvasHacks.Repositories.students import StudentRepository
from factories.ModelFactories import student_factory
from factories.PeerReviewedFactories import unit_factory
from factories.RepositoryMocks import ContentRepositoryMock
from tests.TestingBase import TestingBase

if __name__ == '__main__':
    pass
from CanvasHacks.Messaging.templates import DISCUSSION_REVIEW_NOTICE_TEMPLATE
from faker import Faker

fake = Faker()


class TestDiscussionReviewInvitationMessenger( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()

        self.activity = self.unit.discussion_review

        # student recieiving the message
        self.author = student_factory()
        self.reviewer = student_factory()

        # This would be metareview feedback on the review
        self.work = fake.text()

        self.studentRepo = StudentRepository()
        self.studentRepo.get_student = MagicMock( return_value=self.reviewer )
        self.contentRepo = ContentRepositoryMock()
        self.contentRepo.get_formatted_work_by = MagicMock( return_value=self.work )

        self.review_assign = MagicMock( assessor_id=self.reviewer.id, assessee_id=self.author.id )
        self.statusRepo = create_autospec( StatusRepository )

    def test_prepare_message( self ):
        obj = DiscussionReviewInvitationMessenger( self.unit, self.studentRepo, self.contentRepo, self.statusRepo )

        # call
        message_data = obj.prepare_message( self.review_assign )

        # check
        self.assertEqual( obj.message_template, DISCUSSION_REVIEW_NOTICE_TEMPLATE, "Working off expected template" )
        self.assertEqual( message_data[ 'student_id' ], self.reviewer.id, "Message is going to reviewer" )
        self.assertEqual( message_data[ 'subject' ], self.activity.email_subject, "Email subject" )

        self.assertTrue( len( message_data[ 'body' ] ) > 0 )

        d = obj._make_template_input( self.work, None, self.reviewer )

        expected_content = DISCUSSION_REVIEW_NOTICE_TEMPLATE.format( **d )

        self.assertEqual( expected_content, message_data[ 'body' ], "Expected message body" )

        # Super important: makes sure going to right person
        # This is for the metareview, so the receipient should be the REVIEWER
        self.studentRepo.get_student.assert_called_with( self.reviewer.id )

    @patch( 'CanvasHacks.Messaging.SendTools.ConversationMessageSender.send' )
    def test_notify( self, sendMock ):
        sendMock.return_value = 'taco'
        self.obj = DiscussionReviewInvitationMessenger( self.unit, self.studentRepo, self.contentRepo, self.statusRepo )

        # Call
        result = self.obj.notify( [ self.review_assign ], send=True )

        # Check
        # Intermediate things were called
        self.assertTrue( self.contentRepo.get_formatted_work_by.called, "Content repo method called" )
        self.assertTrue( self.studentRepo.get_student.called, "Student repo method called" )
        # Returned expected stuff
        self.assertTrue( len( result ) == 1, "Something was returned" )

        # Check that the sender was given the expected content
        sendMock.assert_called()
        kwargs = sendMock.call_args[ 1 ]
        self.assertEqual( kwargs[ 'student_id' ], self.reviewer.id, "Sent to reviewer" )
        self.assertEqual( kwargs[ 'subject' ], self.activity.email_subject, "Sent with expected subject line" )

        d = self.obj._make_template_input( self.work, None, self.reviewer )
        b = DISCUSSION_REVIEW_NOTICE_TEMPLATE.format( **d )
        self.assertEqual( kwargs[ 'body' ], b, "Sent with expected body" )

        # Super important: makes sure going to right person
        # This is for the metareview, so the receipient should be the REVIEWER
        self.studentRepo.get_student.assert_called_with( self.reviewer.id )
