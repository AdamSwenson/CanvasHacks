"""
Created by adam on 2/9/20
"""
__author__ = 'adam'

import os
import pandas as pd
from requests.exceptions import HTTPError

from CanvasHacks.Errors.messaging import MessageSendError
from CanvasHacks.Logging.decorators import log_message
from CanvasHacks.Messaging.interfaces import ISender
from CanvasHacks.Api.RequestTools import send_post_request
from CanvasHacks.Messaging.EmailerBase import ExchangeEmailer
from CanvasHacks import environment as env

if __name__ == '__main__':
    pass


class ExchangeMessageSender(ISender, ExchangeEmailer):
    """Handles sending messages through ms exchange email.

    This handles looking up the student email and then sending to them
.
    Doing via class allows easier mocking
    """

    def __init__(self, test=False, text_subtype='plain', student_repository=None):
        """
        :type student_repository: StudentRepository
        :param text_subtype Needs to be plain because if send html will hose the formatting
        """
        super().__init__(env.CONFIG.email_password, test=test, text_subtype=text_subtype)

        # Added student repo in CAN-86 so can use email address from canvas
        # instead of separate file
        self.student_repository = student_repository

        self.url = 'https://canvas.csun.edu/api/v1/conversations'
        self.sent_count = 0
        self.errors = []

    @property
    def error_count(self):
        return len(self.errors)

    def lookup_email(self, canvas_id):
        """Finds the student's email from their canvas id"""
        if self.student_repository is None:
            return self.emails.loc[canvas_id].email
        try:
            return self.student_repository.get_student_email(canvas_id)
        except Exception as e:
            # dev This needs to be removed after F25 since there will be no sheet
            print(f"Error retrieving student email from canvas for canvas id {canvas_id}. "
                  f"Attempting to use internal spreadsheet ")
            # dev This can be deprecated once CAN-86 is working
            emails_path = env.EMAIL_LIST_FILE
            self.emails = pd.read_excel(emails_path).set_index('canvas_id')
            return self.emails.loc[canvas_id].email

    @log_message
    def send(self, student_id, subject, body):
        """Sends a new message to the student.

       :param student_id : The student's csun id
       """
        try:
            email_address = self.lookup_email(student_id)

            self.sendMail(email_address, body, subject)

            self.sent_count += 1

        except Exception as e:
            self.errors.append(e)
            raise MessageSendError(e)


class ConversationMessageSender(ISender):
    """Handles sending messages through canvas's conversation
    interface.
    Doing via class allows easier mocking
    """

    def __init__(self):
        self.url = 'https://canvas.csun.edu/api/v1/conversations'
        self.sent_count = 0
        self.errors = []

    @property
    def error_count(self):
        return len(self.errors)

    def make_conversation_data(self, student_id, subject, body):
        """Creates the request data to be sent to canvas
        This was the source of the problem in CAN-77 (F24)
        """

        return {
            'recipients': [student_id],
            'body': body,
            'subject': subject,
            'force_new': True
        }

    def make_conversation_data_str(self, student_id, subject, body):
        """Creates the request data string to be appended to the url for sending to canvas"""
        return f"?recipients[]={student_id}&body={body}&subject={subject}&force_new=true"

    @log_message
    def send(self, student_id, subject, body):
        """Sends a new message to the student.
       Returns the result object which will contain the conversation id
       if needed for future use
       """
        try:
            d = self.make_conversation_data_str(student_id, subject, body)
            result = send_post_request(self.url + d, {})

            # d = self.make_conversation_data_str(student_id, subject, body)
            # result = send_post_request(self.url, d)

            # result.raise_for_status()
            self.sent_count += 1
            return result

        except (Exception, HTTPError) as e:
            self.errors.append(e)
            raise MessageSendError(e)


class DummyEmailSender(ExchangeMessageSender):
    """
    Mock for testing sending emails.
    """
    def init(self):
        self.outputs = []

    def send(self, student_id, subject, body):
        """Prints out what would've been sent.

       :param student_id : The student's csun id
       """
        email_address = self.lookup_email(student_id)

        out = f"""
        \n============================\n
        student id: {student_id}\n
        email : {email_address}\n
        subject : {subject}\n
        body: \n{body}
        \n============================\n
        """
        self.outputs.append(out)
        print(out)
        return out

# ---------------------- old

def make_conversation_data(student_id, subject, body):
    """Creates the request data to be sent to canvas"""
    return {
        'recipients': [student_id],
        'body': body,
        'subject': subject,
        'force_new': True
    }


@log_message
def send_message_to_student(student_id, subject, body):
    """Sends a new message to the student.
    Returns the result object which will contain the conversation id
    if needed for future use
    """
    d = make_conversation_data(student_id, subject, body)

    return send_post_request('https://canvas.csun.edu/api/v1/conversations', d)
