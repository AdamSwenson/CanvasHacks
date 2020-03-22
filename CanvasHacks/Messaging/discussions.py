"""
Created by adam on 2/28/20
"""
__author__ = 'adam'

from CanvasHacks.Errors.messaging import MessageDataCreationError
from CanvasHacks.Messaging.base import SkaaMessenger
from CanvasHacks.Messaging.templates import DISCUSSION_REVIEW_NOTICE_TEMPLATE, DISCUSSION_REVIEW_FEEDBACK_TEMPLATE
from CanvasHacks.Models.student import get_first_name
from CanvasHacks.Definitions.unit import Unit
from CanvasHacks.Repositories.status import StatusRepository

if __name__ == '__main__':
    pass


class DiscussionReviewInvitationMessenger( SkaaMessenger ):
    """Handles invitation to complete discussion review"""
    message_template = DISCUSSION_REVIEW_NOTICE_TEMPLATE

    def __init__( self, unit: Unit, student_repository, content_repository,
                  status_repositories: StatusRepository ):
        self.activity_inviting_to_complete = unit.discussion_review

        super().__init__( unit, student_repository, content_repository, status_repositories )

        # self.subject = "Discussion forum posts for you to review"
        # self.intro = "Here are some posts by another student for you to review. "

    def prepare_message( self, review_assignment, other=None ):
        """This looks up the appropriate data for a review
        unit and returns what will be the message body
        """
        try:
            # We are going to send the posts to the reviewer
            receiving_student = self.student_repository.get_student( review_assignment.assessor_id )

            # The assessee did the work (i.e., posts) that we want to send
            # to the assessor
            content = self.content_repository.get_formatted_work_by( review_assignment.assessee_id )

            return self._make_message_data( receiving_student, content, other=None )

        except Exception as e:
            # todo exception handling
            print( e )
            raise MessageDataCreationError( review_assignment )


class FeedbackFromDiscussionReviewMessenger( SkaaMessenger ):
    message_template = DISCUSSION_REVIEW_FEEDBACK_TEMPLATE
    email_subject_templ = "Feedback on your Unit {} discussion forum posts"
    intro = "Here is the feedback from another student on your discussion forum posts. "

    def __init__( self, unit: Unit, student_repository, content_repository,
                  status_repositories: StatusRepository ):

        # We will use the subject and intro
        # stored on this class rather than deferring to the activity
        self.activity_inviting_to_complete = None

        self.email_subject = self.email_subject_templ.format(unit.unit_number)

        super().__init__( unit, student_repository, content_repository, status_repositories )

    def prepare_message( self, review_assignment, other=None ):
        """This looks up the appropriate data for a review
        unit and returns what will be the message body
        """
        try:
            # todo

            # We are going to send the posts to the author of the posts
            receiving_student = self.student_repository.get_student( review_assignment.assessee_id )

            # We want the content produced by the reviewer
            content = self.content_repository.get_formatted_work_by( review_assignment.assessor_id )

            d = {
                'intro': self.intro,

                'name': get_first_name( receiving_student ),

                # Formatted work for sending
                'responses': content,

                # Add any materials from me
                'other': "",
            }

            body = self.message_template.format( **d )

            # can't use the usual self.make_message_data because won't have all the expected fields
            return {
                'student_id': receiving_student.id,
                'subject': self.email_subject,
                'body': body
            }

        except Exception as e:
            # todo exception handling
            print( e )
            raise MessageDataCreationError( review_assignment )