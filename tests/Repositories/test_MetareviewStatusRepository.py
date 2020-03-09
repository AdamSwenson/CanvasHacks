# """
# Created by adam on 3/8/20
# """
# __author__ = 'adam'
#
# from unittest import TestCase
#
# from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
# from CanvasHacks.Repositories.status import MetareviewStatusRepository, InvitationStatusRepository,\
#     FeedbackStatusRepository
# from TestingBase import TestingBase
# from factories.PeerReviewedFactories import unit_factory
#
# if __name__ == '__main__':
#     pass
#
#
# class TestMetareviewStatusRepository( TestingBase ):
#     def setUp(self):
#         self.config_for_test()
#         self.unit = unit_factory()
#         self.activity = self.unit.discussion_forum
#         self.activity_id = self.activity.id
#
#         self.dao = SqliteDAO()
#         self.session = self.dao.session
#         self.create_new_and_preexisting_students()
#
#         self.obj = MetareviewStatusRepository( self.dao, self.unit )
#
#     def test_initialization( self ):
#         self.assertEqual(self.obj.feedback_activity, self.unit.initial_work, "Recording that feedback on initial work being sent")
#         self.assertIsInstance(self.obj.feedback_repo, FeedbackStatusRepository, "Correct feedback repo instantiated")
#
#         self.assertEqual(self.obj.invitation_activity, self.unit.metareview, "Recording that being invited to complete metareview")
#         self.assertIsInstance(self.obj.invite_repo, InvitationStatusRepository, "Correct feedback repo instantiated")
#
#
#     def test_record( self ):
#         self.fail()
