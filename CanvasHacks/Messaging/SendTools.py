"""
Created by adam on 2/9/20
"""
from CanvasHacks.Errors.messaging import MessageSendError
from CanvasHacks.Logging.decorators import log_message
from CanvasHacks.Messaging.interfaces import ISender
from CanvasHacks.Api.RequestTools import send_post_request

__author__ = 'adam'

if __name__ == '__main__':
    pass


class ConversationMessageSender( ISender ):
    """Handles sending messages through canvas's conversation
    interface.
    Doing via class allows easier mocking
    """

    def __init__( self ):
        self.url = 'https://canvas.csun.edu/api/v1/conversations'
        self.sent_count = 0
        self.errors = []

    @property
    def error_count( self ):
        return len(self.errors)

    def make_conversation_data( self, student_id, subject, body ):
        """Creates the request data to be sent to canvas"""
        return {
            'recipients': [ student_id ],
            'body': body,
            'subject': subject,
            'force_new': True
        }

    @log_message
    def send( self, student_id, subject, body ):
        """Sends a new message to the student.
       Returns the result object which will contain the conversation id
       if needed for future use
       """
        try:
            d = self.make_conversation_data( student_id, subject, body )
            result = send_post_request( self.url, d )
            self.sent_count += 1
            return result

        except Exception as e:
            self.errors.append(e)
            raise MessageSendError(e)


# ---------------------- old

def make_conversation_data( student_id, subject, body ):
    """Creates the request data to be sent to canvas"""
    return {
        'recipients': [ student_id ],
        'body': body,
        'subject': subject,
        'force_new': True
    }


@log_message
def send_message_to_student( student_id, subject, body ):
    """Sends a new message to the student.
    Returns the result object which will contain the conversation id
    if needed for future use
    """
    d = make_conversation_data( student_id, subject, body )

    return send_post_request( 'https://canvas.csun.edu/api/v1/conversations', d )
