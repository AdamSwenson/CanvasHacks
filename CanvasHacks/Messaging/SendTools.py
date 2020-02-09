"""
Created by adam on 2/9/20
"""
from CanvasHacks.RequestTools import send_post_request
from CanvasHacks.Logging import log_message

__author__ = 'adam'

if __name__ == '__main__':
    pass


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

