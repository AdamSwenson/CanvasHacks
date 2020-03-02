"""
Created by adam on 2/22/20
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch, create_autospec

from CanvasHacks.Models.student import get_first_name
from CanvasHacks.Repositories.status import StatusRepository
from tests.TestingBase import TestingBase

from faker import Faker

from CanvasHacks.Messaging.templates import METAREVIEW_NOTICE_TEMPLATE
from CanvasHacks.PeerReviewed.Definitions import *
from CanvasHacks.Repositories.students import StudentRepository
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import activity_data_factory, unit_factory
from tests.factories.RepositoryMocks import ContentRepositoryMock

from CanvasHacks.Messaging.skaa import MetareviewInvitationMessenger

fake = Faker()

__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestFeedbackForMetareviewMessenger( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        self.activity = self.unit.metareview #InitialWork( **self.activity_data )

        # student recieiving the message
        self.author = student_factory()
        self.reviewer = student_factory()

        # This would be the results of the peer review
        self.work = fake.text()

        self.studentRepo = StudentRepository()
        self.studentRepo.get_student = MagicMock( return_value=self.reviewer )
        self.contentRepo = ContentRepositoryMock()
        self.contentRepo.get_formatted_work_by = MagicMock( return_value=self.work )
        self.statusRepo = create_autospec(StatusRepository)

        self.review_assign = MagicMock( assessor_id=self.reviewer.id, assessee_id=self.author.id )

    def test_prepare_message( self ):
        obj = MetareviewInvitationMessenger( self.unit, self.studentRepo, self.contentRepo, self.statusRepo )

        # call
        message_data = obj.prepare_message( self.review_assign )

        # check
        self.assertEqual( obj.message_template, METAREVIEW_NOTICE_TEMPLATE, "Working off expected template" )
        self.assertEqual( message_data[ 'student_id' ], self.reviewer.id, "Message is going to reviewer" )
        self.assertEqual( message_data[ 'subject' ], self.activity.email_subject, "Expected subject" )
        self.assertTrue( len( message_data[ 'body' ] ) > 0 )

        # todo This relies on another method of the class, would be good to do this independently
        expected_content = obj._make_message_content( self.work, None, self.reviewer )
        self.assertEqual( expected_content, message_data[ 'body' ], "Expected message body" )

        # Super important: makes sure going to right person
        # This is for the request to do the metareview, so the receipient should be the AUTHOR
        self.studentRepo.get_student.assert_called_with(self.author.id )

    @patch( 'CanvasHacks.Messaging.SendTools.ConversationMessageSender.send' )
    def test_notify( self, sendMock ):
        sendMock.return_value = 'taco'
        self.obj = MetareviewInvitationMessenger( self.unit, self.studentRepo, self.contentRepo, self.statusRepo )

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
        self.assertEqual(kwargs['subject'], self.unit.metareview.email_subject, "Sent with expected subject line ")

        # self.assertEqual(kwargs['subject'], self.FeedbackFromMetareviewMessenger.subject, "Sent with expected subject line -- remember this one is different")
        d = self.obj._make_template_input( self.work, None, self.reviewer )
        # d = {
        #     'intro': TestFeedbackForMetare,
        #
        #     'name': get_first_name( self.author.name ),
        #
        #     # Formatted work for sending
        #     'responses': self.work,
        #
        #     # Add any materials from me
        #     'other': "",
        # }
        b = METAREVIEW_NOTICE_TEMPLATE.format(**d)
        self.assertEqual(kwargs['body'], b, "Sent with expected body")

        # Super important: makes sure going to right person
        # This is for the request to do the metareview, so the receipient should be the AUTHOR
        self.studentRepo.get_student.assert_called_with(self.author.id )


