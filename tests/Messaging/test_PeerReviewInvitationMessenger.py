"""
Created by adam on 2/22/20
"""
__author__ = 'adam'

from unittest.mock import MagicMock, patch

from faker import Faker

from CanvasHacks.Messaging.templates import REVIEW_NOTICE_TEMPLATE
from CanvasHacks.Messaging.skaa import PeerReviewInvitationMessenger
from CanvasHacks.Repositories.students import StudentRepository
from tests.TestingBase import TestingBase
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory
from tests.factories.RepositoryMocks import ContentRepositoryMock

fake = Faker()


class TestStudentWorkForPeerReviewMessenger( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        # self.activity_data = activity_data_factory()
        self.activity = self.unit.review #InitialWork( **self.activity_data )

        # student recieiving the message
        self.author = student_factory()
        self.reviewer = student_factory()

        # This would be the content unit
        self.work = fake.text()

        self.studentRepo = StudentRepository()
        self.studentRepo.get_student = MagicMock( return_value=self.reviewer )
        self.contentRepo = ContentRepositoryMock()
        self.contentRepo.get_formatted_work_by = MagicMock( return_value=self.work )
        self.review_assign = MagicMock( assessor_id=self.reviewer.id, assessee_id=self.author.id )
        self.statusRepo = MagicMock() #create_autospec(StatusRepository)

    def test_prepare_message( self ):
        # student recieiving the message
        self.obj = PeerReviewInvitationMessenger( self.unit, self.studentRepo, self.contentRepo, self.statusRepo )

        # call
        message_data = self.obj.prepare_message( self.review_assign )

        # print(message_data)

        # check
        self.assertEqual( self.obj.message_template, REVIEW_NOTICE_TEMPLATE, "Working off expected template" )
        self.assertEqual( message_data[ 'student_id' ], self.reviewer.id, "Receiving student id" )
        self.assertEqual( message_data[ 'subject' ], self.activity.email_subject, "Email subject" )
        self.assertTrue( len( message_data[ 'body' ] ) > 0 )

        # todo This relies on another method of the class, would be good to do this independently
        expected_content = self.obj._make_message_content( self.work, None, self.reviewer )
        self.assertEqual( expected_content, message_data[ 'body' ], "Expected message body" )

        # Super important: makes sure going to right person
        # We are sending the content unit out for review, so the
        #  receipient should be the REVIEWER
        self.studentRepo.get_student.assert_called_with(self.reviewer.id )

    @patch('CanvasHacks.Messaging.base.MessageLogger')
    @patch( 'CanvasHacks.Messaging.SendTools.ConversationMessageSender.send' )
    def test_notify( self, sendMock, loggerMock ):
        sendMock.return_value = 'this would be the result of sending'
        self.obj = PeerReviewInvitationMessenger( self.unit, self.studentRepo, self.contentRepo,  self.statusRepo )

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
        self.assertEqual( kwargs['student_id'], self.reviewer.id, "Sent to correct student" )
        self.assertEqual(kwargs['subject'], self.activity.email_subject, "Sent with expected subject line")
        d = self.obj._make_template_input( self.work, None, self.reviewer )
        b = REVIEW_NOTICE_TEMPLATE.format(**d)
        self.assertEqual(kwargs['body'], b, "Sent with expected body")

        # Super important: makes sure going to right person
        # We are sending the content unit out for review, so the
        #  receipient should be the REVIEWER
        self.studentRepo.get_student.assert_called_with(self.reviewer.id )

        self.statusRepo.record.assert_called()
        self.statusRepo.record.assert_called_with(self.reviewer.id)

        # self.obj.logger.write.assert_called()
