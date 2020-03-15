"""
Created by adam on 3/13/20
"""
__author__ = 'adam'

from CanvasHacks.Messaging.SendTools import ConversationMessageSender

if __name__ == '__main__':
    pass

WAITING_ON_REVIEWER_TEMPLATE = """
Hi {name},

I just wanted to let you know that the person assigned to review your essay assignment has not yet turned it in. 

I will send it to you as soon as they turn it in so that you can do the metareview assignment. 

If they do not turn it in before the metareview assignment is due, you will receive full credit for the metareview.

All best wishes,
/a

"""


class StudentsWaitingOnReviewerMessaging:

    def __init__( self, unit, send=True ):
        self.send = send
        self.unit = unit
        self.activity = self.unit.review
        self.messenger = ConversationMessageSender()
        self.subject = "Waiting for your reviewer to complete the review...".format( self.unit.unit_number )
        self.sent = [ ]


    def prepare_message( self, student_name ):
        data = {
            'name': student_name,
            'assignment_name': self.activity.name,
            # 'original_due_date': self.activity.string_due_date,
            # 'final_date': self.activity.string_lock_date
        }

        return WAITING_ON_REVIEWER_TEMPLATE.format( **data )


    def send_message_to_student( self, student_id, first_name ):
        # student_id = student.id if isinstance(student, User) else student.student_id
        body = self.prepare_message( first_name )
        if self.send:
            msg = self.messenger.send( student_id=student_id, subject=self.subject, body=body )
            self.sent.append( (student_id, msg) )
            print( msg )
        else:
            self.sent.append( (student_id, body) )
            print( body )
