"""
Created by adam on 2/28/20
"""
__author__ = 'adam'

from CanvasHacks.Logging.messages import MessageLogger
from CanvasHacks.Messaging.SendTools import ConversationMessageSender
from CanvasHacks.Models.student import get_first_name
from CanvasHacks.PeerReviewed.Definitions import Unit
from CanvasHacks.Repositories.status import StatusRepository

if __name__ == '__main__':
    pass


class SkaaMessenger:

    def __init__( self, unit: Unit, student_repository, content_repository,
                  status_repository: StatusRepository ):
        """
        :param unit:
        :param student_repository:
        :param content_repository:
        :param status_repository:
        """
        self.unit = unit
        self.student_repository = student_repository
        self.content_repository = content_repository
        # self.activity_inviting_to_complete = activity_inviting_to_complete
        # Object responsible for actually sending message
        self.sender = ConversationMessageSender()
        # Objec in charge of logging statuses
        self.status_repository = status_repository
        self.logger = MessageLogger()

    def _make_message_data( self, receiving_student, content, other=None ):
        """
        Creates a dictionary with data to be passed to the
        method which actually sends the info to the receiving student
        """
        message = self._make_message_content( content, other, receiving_student )

        return {
            'student_id': receiving_student.id,
            'subject': self.activity_inviting_to_complete.email_subject,
            'body': message
        }

    def _make_message_content( self, content, other, receiving_student ):
        d = self._make_template_input( content, other, receiving_student )
        message = self.message_template.format( **d )
        # message = make_notice( d )
        return message

    def _make_template_input( self, content, other, receiving_student ):
        """Creates the dictionary that will be used to format the message template
        and create the message content
        This is abstracted out to make testing easier
        """

        d = {
            'intro': self.activity_inviting_to_complete.email_intro,

            'name': get_first_name( receiving_student ),

            # Formatted work for sending
            'responses': content,

            # Add any materials from me
            'other': other if other is not None else "",

            # Add code and link to do reviewing assignment
            'review_assignment_name': self.activity_inviting_to_complete.name,
            'access_code_message': self._make_access_code_message(),
            'review_url': self.activity_inviting_to_complete.html_url,
            'due_date': self.activity_inviting_to_complete.string_due_date
        }
        return d

    def _make_access_code_message( self ):
        """Adds text with the access code for the next assignment if a code
        exists otherwise returns an empty string
        """
        tmpl = "Here's the access code: {}"

        if self.activity_inviting_to_complete.access_code is not None:
            return tmpl.format( self.activity_inviting_to_complete.access_code )
        return ""

    def prepare_message( self, review_assignment, other=None ):
        """Creates the message data for sending specific to the assignment"""
        raise NotImplementedError

    def notify( self, review_assignments, send=False, other=None ):
        """Given a list of review assignment objects, sends the
        appropriate notification message to the correct person
        for the assignment
        """
        messages = [ ]
        for rev in review_assignments:
            # print( rev )
            message_data = self.prepare_message( rev, other )
            # messages.append( message_data )

            if send:
                # m = send_message_to_student( **message_data )
                m = self.sender.send( **message_data )
                # todo Decide whether to keep the logging on the sender.send method or add the following here so all outgoing messages are written to file. NB, if uncomment this, will need to change to use to call class method
                # self.logger.write(m)

                messages.append( m )
                # Record status change (not to log)
                if self.status_repository is not None:
                    self.status_repository.record( message_data[ 'student_id' ] )
                    # if isinstance(self.content_repository.activity, Metareview):
                    # For the peer review, the reviewer will be marked as notified
                    # For the metareview the author will be marked as notified
                    # self.status_repository.record_opened( message_data[ 'student_id' ] )
                print( "Message sent", m )
            else:
                # For test runs
                messages.append( message_data )
                print( message_data )
        # Returns for testing / auditing
        return messages