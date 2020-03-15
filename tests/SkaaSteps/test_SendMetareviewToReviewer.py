"""
Tests that the correct content will get
sent to the reviewer after the metareview is complete
Created by adam on 2/22/20
"""
__author__ = 'adam'

from unittest.mock import MagicMock, patch

import CanvasHacks.environment as env
import CanvasHacks.testglobals
from CanvasHacks.Models.status_record import StatusRecord, InvitationReceivedRecord, FeedbackReceivedRecord
from CanvasHacks.Repositories.status import FeedbackStatusRepository, InvitationStatusRepository
from factories.RepositoryMocks import ContentRepositoryMock
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory

CanvasHacks.testglobals.use_api = False

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from tests.TestingBase import TestingBase

from CanvasHacks.SkaaSteps.SendMetareviewToReviewer import SendMetareviewToReviewer

from faker import Faker

fake = Faker()


# Make sure correct students involved (have more than the 2 in db)
# Make sure correct text is sent
# Make sure addressing params are correct



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

    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.RunLogger' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.FeedbackFromMetareviewMessenger' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.AssociationRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.WorkRepositoryLoaderFactory' )
    def test_run( self, workLoaderMock, assocRepoMock, messengerMock, studentRepoMock, loggerMock ):
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
        obj = SendMetareviewToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )

        # call
        obj.run()

        # check
        workLoaderMock.make.assert_called()
        workLoaderMock.make.assert_called_with( self.unit.metareview, self.course) #, only_new=False, rest_timeout=5 )

        obj.studentRepo.download.assert_called()

        obj.associationRepo.get_by_assessee.assert_called()

        obj.messenger.notify.assert_called()
        obj.messenger.notify.assert_called_with( obj.associations, send )

        loggerMock.log_metareview_feedback_distributed.assert_called()


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
        obj = SendMetareviewToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )

        self.assertIsInstance(obj.statusRepos, list, "status repos is a list")
        self.assertTrue(len(obj.statusRepos) == 1)
        # self.assertIsInstance(obj.invite_status_repo, InvitationStatusRepository, "Invite repo instantiated")
        self.assertIsInstance( obj.feedback_status_repo, FeedbackStatusRepository, "Correct status repo instantiated" )



class TestFunctionalTests( TestingBase ):
    """Test that works using local data"""

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

    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.InvitationStatusRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.FeedbackStatusRepository' )
    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.WorkRepositoryLoaderFactory' )
    def test_run( self, workLoaderMock, studentRepoMock, messengerMock, feedbackStatusRepoMock, inviteStatusRepoMock ):

        # Prepare fake work repo to give values to calling  objects
        # workRepo = ContentRepositoryMock()
        # workRepo.create_test_content( self.student_ids )
        self.workRepo.submitter_ids = self.student_ids
        self.workRepo.remove_student_records = MagicMock()
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        # prepare student repo
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        # set up mocks on instantiated object
        obj = SendMetareviewToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
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
        self.assertEqual( len( obj.associations ), len( self.students ), "Correct number of students notified" )

        # Check that filtered previously notified
        # self.workRepo.remove_student_records.assert_called()

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, len( self.students ),
                          "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in messengerMock.call_args_list ]
        # print(args)

        # Status repo calls on messenger
        for repo in obj.messenger.status_repositories:
            repo.record.assert_called()
            # obj.messenger.status_repositories.record_invited.assert_called()
            call_list = repo.record.call_args_list
            # call_list = obj.messenger.status_repositories.record_invited.call_args_list
            status_args = [ c[ 0 ][ 0 ] for c in call_list ]
            self.assertEqual( len( self.students ), len( call_list ),
                              "Both status repos called expected number of times" )
            for sid in self.student_ids:
                self.assertIn( sid, status_args, "Both status repos called on all students" )

        # student repo calls on messenger
        for sid in self.student_ids:
            obj.messenger.student_repository.get_student.assert_any_call( sid )

        # Check the content sent
        for record in obj.associations:
            # print(record.assessee_id)
            review_text_by_author = self.workRepo.get_formatted_work_by( record.assessee_id )
            # see if sent to assessor
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessor_id ][ 0 ]
            rx = r'{}'.format( review_text_by_author )
            self.assertRegex( sent_text, rx, "Author's review of review in message sent to reviewer" )



    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.WorkRepositoryLoaderFactory' )
    def test_status_updated( self, workLoaderMock, studentRepoMock, messengerMock ):
        # Prepare fake work repo to give values to calling  objects
        # workRepo = ContentRepositoryMock()
        # workRepo.create_test_content( self.student_ids )
        self.workRepo.submitter_ids = self.student_ids
        self.workRepo.remove_student_records = MagicMock()
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        # prepare student repo
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        # set up mocks on instantiated object
        obj = SendMetareviewToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )

        # Have to do this after object creation so that we can use the
        # same in-memory db
        self.session = obj.dao.session
        # Sets up data for the association repo to use
        self.preexisting_pairings = self.create_preexisting_review_pairings( self.unit.initial_work.id, self.students )

        r = self.session.query(FeedbackReceivedRecord).filter(FeedbackReceivedRecord.activity_id == self.unit.review.id).all()
        self.assertTrue(len(r) == 0, "No sent feedback on review beforehand")
        r2 = self.session.query(InvitationReceivedRecord).filter(InvitationReceivedRecord.activity_id == self.unit.metareview.id).all()
        self.assertTrue(len(r) == 0, "No sent invitations to metareview beforehand")

        # call
        obj.run()

        # check
        self.assertEqual( len( obj.associations ), len( self.students ), "Correct number of students notified" )

        # check marked as sent
        for status_repo in obj.statusRepos:
            self.assertEqual( len(self.students), len( status_repo.previously_received), "all students have updated status" )

        # Check the content sent
        for record in obj.associations:
            # we need to check each of the reviewers to see that results has a value
            status_record = self.session\
                .query( FeedbackReceivedRecord )\
                .filter( FeedbackReceivedRecord.activity_id == self.unit.review.id )\
                .filter(FeedbackReceivedRecord.student_id == record.assessor_id)\
                .one_or_none()
            self.assertIsNotNone(status_record, "Feedback Record exists")
            self.assertIsNotNone(status_record.sent_at, "Value set for timestamp")

            # invite_status_record = self.session\
            #     .query( InvitationReceivedRecord )\
            #     .filter( InvitationReceivedRecord.activity_id == self.unit.metareview.id )\
            #     .filter(InvitationReceivedRecord.student_id == record.assessor_id)\
            #     .one_or_none()
            # self.assertIsNotNone(invite_status_record, "Invitation Record exists")
            # self.assertIsNotNone(invite_status_record.sent_at, "Value set for timestamp")


    # @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.FeedbackStatusRepository' )
    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.WorkRepositoryLoaderFactory' )
    def test_run_some_already_notified( self, workLoaderMock, studentRepoMock, messengerMock):
        # Set up status repo with some students already notified
        num_previously_sent = fake.random.randint( 1, len( self.students ) - 1 )
        previously_sent = self.student_ids[ : num_previously_sent ]
        # previously_sent = fake.random.choices(self.student_ids, k=num_previously_sent)
        to_notify = [ s for s in self.student_ids if s not in previously_sent ]
        num_to_notify = len( to_notify )
        # feedbackStatusRepoMock.previously_sent_result = MagicMock( return_value=previously_sent )

        # Prepare fake work repo to give values to calling  objects
        # workRepo = ContentRepositoryMock()
        # workRepo.create_test_content( self.student_ids )

        # prepare student repo
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        # set up mocks on instantiated object
        obj = SendMetareviewToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )

        # Have to do this after object creation so that we can use the
        # same in-memory db
        self.session = obj.dao.session
        # Sets up data for the association repo to use
        self.preexisting_pairings = self.create_preexisting_review_pairings( self.unit.initial_work.id, self.students )
        # Set up previous notifications

        for sid in previously_sent:
            obj.feedback_status_repo.record(sid)

        authors_with_notified_reviewers = [ r.assessee_id for r in self.preexisting_pairings if r.assessor_id in previously_sent ]
        authors_without_notified_reviewers = [ s for s in self.student_ids if s not in authors_with_notified_reviewers ]

        # have to fake this since using a dummy
        self.workRepo.submitter_ids = authors_without_notified_reviewers
        # workRepo.remove_student_records = MagicMock()
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        # call
        obj.run()

        # check
        self.assertEqual( num_to_notify, len( obj.associations ), "Correct number of students ({}) notified when {} have already been notified".format(len( obj.associations ), num_to_notify ) )

        # Check that filtered previously notified
        # Have to actually check repo.testText since can't mock
        # self.assertEqual( len( workRepo.testText ), num_to_notify )
        # for sid in previously_sent:
        #     self.assertNotIn( sid, workRepo.testText.keys() )
        # workRepo.remove_student_records.assert_called()
        # workRepo.remove_student_records.assert_called_with(previously_sent)

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, num_to_notify, "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in
                           messengerMock.call_args_list ]
        # print(args)

        # # Status repo calls on messenger
        # obj.messenger.status_repositories.record.assert_called()
        # # obj.messenger.status_repositories.record_invited.assert_called()
        # call_list = obj.messenger.status_repositories.record.call_args_list
        # # call_list = obj.messenger.status_repositories.record_invited.call_args_list
        # status_args = [ c[ 0 ][ 0 ] for c in call_list ]
        # self.assertEqual( num_to_notify, len( call_list ), "Status repo record called expected number of times" )
        # for sid in self.student_ids:
        #     if sid not in previously_sent:
        #         self.assertIn( sid, status_args, "StatusRepo.record called on non prev notified students" )
        #     else:
        #         self.assertNotIn( sid, status_args, "StatusRepo.record not called on prev notified students" )

        # student repo calls on messenger
        # this doesn't work because we record by who received
        # for sid in self.student_ids:
        #     if sid not in previously_sent:
        #         obj.messenger.student_repository.get_student.assert_any_call( sid )

        # Check the content sent
        for record in obj.associations:
            # print(record.assessee_id)
            review_text_by_author = self.workRepo.get_formatted_work_by( record.assessee_id )
            # see if sent to assessor
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessor_id ][ 0 ]
            rx = r'{}'.format( review_text_by_author )
            self.assertRegex( sent_text, rx, "Author's review of review in message sent to reviewer" )

    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.WorkRepositoryLoaderFactory' )
    def test_run_some_not_turned_in( self, workLoaderMock, studentRepoMock, messengerMock):
        # Set up status repo with some students already notified
        num_unsubmitted = fake.random.randint( 1, len( self.students ) - 1 )
        submitted = self.student_ids[ : num_unsubmitted ]
        # previously_sent = fake.random.choices(self.student_ids, k=num_previously_sent)
        to_notify = [ s for s in self.student_ids if s in submitted ]
        num_to_notify = len( to_notify )
        # feedbackStatusRepoMock.previously_sent_result = MagicMock( return_value=previously_sent )

        # Prepare fake work repo to give values to calling  objects
        # workRepo = ContentRepositoryMock()
        # workRepo.create_test_content( self.student_ids )
        self.workRepo.submitter_ids = to_notify
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        # prepare student repo
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        # set up mocks on instantiated object
        obj = SendMetareviewToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
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
        self.assertEqual( num_to_notify, len( obj.associations ), "Correct number of students ({}) notified when {} have already been notified".format(len( obj.associations ), num_to_notify ) )

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, num_to_notify, "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in messengerMock.call_args_list ]

        # Check the content sent
        for record in obj.associations:
            # get original author's feedback on their review
            review_text_by_author = self.workRepo.get_formatted_work_by( record.assessee_id )
            # see if sent to assessor
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessor_id ][ 0 ]
            rx = r'{}'.format( review_text_by_author )
            self.assertRegex( sent_text, rx, "Author's review of review in message sent to reviewer" )

