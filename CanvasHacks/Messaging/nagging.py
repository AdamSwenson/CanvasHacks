"""
Created by adam on 3/11/20
"""
__author__ = 'adam'

from CanvasHacks.Messaging.SendTools import ConversationMessageSender, ExchangeMessageSender
from canvasapi.user import User

from CanvasHacks.Messaging.mixins import DateFormatterMixin
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from CanvasHacks.Repositories.status import InvitationStatusRepository

if __name__ == '__main__':
    pass

REVIEW_NON_SUBMITTER_TEMPLATE = """Hi {name},

I hope everything is okay with you. It looks like you haven't yet submitted the {assignment_name} which you were invited to complete on {invite_sent_date}.

This is a gentle nudge to please do this as soon as you have enough time to do a good job. The person you're reviewing is waiting for your feedback; they cannot do the metareview until you have completed the review. 

Please let me know if you have any questions or are having any trouble.

All best wishes,
/a

PS, If we've already spoken about this or if you've only recently been assigned the reviewing task, apologies for this semi-automated reminder. 
"""

ESSAY_NON_SUBMITTER_TEMPLATE = """Hi {name},

It looks like you haven't yet submitted the {assignment_name} which was due {original_due_date}. So I just wanted to check in to make sure everything is okay with you and give a very gentle nudge about this assignment.

No pressure. As always, the due dates for the essays are not strict and it's perfectly fine to take the time you need. Indeed, given the flexibility in due dates, no matter how far behind you are right now, it's still perfectly possible to get a good grade in the class ---with the exception of journals, it is possible to turn things in at the very end of the semester and get full credit for them.

Please let me know if you have any questions.

All best wishes,
/a

PS, If we've already spoken about this, apologies for this semi-automated reminder. 

"""


class EssayNonSubmittersMessaging(DateFormatterMixin):

    def __init__( self, unit, send=True, **kwargs ):
        """
        :param unit: The Unit object for the unit in question
        :param send: Whether to actually send the message to the student
        """
        self.send = send
        self.unit = unit
        self.activity = self.unit.initial_work

        # Changed to use email in CAN-78
        # self.messenger = ConversationMessageSender()
        self.messenger = ExchangeMessageSender()

        self.subject = "Missing Unit {} Essay".format( self.unit.unit_number )
        self.sent = [ ]

    def prepare_message( self, student_name ):
        data = {
            'name': student_name,
            'assignment_name': self.activity.name,
            'original_due_date': self.activity.string_due_date,
            'final_date': self.activity.string_lock_date
        }

        return ESSAY_NON_SUBMITTER_TEMPLATE.format( **data )

    def send_message_to_student( self, student_id, first_name ):
        """
        Populates the relevant template with the student's name and
        sends the message via canvas.
        If send was False when initialized, merely prints the text.
        :param student_id:
        :param first_name:
        :return:
        """

        # student_id = student.id if isinstance(student, User) else student.student_id
        body = self.prepare_message( first_name )
        if self.send:
            msg = self.messenger.send( student_id=student_id, subject=self.subject, body=body )
            self.sent.append( (student_id, msg) )
            print( msg )
        else:
            print("------------ Dry run EssayNonSubmitterNagger --------------")
            self.sent.append( (student_id, body) )
            print( body )


class ReviewNonSubmittersMessaging(DateFormatterMixin):
    SUBJECT_TEMPLATE = "Missing Unit {} Peer Review"

    def __init__( self, unit, send=True, dao=None ):
        """
        :param unit: The Unit object for the unit in question
        :param send: Whether to actually send the message to the student
        :param dao: The status repository object to use. If none, InvitationStatusRepository will be used
        """
        self.dao = dao
        self.send = send
        self.unit = unit
        self.activity = self.unit.review

        # Changed to use email in CAN-78
        # self.messenger = ConversationMessageSender()
        self.messenger = ExchangeMessageSender()

        self.subject = self.SUBJECT_TEMPLATE.format( self.unit.unit_number )
        self.sent = [ ]

        # Initialize the relevant status repo
        if self.dao is not None:
            self.invite_status_repo = InvitationStatusRepository( self.dao, self.activity )


    def prepare_message( self, student_name, student_id ):
        data = {
            'name': student_name,
            'assignment_name': self.activity.name,
            'original_due_date': self.activity.string_due_date,
            'invite_sent_date' : self.get_review_invitation_date( student_id )
        }

        return REVIEW_NON_SUBMITTER_TEMPLATE.format( **data )

    def get_review_invitation_date( self, student_id ):
        """
        Looks up when they were invited to complete the assignment
        and returns that date with the format yyyy-mm-dd or an empty string.
        :param student_id:
        :return:
        """
        # todo error handling needs to be added here so just returns empty string
        invite = self.invite_status_repo.get(student_id)
        return self.make_date_for_message(invite.sent_at)


    def send_message_to_student( self, student_id, first_name ):
        body = self.prepare_message( first_name, student_id )

        if self.send:
            msg = self.messenger.send( student_id=student_id, subject=self.subject, body=body )
            self.sent.append( (student_id, msg) )
            print( msg )
        else:
            print("------------ Dry run --------------")
            self.sent.append( (student_id, body) )
            print( body )
