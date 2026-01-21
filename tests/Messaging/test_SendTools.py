from unittest import TestCase

from CanvasHacks.Messaging.SendTools import DummyEmailSender
from TestingBase import TestingBase


class TestDummyEmailSender(TestingBase):

    def setUp(self):
        self.config_for_test()

    def test_send(self):
        student_id = 4
        email_address = 'beep@beep.whap'
        subject = 'test'
        body = 'test body'
        expect = f"""
        \n============================\n
        student id: {student_id}\n
        email : {email_address}\n
        subject : {subject}\n
        body: \n{body}
        \n============================\n
        """

        object = DummyEmailSender()
        object.init()

        def fakelookup(p):
            return email_address

        object.lookup_email = fakelookup

        result = object.send(student_id, subject, body)
        self.assertEqual(result, expect)

