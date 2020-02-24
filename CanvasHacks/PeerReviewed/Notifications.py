"""
Created by adam on 12/26/19
"""
from CanvasHacks import environment as env
from CanvasHacks.Messaging.SendTools import send_message_to_student, ConversationMessageSender
from CanvasHacks.Messaging.templates import REVIEW_NOTICE_TEMPLATE, METAREVIEW_NOTICE_TEMPLATE, \
    METAREVIEW_CONTENT_TEMPLATE
from CanvasHacks.Models.student import get_first_name
from CanvasHacks.TimeTools import getDateForMakingFileName

__author__ = 'adam'

if __name__ == '__main__':
    pass


class SkaaMessenger:

    def __init__( self, activity, student_repository, content_repository ):
        self.student_repository = student_repository
        self.content_repository = content_repository
        self.activity = activity
        # Object responsible for actually sending message
        self.sender = ConversationMessageSender()

    def _make_message_data( self, receiving_student, content, other=None ):
        """
        Creates a dictionary with data to be passed to the
        method which actually sends the info to the receiving student
        """
        message = self._make_message_content( content, other, receiving_student )

        return {
            'student_id': receiving_student.id,
            'subject': self.activity.email_subject,
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
            'intro': self.activity.email_intro,

            'name': get_first_name( receiving_student ),

            # Formatted work for sending
            'responses': content,

            # Add any materials from me
            'other': other,

            # Add code and link to do reviewing assignment
            'review_assignment_name': self.activity.name,
            'access_code': self.activity.access_code,
            'review_url': self.activity.html_url,
            'due_date': self.activity.string_due_date
        }
        return d

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
                m = self.sender.send( **message_data )
                messages.append( m )
                # m = send_message_to_student( **message_data )
                print( m )
            else:
                # For test runs
                messages.append( message_data )
                print( message_data )
        # Returns for testing / auditing
        return messages


class StudentWorkForPeerReviewMessenger( SkaaMessenger ):
    """Handles sending message containg student work from the initial content assignment to the person who will conduct the peer review
    """

    def __init__( self, activity, student_repository, content_repository ):
        super().__init__( activity, student_repository, content_repository )
        self.message_template = REVIEW_NOTICE_TEMPLATE

    def prepare_message( self, review_assignment, other=None ):
        """This looks up the appropriate data for a review
        assignment and returns what will be the message body
        """
        try:
            # We are going to send the original work to the assessor
            # who will do the peer review
            receiving_student = self.student_repository.get_student_record( review_assignment.assessor_id )

            # The assessee did the work that we want to send
            # to the assessor
            content = self.content_repository.get_formatted_work_by( review_assignment.assessee_id )

            return self._make_message_data( receiving_student, content, other=None )

        except Exception as e:
            # todo exception handling
            print( e )


class FeedbackForMetareviewMessenger( SkaaMessenger ):
    """Handles sending message containg feedback from the peer reviewer
    to the person who was reviewed
    """

    def __init__( self, activity, student_repository, content_repository ):
        super().__init__( activity, student_repository, content_repository )
        self.message_template = METAREVIEW_NOTICE_TEMPLATE

    def prepare_message( self, review_assignment, other=None ):
        """This looks up the appropriate data for a review
        assignment and returns what will be the message body
        """
        try:
            # We are going to send the peer review feedback
            # created by the assessor to the student who was
            # assessed in the peer review stage
            receiving_student = self.student_repository.get_student_record( review_assignment.assessee_id )

            # The assessor did the work that we want to send
            # to the assessee
            content = self.content_repository.get_formatted_work_by( review_assignment.assessor_id )

            return self._make_message_data( receiving_student, content, other=None )

        except Exception as e:
            # todo exception handling
            print( e )


class FeedbackFromMetareviewMessenger( SkaaMessenger ):
    """Sends the contents of the metareview to the student who r
    did the initial peer review
    """

    def __init__( self, activity, student_repository, content_repository ):
        super().__init__( activity, student_repository, content_repository )
        self.message_template = METAREVIEW_CONTENT_TEMPLATE

    def prepare_message( self, review_assignment, other=None ):
        """This looks up the appropriate data for a review
        assignment and returns what will be the message body
        """
        try:
            # We are going to send the metareview feedback
            # created by the assessee to the student who did
            # the assessing in the peer review stage
            receiving_student = self.student_repository.get_student_record( review_assignment.assessor_id )

            # The assessor did the work that we want to send
            # to the assessee
            content = self.content_repository.get_formatted_work_by( review_assignment.assessee_id )

            return self._make_message_data( receiving_student, content, other=None )

        except Exception as e:
            # todo exception handling
            print( e )


# --------------------------------------- OLD

def make_prompt_and_response( response_list ):
    temp = """
            ------
    Prompt: {prompt}

    Their response:
    {response}
            ------
    """
    rs = [ temp.format( **r ) for r in response_list ]
    return " ".join( rs )


def make_notice( data ):
    """Should define
    name, responses, review_assignment_name, access_code
    """
    return REVIEW_NOTICE_TEMPLATE.format( **data )

# old
def make_metareview_notice( data ):
    return METAREVIEW_NOTICE_TEMPLATE.format( **data )

# old
def metareview_send_message_to_reviewers( review_assignments, studentRepo, contentRepo, activity, send=False ):
    # # Load list of ReviewAssociation objects representing who reviews whom
    # review_assigns = associationRepo.get_associations(activity)
    # print("loaded {} student reviewer assignments".format(len(review_assigns)))
    log_file = "{}/{}-metareview-message-log.txt".format( env.LOG_FOLDER, getDateForMakingFileName() )
    with open( log_file, 'a' ) as f:
        for rev in review_assignments:
            try:
                assessee = studentRepo.get_student_record( rev.assessee_id )

                content = contentRepo.get_formatted_work_by( rev.assessor_id )

                d = {
                    'intro': activity.email_intro,

                    'name': get_first_name( assessee ),

                    # Formatted work for sending
                    'responses': content,

                    # Add any materials from me
                    'other': '',

                    # Add code and link to do reviewing assignment
                    'review_assignment_name': activity.name,
                    'access_code': activity.access_code,
                    'review_url': activity.html_url,
                    'due_date': activity.string_due_date
                }

                message = make_notice( d )

                f.write( "\n=========\n {}".format( message ) )

                if send:
                    subject = activity.email_subject
                    m = send_message_to_student(
                        student_id=rev.assessee_id,
                        subject=subject,
                        body=message )
                    print( m )
                else:
                    print( message )
            except Exception as e:
                # todo Replace with raise LookupError and hook handler
                f.write( "\n=========\n {}".format( e ) )
                print( e )


def review_send_message_to_reviewers( review_assignments, studentRepo, contentRepo, activity, send=False ):
    # THIS IS UNUSABLE. MUST FIX ERROR

    # # Load list of ReviewAssociation objects representing who reviews whom
    # review_assigns = associationRepo.get_associations(activity)
    # print("loaded {} student reviewer assignments".format(len(review_assigns)))

    for rev in review_assignments:
        try:
            assessor = studentRepo.get_student_record( rev.assessor_id )

            content = contentRepo.get_formatted_work( rev.assessee_id )

            d = {
                'intro': activity.email_intro,

                'name': get_first_name( assessor ),

                # Formatted work for sending
                'responses': content,

                # Add any materials from me
                'other': '',

                # Add code and link to do reviewing assignment
                'review_assignment_name': activity.name,
                'access_code': activity.access_code,
                'review_url': activity.html_url,
                'due_date': activity.string_due_date
            }

            message = make_notice( d )

            if send:
                subject = activity.email_subject
                # fix this you fucking idiot
                m = send_message_to_student( student_id=rev.assessor_id, subject=subject, body=message )
                print( m )
            else:
                print( message )
        except Exception as e:
            # todo Replace with raise LookupError and hook handler
            print( e )
