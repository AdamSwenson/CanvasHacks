"""
Created by adam on 3/2/20
"""
__author__ = 'adam'

from unittest.mock import MagicMock, patch

from faker import Faker

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Repositories.status import InvitationStatusRepository
from CanvasHacks.SkaaSteps.SendForumPostsToReviewer import SendForumPostsToReviewer
from tests.TestingBase import TestingBase
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory
from tests.factories.RepositoryMocks import ContentRepositoryMock

fake = Faker()

if __name__ == '__main__':
    pass


class TestUnitTests( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        self.activity = self.unit.discussion_forum
        self.course = MagicMock()

        # student recieiving the message
        self.author = student_factory()
        self.reviewer = student_factory()

        # This would be the content unit
        self.work = fake.text()
        # Set to none so that loader thinks not a quiz
        self.activity_id = self.unit.discussion_forum.id
        self.dao = SqliteDAO()
        self.session = self.dao.session
        self.create_new_and_preexisting_students()
        # Prepare fake work repo to give values to calling  objects

        # self.studentRepo = StudentRepository()
        # self.studentRepo.get_student = MagicMock( return_value=self.reviewer )
        self.contentRepo = ContentRepositoryMock()
        self.contentRepo.get_formatted_work_by = MagicMock( return_value=self.work )
        self.review_assign = MagicMock( assessor_id=self.reviewer.id, assessee_id=self.author.id )
        self.statusRepo = MagicMock()
        # Prepare fake work repo to give values to calling  objects
        self.workRepo = ContentRepositoryMock()
        self.workRepo.create_test_content( self.student_ids )
        self.workRepo.add_students_to_data( self.student_ids, make_dataframe=True )

    def test_instantiates_correct_status_repo( self ):
        """The sending of metareview results requires a
        special status repository"""
        obj = SendForumPostsToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
        self.assertEqual(len(obj.statusRepos), 1, "expected number of status repos")
        self.assertIsInstance( obj.statusRepos[0], InvitationStatusRepository,
                               "Correct status repo instantiated" )

    def test__message_step( self ):
        self.skipTest( "todo" )

    def test__assign_step( self ):
        self.skipTest( "todo" )

    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.DisplayManager' )
    @patch( 'CanvasHacks.SkaaSteps.SendForumPostsToReviewer.WorkRepositoryLoaderFactory' )
    def test__load_step( self, workLoaderMock, displayManagerMock ):
        self.workRepo.remove_student_records = MagicMock()
        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        obj = SendForumPostsToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )

        # call
        obj._load_step()

        # check
        workLoaderMock.make.assert_called()
        displayManagerMock.assert_called()

        call_args = [ c[ 0 ][ 0 ] for c in workLoaderMock.call_args_list ]
        # print( call_args )
        # self.assertEqual()


class TestFunctionalTests( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.unit = unit_factory()
        self.activity = self.unit.discussion_forum
        self.course = MagicMock()

        # student recieiving the message
        self.author = student_factory()
        self.reviewer = student_factory()

        # This would be the content unit
        self.work = fake.text()
        # Set to none so that loader thinks not a quiz
        self.activity_id = self.unit.discussion_forum.id
        self.dao = SqliteDAO()
        self.session = self.dao.session
        self.create_new_and_preexisting_students()
        # Prepare fake work repo to give values to calling  objects

        # self.studentRepo = StudentRepository()
        # self.studentRepo.get_student = MagicMock( return_value=self.reviewer )
        self.contentRepo = ContentRepositoryMock()
        self.contentRepo.get_formatted_work_by = MagicMock( return_value=self.work )
        self.review_assign = MagicMock( assessor_id=self.reviewer.id, assessee_id=self.author.id )
        self.statusRepo = MagicMock()
        # Prepare fake work repo to give values to calling  objects
        self.workRepo = ContentRepositoryMock()
        self.workRepo.create_test_content( self.student_ids )
        self.workRepo.add_students_to_data( self.student_ids, make_dataframe=True )

    @patch( 'CanvasHacks.SkaaSteps.SendForumPostsToReviewer.InvitationStatusRepository' )
    @patch( 'CanvasHacks.Messaging.base.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendForumPostsToReviewer.WorkRepositoryLoaderFactory' )
    def test_run( self, workLoaderMock, studentRepoMock, messengerMock, statusRepoMock ):
        self.workRepo.submitter_ids = self.new_students_ids

        workLoaderMock.make = MagicMock( return_value=self.workRepo )

        # prepare student repo
        students = { s.student_id: s for s in self.students }

        def se( sid ):
            return students.get( sid )

        # studentRepoMock.get_student = MagicMock(side_effect=se)
        # studentRepoMock.download = MagicMock( return_value=self.students )

        # call
        obj = SendForumPostsToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )
        # obj.studentRepo = MagicMock()
        obj.studentRepo.get_student = MagicMock( side_effect=se )
        obj.studentRepo.download = MagicMock( return_value=self.students )
        preexisting_pairings = self.create_preexisting_review_pairings( self.activity_id, self.preexisting_students,
                                                                        obj.dao.session )

        obj.run()

        # check
        self.assertEqual( len( obj.associations ), len( self.new_students_ids ),
                          "Correct number of students assigned" )

        # Check that new assignments don't involve previously assigned sudents
        for rec in obj.associations:
            self.assertNotIn( rec.assessor_id, self.preexisting_student_ids,
                              "Newly assigned assessor not among previously assigned students" )
            self.assertNotIn( rec.assessee_id, self.preexisting_student_ids,
                              "Newly assigned assessee not among previously assigned students" )

        # Check whether each new student has been assigned
        new_assessor_ids = [ r.assessor_id for r in obj.associations ]
        new_assessee_ids = [ r.assessee_id for r in obj.associations ]
        self.assertEqual( len( set( new_assessor_ids ) ), len( self.new_students_ids ),
                          "No duplicate assessor assignments" )
        self.assertEqual( len( set( new_assessee_ids ) ), len( self.new_students_ids ),
                          "No duplicate assessee assignments" )
        for sid in self.new_students_ids:
            self.assertIn( sid, new_assessee_ids, "Student is an assessee" )
            self.assertIn( sid, new_assessor_ids, "Student is an assessor" )

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, len( self.new_students_ids ),
                          "Send method called expected number of times" )
        messenger_args = [ (c[ 1 ][ 'student_id' ], c[ 1 ][ 'subject' ], c[ 1 ][ 'body' ]) for c in
                           messengerMock.call_args_list ]
        # print(args)

        # Check that all messages have the correct subject
        for sid, subj, body in messenger_args:
            self.assertEqual( self.unit.discussion_review.email_subject, subj, "Correct subject line" )

        # Status repo calls on messenger
        obj.messenger.status_repositories[0].record.assert_called()
        call_list = obj.messenger.status_repositories[0].record.call_args_list

        # obj.messenger.status_repositories.record_invited.assert_called()
        # call_list = obj.messenger.status_repositories.record_invited.call_args_list
        status_args = [ c[ 0 ][ 0 ] for c in call_list ]
        self.assertEqual( len( self.new_students ), len( call_list ),
                          "Status repo record_invited called expected number of times" )
        for sid in self.new_students_ids:
            self.assertIn( sid, status_args, "StatusRepo.record_invited called on all students" )

        # student repo calls on messenger
        for sid in self.new_students_ids:
            obj.messenger.student_repository.get_student.assert_any_call( sid )

        # Check the content sent
        for record in obj.associations:
            # print(record.assessee_id)
            author_text = self.workRepo.get_formatted_work_by( record.assessee_id )
            # see if sent to assessor
            sent_text = [ t[ 2 ] for t in messenger_args if t[ 0 ] == record.assessor_id ][ 0 ]
            rx = r'{}'.format( author_text )
            self.assertRegex( sent_text, rx, "Author's work in message sent to reviewer" )

    def test_audit_frame( self ):
        self.skipTest( "todo" )
