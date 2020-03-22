"""
Created by adam on 2/28/20
"""
__author__ = 'adam'

from CanvasHacks.Logging.messages import MessageLogger
from CanvasHacks.Messaging.SendTools import ConversationMessageSender
from CanvasHacks.Models.student import get_first_name
from CanvasHacks.Definitions.unit import Unit

if __name__ == '__main__':
    pass


class SkaaMessenger:

    def __init__( self, unit: Unit, student_repository, content_repository,
                  status_repositories: list ):
        """
        :param unit:
        :param student_repository:
        :param content_repository:
        :param status_repositories: List of status repos to call once sent
        """
        self.unit = unit
        self.student_repository = student_repository
        self.content_repository = content_repository

        # Object responsible for actually sending message
        self.sender = ConversationMessageSender()

        # Objects in charge of storing change in status
        # after sent. Should be a list of InvitationStatusRepository
        # or FeedbackStatusRepository objects
        self.status_repositories = status_repositories

        self.logger = MessageLogger()

    @property
    def sent_count( self ):
        return self.sender.sent_count

    @property
    def send_errors( self ):
        return self.sender.errors

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

            # Add code and link to do reviewing unit
            'review_assignment_name': self.activity_inviting_to_complete.name,
            'access_code_message': self._make_access_code_message(),
            'review_url': self.activity_inviting_to_complete.html_url,
            'due_date': self.activity_inviting_to_complete.string_due_date
        }
        return d

    def _make_access_code_message( self ):
        """Adds text with the access code for the next unit if a code
        exists otherwise returns an empty string
        """
        tmpl = "Here's the access code: {}"

        if self.activity_inviting_to_complete.access_code is not None:
            return tmpl.format( self.activity_inviting_to_complete.access_code )
        return ""

    def prepare_message( self, review_assignment, other=None ):
        """Creates the message data for sending specific to the unit"""
        raise NotImplementedError

    def notify( self, review_assignments, send=False, other=None ):
        """Given a list of review unit objects, sends the
        appropriate notification message to the correct person
        for the unit
        """
        messages = [ ]
        for rev in review_assignments:
            # print( rev )
            message_data = self.prepare_message( rev, other )
            # messages.append( message_data )

            if send:
                m = self.sender.send( **message_data )
                # todo Decide whether to keep the logging on the sender.send method or add the following here so all outgoing messages are written to file. NB, if uncomment this, will need to change to use to call class method
                # self.logger.write(m)

                messages.append( m )
                self.update_status( message_data )

            else:
                # For test runs
                messages.append( message_data )
                print( message_data )
        # Returns for testing / auditing
        return messages

    def update_status( self, message_data ):
        """
        Call the record method on all status repos
        :param message_data:
        :return:
        """
        if self.status_repositories is not None:
            # If was passed a single repo, make a list
            if not isinstance(self.status_repositories, list):
                self.status_repositories = [ self.status_repositories ]

            for status_repo in self.status_repositories:
                # Record status change (not to log)
                # records that the student has been invited or that they
                # have been sent feedback depending on the class
                status_repo.record( message_data[ 'student_id' ] )
