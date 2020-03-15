"""
Created by adam on 3/11/20
"""
__author__ = 'adam'

from unittest import TestCase

from CanvasHacks.Messaging.nagging import EssayNonSubmittersMessaging
from TestingBase import TestingBase
from factories.ModelFactories import student_factory
from factories.PeerReviewedFactories import unit_factory

from unittest.mock import patch, MagicMock

if __name__ == '__main__':
    pass


class TestEssayNonSubmittersMessaging( TestingBase ):
    def setUp(self):
        self.config_for_test()
        self.student = student_factory()
        self.unit = unit_factory()

    def test_prepare_message( self ):
        self.skipTest('todo')

    # @patch('CanvasHacks.Messaging.nagging.ConversationMessageSender')
    def test_send_message_to_student( self): #, messengerMock ):
        self.obj = EssayNonSubmittersMessaging( self.unit )
        self.obj.messenger = MagicMock()
        self.obj.messenger.send = MagicMock(return_value='taco')

        self.obj.send_message_to_student(self.student.student_id, self.student.first_name)

        self.obj.messenger.send.assert_called()

        # messengerMock.send.assert_called()

        # messengerMock.send.assert_called()
