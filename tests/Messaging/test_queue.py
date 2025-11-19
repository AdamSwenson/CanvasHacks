"""
Created by adam on 10/28/25
"""

from unittest.mock import MagicMock, patch

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Messaging.queue import QueuedMessageSender
from CanvasHacks.Models.message_queue import MessageQueueItem
from CanvasHacks.Repositories.students import StudentRepository
from TestingBase import TestingBase
from faker import Faker

from factories.ModelFactories import student_factory, message_queue_item_factory

fake = Faker()


class TestQueuedMessageSender(TestingBase):

    def setUp(self):
        self.dao = SqliteDAO()
        self.session = self.dao.session

        self.students = [student_factory() for i in range(0, 5)]

        # This would be the content unit
        self.work = fake.text()

        self.studentRepo = StudentRepository()
        self.studentRepo.get_student = MagicMock( return_value=self.students[0] )


    @patch('CanvasHacks.Messaging.base.MessageLogger')
    @patch( 'CanvasHacks.Messaging.SendTools.ExchangeMessageSender.send' )
    def test_send_all_empty_queue(self, mockSend, loggerMock,):
        obj = QueuedMessageSender(self.studentRepo, use_file_db=False)

        # call
        r = obj.send_all()

        # check
        self.assertFalse(r, "sender returns false on empty queue")
        self.assertFalse(mockSend.called, "Sender not called on empty queue")


    @patch('CanvasHacks.Repositories.messaging.MessageRepository')
    @patch( 'CanvasHacks.Messaging.SendTools.ExchangeMessageSender' )
    def test_send_all_stubbed(self, mockSend, mockMessageRepo): #, mockSend, loggerMock, mockDao):
        """nb, patches applied from bottom up"""
        # prep
        msgs = [message_queue_item_factory() for i in range(0, 5)]

        mockMessageRepo.get_message_queue.return_value = msgs
        mockMessageRepo.to_send_count = len(msgs)
        mockMessageRepo.all_to_send = msgs

        obj = QueuedMessageSender(self.studentRepo, use_file_db=False)
        obj.message_repository = mockMessageRepo  # MagicMock(return_value = 5)
        obj.sender = mockSend

        # call
        obj.send_all()

        # check
        self.assertEqual(mockSend.send.call_count, len(msgs), "Expected number of messages sent")

        ix = 0
        a = mockSend.send.call_args_list
        for m in msgs:
            self.assertEqual(m.student_id, a[ix][0][0], "Expected student ID")
            self.assertEqual(m.subject, a[ix][0][1], "Expected message subject")
            self.assertEqual(m.body, a[ix][0][2], "Expected message body")
            ix += 1

        self.assertEqual(mockMessageRepo.remove_from_queue.call_count, len(msgs), "Expected number of messages removed from queue")

        v = mockMessageRepo.remove_from_queue.call_args_list
        for mm in mockMessageRepo.remove_from_queue.call_args_list:
            k = mm[0][0]
            self.assertIn(k, msgs, "Expected message to be removed from queue")


    @patch('CanvasHacks.Messaging.base.MessageLogger')
    @patch( 'CanvasHacks.Messaging.SendTools.ExchangeMessageSender' )
    def test_send_all_integrated(self, mockSend, loggerMock):
        """Checks that pulls from db stored queue and calls send"""
        # prep
        msgs = [message_queue_item_factory() for i in range(0, 5)]
        [self.session.add(m) for m in msgs]
        self.session.commit()
        self.assertEqual(len(self.session.query(MessageQueueItem).all()), len(msgs), "Message queue populated")

        obj = QueuedMessageSender(self.studentRepo, use_file_db=False)
        obj.message_repository.session = self.session
        obj.sender = mockSend

        # call
        obj.send_all()

        # check
        self.assertEqual(mockSend.send.call_count, len(msgs), "Expected number of messages sent")

        for a in mockSend.send.call_args_list:
            sid = a[0][0]
            m = [s for s in msgs if s.student_id==sid][0]
            self.assertEqual(m.subject, a[0][1], "Expected subject ")
            self.assertEqual(m.body, a[0][2], "Expected body ")

        self.assertEqual(len(self.session.query(MessageQueueItem).all()), 0, "All messages removed from queue")


