"""
Created by adam on 2/22/20
"""
__author__ = 'adam'
import CanvasHacks.globals
CanvasHacks.globals.use_api = False
import unittest
from unittest.mock import MagicMock, patch
from tests.TestingBase import TestingBase

from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory
from tests.factories.RepositoryMocks import ContentRepositoryMock

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO

from CanvasHacks.SkaaSteps.SendReviewToReviewee import SendReviewToReviewee

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
    @patch( 'CanvasHacks.SkaaSteps.SendReviewToReviewee.FeedbackForMetareviewMessenger' )
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

        # call
        obj.run()

        # check
        workLoaderMock.make.assert_called()
        workLoaderMock.make.assert_called_with( self.unit.review, self.course, True )

        obj.studentRepo.download.assert_called()

        obj.messenger.notify.assert_called()
        obj.messenger.notify.assert_called_with( obj.associationRepo.data, send )


class TestFunctionalTests( TestingBase ):
    """Checks that works properly on first run after
    deadline on work that has been submitted
    """
    def setUp(self):
        self.config_for_test()
        self.unit = unit_factory()
        self.course = MagicMock()
        self.activity_id = self.unit.review.id
        self.dao = SqliteDAO()
        self.session = self.dao.session
        self.create_new_and_preexisting_students()

    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StatusRepository' )
    @patch( 'CanvasHacks.Messaging.Messengers.ConversationMessageSender.send' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendReviewToReviewee.WorkRepositoryLoaderFactory' )
    def test_run( self, workLoaderMock, studentRepoMock, messengerMock, statusRepoMock  ):
        self.preexisting_pairings = self.create_preexisting_review_pairings(self.activity_id, self.students)

        # Prepare fake work repo to give values to calling  objects
        workRepo = ContentRepositoryMock()
        workRepo.create_test_content(self.student_ids)
        workRepo.submitter_ids = self.student_ids
        workLoaderMock.make = MagicMock( return_value=workRepo )

        # prepare student repo
        students = { s.student_id : s for s in self.students}

        def se(sid):
            return students.get(sid)

        # call
        obj = SendReviewToReviewee( course=self.course, unit=self.unit, is_test=True, send=True )
        obj.studentRepo.get_student = MagicMock(side_effect=se)
        obj.studentRepo.download = MagicMock( return_value=self.students )

        obj.run()

        # check
        self.assertEqual( len( obj.associations ), len( self.students ), "Correct number of students notified" )

        # ================== Events on Messenger
        # Check that mocked objects were called with expected data
        messengerMock.assert_called()
        self.assertEqual( messengerMock.call_count, len( self.students ), "Send method called expected number of times" )
        messenger_args = [ (c[1]['student_id'], c[1]['subject'], c[ 1 ]['body']) for c in messengerMock.call_args_list ]
        # print(args)

        # Status repo calls on messenger
        obj.messenger.status_repository.record_opened.assert_called()
        call_list = obj.messenger.status_repository.record_opened.call_args_list
        status_args = [c[0][0] for c in call_list]
        self.assertEqual(len(self.students), len(call_list),  "Status repo record_opened called expected number of times")
        for sid in self.students:
            self.assertIn(sid, status_args, "StatusRepo.record_opened called on all students")

        # student repo calls on messenger
        for sid in self.students:
            obj.messenger.student_repository.get_student.assert_any_call(sid)

        # Check the content sent
        for record in obj.new_assignments:
            # print(record.assessee_id)
            author_text = workRepo.get_formatted_work_by(record.assessee_id)
            # see if sent to assessee
            sent_text = [t[2] for t in messenger_args if t[0] == record.assessee_id][0]
            rx = r'{}'.format(author_text)
            self.assertRegex(sent_text, rx, "Author's work in message sent to reviewee")


if __name__ == '__main__':
    unittest.main()
