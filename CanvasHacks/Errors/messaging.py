"""
Created by adam on 2/25/20
"""
from CanvasHacks.Models.model import StoreMixin

__author__ = 'adam'

if __name__ == '__main__':
    pass


class MessageDataCreationError(Exception, StoreMixin):
    """"Something went wrong in creating the data that would be
    used to format the message
    """
    def __init__( self, review_assignment, **kwargs ):
        self.review_assignment = review_assignment
        self.handle_kwargs(**kwargs)


class MessageSendError(Exception):
    """Wraps an error response from server when an
    attempt to send a message fails"""
    pass

class NoStudentsNeedNotification(Exception):
    """
    Raised when no students need to be notified
    for the current step
    """
    pass