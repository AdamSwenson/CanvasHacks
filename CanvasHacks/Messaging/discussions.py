"""
Created by adam on 2/28/20
"""
__author__ = 'adam'

from CanvasHacks.Errors.messaging import MessageDataCreationError
from CanvasHacks.Messaging.base import SkaaMessenger
from CanvasHacks.Messaging.templates import DISCUSSION_REVIEW_NOTICE_TEMPLATE, DISCUSSION_REVIEW_FEEDBACK_TEMPLATE
from CanvasHacks.PeerReviewed.Definitions import Unit
from CanvasHacks.Repositories.status import StatusRepository

if __name__ == '__main__':
    pass


class DiscussionReviewInvitationMessenger( SkaaMessenger ):
    """Handles invitation to complete discussion review"""
    message_template = DISCUSSION_REVIEW_NOTICE_TEMPLATE

    def __init__( self, unit: Unit, student_repository, content_repository,
                  status_repository: StatusRepository ):
        self.activity_inviting_to_complete = unit.discussion_review

        super().__init__( unit, student_repository, content_repository, status_repository )

        self.subject = "Discussion forum posts for you to review"
        self.intro = "Here are some posts by another student for you to review. "

    def prepare_message( self, review_assignment, other=None ):
        """This looks up the appropriate data for a review
        unit and returns what will be the message body
        """
        try:
            # todo

            # We are going to send the posts to the reviewer
            receiving_student = self.student_repository.get_student( review_assignment.assessor_id )

            # The assessor did the work that we want to send
            # to the assessee
            content = self.content_repository.get_formatted_work_by( review_assignment.assessee_id )

            return self._make_message_data( receiving_student, content, other=None )

        except Exception as e:
            # todo exception handling
            print( e )
            raise MessageDataCreationError( review_assignment )


class FeedbackFromDiscussionReviewMessenger( SkaaMessenger ):
    message_template = DISCUSSION_REVIEW_FEEDBACK_TEMPLATE

    def __init__( self, unit: Unit, student_repository, content_repository,
                  status_repository: StatusRepository ):
        self.activity_inviting_to_complete = unit.discussion_review

        super().__init__( unit, student_repository, content_repository, status_repository )

        self.subject = "Discussion forum posts for you to review"
        self.intro = "Here are some posts by another student for you to review. "

    def prepare_message( self, review_assignment, other=None ):
        """This looks up the appropriate data for a review
        unit and returns what will be the message body
        """
        try:
            # todo

            # We are going to send the posts to the reviewer
            receiving_student = self.student_repository.get_student( review_assignment.assessee_id )

            # The assessor did the work that we want to send
            # to the assessee
            content = self.content_repository.get_formatted_work_by( review_assignment.assessor_id )

            return self._make_message_data( receiving_student, content, other=None )

        except Exception as e:
            # todo exception handling
            print( e )
            raise MessageDataCreationError( review_assignment )