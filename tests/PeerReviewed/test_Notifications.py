"""
Created by adam on 12/26/19
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from faker import Faker

from tests.TestingBase import TestingBase

fake = Faker()

from CanvasHacks.PeerReviewed.Notifications import *
from CanvasHacks.PeerReviewed.Definitions import *
from tests.factories.PeerReviewedFactories import activity_data_factory
from tests.factories.ModelFactories import student_factory
from CanvasHacks.Repositories.students import StudentRepository
from tests.factories.RepositoryMocks import ContentRepositoryMock

__author__ = 'adam'

if __name__ == '__main__':
    pass


def prompt_response_factory( number=3 ):
    return [ { 'prompt': fake.sentence(), 'response': fake.paragraph() } for _ in range( 0, number ) ]


class TestMake_conversation_data( TestCase ):
    def test_make_conversation_data( self ):
        self.fail()


class TestStudentNotices( TestCase ):

    def test_make_prompt_and_response( self ):
        w = prompt_response_factory()
        j = make_prompt_and_response( w )

        self.assertTrue( len( j ) > 1, "Created string is non empty" )

    def test_make_notice( self ):
        w = prompt_response_factory()
        d = { 'name': fake.name(),
              'response_list': w,
              'review_assignment_name': fake.job(),
              'access_code': fake.slug()
              }
        j = make_notice(d)
        # self.assertEquals(  j, 1, "Created string is non empty" )
        self.assertTrue( len( j ) > 1, "Created string is non empty" )


# def make_expected_message_data(activity, template, receiving_student, content, other=None):
#     d = {
#         'intro': activity.email_intro,
#
#         'name': get_first_name( receiving_student ),
#
#         # Formatted work for sending
#         'responses': content,
#
#         # Add any materials from me
#         'other': other,
#
#         # Add code and link to do reviewing assignment
#         'review_assignment_name': activity.name,
#         'access_code': activity.access_code,
#         'review_url': activity.html_url,
#         'due_date': activity.string_due_date
#     }
#
#     message = template.format( **d )


class TestSkaaMessenger(TestCase, TestingBase):

    def setUp(self):
        self.config_for_test()
        self.activity_data = activity_data_factory()
        self.activity = Activity(**self.activity_data)
        # student recieiving the message
        self.receiving_student = student_factory()
        self.reviewed_student_work = fake.text()

        self.studentRepo = StudentRepository()
        self.studentRepo.get_student = MagicMock( return_value=self.receiving_student )
        self.contentRepo = ContentRepositoryMock()

    def test__make_message_data(self):
        self.contentRepo.get_formatted_work_by = MagicMock(return_value=self.reviewed_student_work)
        review_assign = MagicMock( assessor_id=self.receiving_student.id )

        # parent class doesn't define message_template
        testing_template = """{intro} {name} {responses} {other} 
        {review_assignment_name} {access_code} {review_url} {due_date}
        """

        self.obj = SkaaMessenger(self.activity, self.studentRepo, self.contentRepo)

        self.obj.message_template = testing_template

        # Call
        result = self.obj._make_message_data( self.receiving_student, self.reviewed_student_work )

        # Check
        self.assertIsInstance(self.obj.student_repository, StudentRepository)
        expected_keys = ['student_id', 'subject', 'body']
        for k in result.keys():
            self.assertIn(k, expected_keys, "Result contains expected keys")

    # @patch('CanvasHacks.PeerReviewed.Notifications.ConversationMessageSender')
    # def test_notify( self, senderMock ):
    #     self.contentRepo.get_formatted_work_by = MagicMock(return_value=self.authors_work)
    #     review_assign = MagicMock( assessor_id=self.receiving_student.id )
    #
    #     # parent class doesn't define message_template
    #     testing_template = """{intro} {name} {responses} {other}
    #         {review_assignment_name} {access_code} {review_url} {due_date}
    #         """
    #
    #     self.obj = SkaaMessenger(self.activity, self.studentRepo, self.contentRepo)
    #
    #     self.obj.message_template = testing_template
    #
    #     # Call
    #     result = self.obj.notify([review_assign], send=True )
    #
    #     # Check
    #     # Only going to check most general things here. Specific stuff
    #     # like content and who gets what will be tested in
    #     # tests for child classes
    #     self.assertTrue(self.contentRepo.get_formatted_work_by.called, "Content repo method called")
    #     self.assertTrue(self.studentRepo.get_student_record.called, "Student repo method called")
    #     # Returned expected stuff
    #     self.assertTrue( len( result ) == 1, "Something was returned" )
    #     # Sender method called
    #     senderMock.send.assert_called()
