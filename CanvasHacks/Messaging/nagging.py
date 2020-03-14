"""
Created by adam on 3/11/20
"""
__author__ = 'adam'

from CanvasHacks.Messaging.SendTools import ConversationMessageSender
from canvasapi.user import User

if __name__ == '__main__':
    pass

REVIEW_NON_SUBMITTER_TEMPLATE = """
Hi {name},

I hope everything is okay with you. It looks like you haven't yet submitted the {assignment_name} which was due {original_due_date}.

Please do this as soon as possible. The person you were assigned to review is waiting for your feedback; they cannot do the metareview until you have completed this assignment.

Please let me know if you have any questions. And, please, please, please get this turned in.

All best wishes,
/a

PS, If we've already spoken about this or if you've only recently been assigned the reviewing task, apologies for this automated reminder. 
"""


ESSAY_NON_SUBMITTER_TEMPLATE = """
Hi {name},

I hope everything is okay with you. It looks like you haven't yet submitted the {assignment_name} which was due {original_due_date}.

Missing one of these assignments means also missing points from the peer review and metareview. Thus I have re-opened the assignment until 11.59PM on {final_date}. Please take advantage of this and turn it in!

Once you turn it in, please let me know. If someone else has turned it in late (and you are definitely not the only one), I will pair you up so you can complete the review and metareview before 11.59PM on {final_date}

Please let me know if you have any questions. And, please, please, please get this turned in. I want you to succeed in this class!

All best wishes,
/a

PS, If we've already spoken about this, apologies for this automated reminder. 

"""

class EssayNonSubmittersMessaging:

    def __init__(self, unit, send=True):
        self.send = send
        self.unit = unit
        self.activity = self.unit.initial_work
        self.messenger = ConversationMessageSender()
        self.subject = "Missing Unit {} Essay".format(self.unit.unit_number)
        self.sent = []

    def prepare_message( self, student_name ):
        data = {
            'name': student_name,
            'assignment_name': self.activity.name,
            'original_due_date': self.activity.string_due_date,
            'final_date' : self.activity.string_lock_date
        }

        return ESSAY_NON_SUBMITTER_TEMPLATE.format(**data)

    def send_message_to_student( self, student_id, first_name):

        # student_id = student.id if isinstance(student, User) else student.student_id
        body = self.prepare_message(first_name)
        if self.send:
            msg = self.messenger.send(student_id=student_id, subject=self.subject, body=body)
            self.sent.append( (student_id, msg) )
            print( msg )
        else:
            self.sent.append((student_id, body))
            print(body)


class ReviewNonSubmittersMessaging:

    def __init__(self, unit, send=True):
        self.send = send
        self.unit = unit
        self.activity = self.unit.review
        self.messenger = ConversationMessageSender()
        self.subject = "Missing Unit {} Peer Review".format(self.unit.unit_number)
        self.sent = []

    def prepare_message( self, student_name ):
        data = {
            'name': student_name,
            'assignment_name': self.activity.name,
            'original_due_date': self.activity.string_due_date,
        }

        return REVIEW_NON_SUBMITTER_TEMPLATE.format(**data)

    def send_message_to_student( self, student_id, first_name):

        # student_id = student.id if isinstance(student, User) else student.student_id
        body = self.prepare_message(first_name)
        if self.send:
            msg = self.messenger.send(student_id=student_id, subject=self.subject, body=body)
            self.sent.append( (student_id, msg) )
            print( msg )
        else:
            self.sent.append((student_id, body))
            print(body)
