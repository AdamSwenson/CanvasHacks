
# todo This should be an end-to-end integration test which actually hits the server

# todo Should check the case where no student is available to review

# """
# Assigns a randomly selected reviewer and sends them the work
#
# """
# import unittest
#
# from unittest.mock import MagicMock, patch
#
# from CanvasHacks.PeerReviewed.Definitions import Unit, Review
# from tests.factories.PeerReviewedFactories import activity_data_factory, unit_factory
# from tests.factories.ModelFactories import student_factory
# import CanvasHacks.globals
# CanvasHacks.globals.use_api = False
#
# from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
# from tests.TestingBase import TestingBase
#
# from CanvasHacks.SkaaSteps.SendInitialWorkToReviewer import SendInitialWorkToReviewer
#
#
# class TestOnTimeSubmissions(TestingBase ):
#     """Checks that works properly on first run after
#     deadline on work that has been submitted
#     """
#
#     def setUp(self):
#         self.config_for_test()
#         self.dao = SqliteDAO()
#
#         self.course = MagicMock()
#         # review = Review(**activity_data_factory())
#         self.unit = unit_factory()
#         # self.unit.components.append(review)
#
#     @patch('CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository')
#     @patch('CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.PeerReviewInvitationMessenger')
#     @patch('CanvasHacks.SkaaSteps.ISkaaSteps.AssociationRepository')
#     @patch('CanvasHacks.SkaaSteps.SendInitialWorkToReviewer.WorkRepositoryLoaderFactory')
#     def test_sends_correctly( self, workLoaderMock, assocRepoMock, messengerMock, studentRepoMock ):
#         """Check that each student receives the expected message
#         containing the correct student's submission
#         """
#         students = [student_factory(), student_factory()]
#         submitter_ids = [s.student_id for s in students]
#         workRepo = MagicMock()
#         workRepo.submitter_ids = submitter_ids
#         workLoaderMock.make = MagicMock(return_value=workRepo)
#
#         studentRepoMock.download = MagicMock(return_value=students)
#         send = True
#         obj = SendInitialWorkToReviewer(course=self.course, unit=self.unit, is_test=True, send=True)
#
#         # call
#         obj.run()
#
#         # check
#         workLoaderMock.make.assert_called()
#         workLoaderMock.make.assert_called_with(self.unit.initial_work, self.course, True)
#
#         obj.studentRepo.download.assert_called()
#
#         obj.associationRepo.assign_reviewers.assert_called()
#         obj.associationRepo.assign_reviewers.assert_called_with(submitter_ids)
#
#         obj.messenger.notify.assert_called()
#         obj.messenger.notify.assert_called_with(obj.associationRepo.data, send)
#
#
#
#     #
#     # def test_assignments_stored_correctly( self ):
#     #     """Check that the students who have submitted the unit
#     #     (and none of the non-submitteers) have been paired up
#     #     in the expected manner, and that the pairings have been stored
#     #     """
#     #     self.fail()
#
#
# class TestLateSubmissions( TestingBase ):
#     """Checks that works properly on subsequent runs after the
#     initial assignments have been sent out
#
#     """
#
#     def test_sends_correctly( self ):
#         """Check that each student receives the expected message
#         containing the correct student's submission
#         """
#         self.fail()
#
#     def test_review_pairings_made_correctly( self ):
#         """Check that the students who have submitted the unit
#         (and none of the non-submitteers) have been paired up
#         in the expected manner, and that the pairings have been stored
#         """
#         self.fail()
#
#     def test_original_review_pairings_are_unaffected( self ):
#         """Check that the review assignments which were created
#         on the earlier run(s) have not been altered when the
#         new review assignments were made
#         """
#         self.fail()
#
#
# if __name__ == '__main__':
#     unittest.main()
