"""
Created by adam on 2/22/20
"""
__author__ = 'adam'

import CanvasHacks.testglobals
from CanvasHacks.Repositories.status import StatusRepository, FeedbackStatusRepository, InvitationStatusRepository

CanvasHacks.testglobals.use_api = False
import unittest
from unittest.mock import MagicMock, patch
from tests.TestingBase import TestingBase

from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory
from tests.factories.RepositoryMocks import ContentRepositoryMock

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO

from CanvasHacks.SkaaSteps.SendReviewToReviewee import SendReviewToReviewee
import CanvasHacks.environment as env
from faker import Faker

fake = Faker()


class TestCallsAllExpected( TestingBase ):
    """Makes sure that everything gets called with expected values.
       Not super diagnostic since many of the mocked calls are
       where we'd actually expect failure. Still, useful for catching
       problems when update code etc"""

    def setUp( self ):
        self.config_for_test()
        self.dao = SqliteDAO()

        self.course = MagicMock()
        self.unit = unit_factory()

    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendReviewToReviewee.MetareviewInvitationMessenger' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.AssociationRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendReviewToReviewee.WorkRepositoryLoaderFactory' )
    def test_run( self, workLoaderMock, assocRepoMock, messengerMock, studentRepoMock ):
        """Check that each student receives the expected message
        containing the correct student's submission
        """
        students = [ student_factory(), student_factory() ]
        submitter_ids = [ s.student_id for s in students ]
        workRepo = MagicMock()
        workRepo.submitter_ids = submitter_ids
        workLoaderMock.make = MagicMock( return_value=workRepo )

        studentRepoMock.download = MagicMock( return_value=students )
        send = True
        obj = SendReviewToReviewee( course=self.course, unit=self.unit, is_test=True, send=True )
        # ra = ReviewAssociation(assessor_id=students[0], assessee_id=students[1])
        # obj.associationRepo.get_assessor_object = MagicMock(return_value=[ra])

        # call
        obj.run()

        # check
        workLoaderMock.make.assert_called()
        workLoaderMock.make.assert_called_with( self.unit.review, self.course) # only_new=False, rest_timeout=5 )

        obj.studentRepo.download.assert_called()

        obj.messenger.notify.assert_called()
        obj.messenger.notify.assert_called_with( obj.associations, send )


class TestUnitTests(TestingBase):
    """Unit tests with all dependencies mocked"""
    def setUp( self ):
        self.config_for_test()
        env.CONFIG.semester_name = "T30"
        self.unit = unit_factory()
        self.course = MagicMock()
        self.activity_id = self.unit.review.id
        # self.dao = SqliteDAO()
        self.create_new_and_preexisting_students()
        # Prepare fake work repo to give values to calling  objects
        self.workRepo = ContentRepositoryMock()
        self.workRepo.create_test_content( self.student_ids )
        self.workRepo.add_students_to_data(self.student_ids, make_dataframe=True)

    def test_instantiates_correct_status_repos( self ):
        """The sending of metareview results requires a
        special status repository"""
        obj = SendReviewToReviewee( course=self.course, unit=self.unit, is_test=True, send=True )

        self.assertIsInstance(obj.statusRepos, list, "status repos is a list")
        self.assertTrue(len(obj.statusRepos) == 2)
        self.assertIsInstance(obj.invite_status_repo, InvitationStatusRepository, "Invite repo instantiated")
        self.assertIsInstance( obj.feedback_status_repo, FeedbackStatusRepository, "Correct status repo instantiated" )




class TestFunctionalTests( TestingBase ):
    """Checks that works properly on first run after
    deadline on work that has been submitted
    """

    def setUp( self ):
        self.config_for_test()
        env.CONFIG.semester_name = "T30"
        self.unit = unit_factory()
        self.course = MagicMock()
        self.activity_id = self.unit.review.id
        # self.dao = SqliteDAO()
        self.create_new_and_preexisting_students()
        # Prepare fake work repo to give values to calling  objects
        self.workRepo = ContentRepositoryMock()
        self.workRepo.create_test_content( self.student_ids )
        self.workRepo.add_students_to_data(self.student_ids, make_dataframe=True)

    @patch( 'CanvasHacks.SkaaSteps.SendReviewToReviewee.InvitationStatusRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendReviewToReviewee.FeedbackStatusRepository' )
    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendReviewToReviewee.WorkRepositoryLoaderFactory' )
    def test_run( self, workLoaderMock, studentRepoMock, messengerMock, statusRepoMock, inviteStatusRepoMock ):

        # Prepare fake work repo to give values to calling  objects
        workRepo = ContentRepositoryMock()
        workRepo.create_test_content( self.student_ids )
        workRepo.submitter_ids = self.student_ids
        workRepo.remove_student_records = MagicMock()
        workLoaderMock.make = MagicMock( return_value=workRepo )

        # prepare student repo
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        # call
        obj = SendReviewToReviewee( course=self.course, unit=self.unit, is_test=True, send=True )
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )

        # Have to do this after object creation so that we can use the
        # same in-memory db
        self.session = obj.dao.session
        # Sets up data for the association repo to use
        self.preexisting_pairings = self.create_preexisting_review_pairings( self.unit.initial_work.id, self.students )

        obj.run()

        # check
        self.assertEqual( len( obj.associations ), len( self.students ), "Correct number of students notified" )

        # Check that filtered previously notified
        workRepo.remove_student_records.assert_called()

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, len( self.students ),
                          "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in
                           messengerMock.call_args_list ]
        # Check that all messages have the correct subject
        for sid, subj, body in messenger_args:
            self.assertEqual(self.unit.metareview.email_subject, subj, "Correct subject line")

        # Status repo calls on messenger
        for repo in obj.messenger.status_repositories:
            repo.record.assert_called()
            # obj.messenger.status_repositories.record_invited.assert_called()
            call_list = repo.record.call_args_list
            # call_list = obj.messenger.status_repositories.record_invited.call_args_list
            status_args = [ c[ 0 ][ 0 ] for c in call_list ]
            self.assertEqual( len( self.students ), len( call_list ),
                              "Status repo record called expected number of times" )
            for sid in self.student_ids:
                self.assertIn( sid, status_args, "Record called on both repos for all students" )

        # student repo calls on messenger
        for sid in self.student_ids:
            obj.messenger.student_repository.get_student.assert_any_call( sid )

        # Check the content sent
        for record in obj.associations:
            # print(record.assessee_id)
            reviewer_text = workRepo.get_formatted_work_by( record.assessor_id )
            # see if sent to assessee
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessee_id ][ 0 ]
            rx = r'{}'.format( reviewer_text )
            self.assertRegex( sent_text, rx, "Reviewer's work in message sent to author" )

    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendReviewToReviewee.WorkRepositoryLoaderFactory' )
    def test_run_some_already_notified( self, workLoaderMock, studentRepoMock, messengerMock ):
        # Set up status repo with some students already notified
        num_previously_sent = fake.random.randint( 1, len( self.students ) - 1 )
        previously_sent = self.student_ids[ : num_previously_sent ]
        # previously_sent = fake.random.choices(self.student_ids, k=num_previously_sent)
        to_notify = [ s for s in self.student_ids if s not in previously_sent ]
        num_to_notify = len( to_notify )

        # Prepare fake work repo to give values to calling  objects
        workRepo = ContentRepositoryMock()
        workRepo.create_test_content( self.student_ids )

        # prepare student repo
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        # set up mocks on instantiated object
        obj = SendReviewToReviewee( course=self.course, unit=self.unit, is_test=True, send=True )
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )

        # Have to do this after object creation so that we can use the
        # same in-memory db
        self.session = obj.dao.session
        # Sets up data for the association repo to use
        self.preexisting_pairings = self.create_preexisting_review_pairings( self.unit.initial_work.id, self.students )

        reviewers_without_prev_notified_authors = [s.assessor_id for s in self.preexisting_pairings if s.assessee_id not in previously_sent]

        # setting this since filter step doesn't happen on dummy
        workRepo.submitter_ids = reviewers_without_prev_notified_authors
        # workRepo.remove_student_records = MagicMock()
        workLoaderMock.make = MagicMock( return_value=workRepo )

        # Set up previous notifications
        for sid in previously_sent:
            obj.feedback_status_repo.record( sid )

        # call
        obj.run()

        # check
        self.assertEqual( num_to_notify, len( obj.associations ), "Correct number of students notified" )

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, num_to_notify, "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in messengerMock.call_args_list ]

        # Check the content sent
        for record in obj.associations:
            # print(record.assessee_id)
            reviewer_text = workRepo.get_formatted_work_by( record.assessor_id )
            # see if sent to assessee
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessee_id ][ 0 ]
            rx = r'{}'.format( reviewer_text )
            self.assertRegex( sent_text, rx, "Reviewer's work in message sent to author" )

    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendReviewToReviewee.WorkRepositoryLoaderFactory' )
    def test_run_some_not_turned_in( self, workLoaderMock, studentRepoMock, messengerMock ):
        # Set up status repo with some students already notified
        num_unsubmitted = fake.random.randint( 1, len( self.students ) - 1 )
        submitted = self.student_ids[ : num_unsubmitted ]
        # previously_sent = fake.random.choices(self.student_ids, k=num_previously_sent)
        to_notify = [ s for s in self.student_ids if s in submitted ]
        num_to_notify = len( to_notify )
        # feedbackStatusRepoMock.previously_sent_result = MagicMock( return_value=previously_sent )

        # Prepare fake work repo to give values to calling  objects
        workRepo = ContentRepositoryMock()
        workRepo.create_test_content( self.student_ids )
        workRepo.submitter_ids = to_notify
        workLoaderMock.make = MagicMock( return_value=workRepo )

        # prepare student repo
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        # set up mocks on instantiated object
        obj = SendReviewToReviewee( course=self.course, unit=self.unit, is_test=True, send=True )
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )

        # Have to do this after object creation so that we can use the
        # same in-memory db
        self.session = obj.dao.session
        # Sets up data for the association repo to use
        self.preexisting_pairings = self.create_preexisting_review_pairings( self.unit.initial_work.id, self.students )

        # call
        obj.run()

        # check
        self.assertEqual( num_to_notify, len( obj.associations ), "Correct number of students notified" )

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, num_to_notify, "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in messengerMock.call_args_list ]

        # Check the content sent
        for record in obj.associations:
            # print(record.assessee_id)
            reviewer_text = workRepo.get_formatted_work_by( record.assessor_id )
            # see if sent to assessee
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessee_id ][ 0 ]
            rx = r'{}'.format( reviewer_text )
            self.assertRegex( sent_text, rx, "Reviewer's work in message sent to author" )


if __name__ == '__main__':
    unittest.main()
