"""
Created by adam on 12/26/19
"""
from CanvasHacks import environment as env
from CanvasHacks.Errors.messaging import MessageDataCreationError
from CanvasHacks.Messaging.SendTools import send_message_to_student
from CanvasHacks.Messaging.base import SkaaMessenger
from CanvasHacks.Messaging.templates import METAREVIEW_CONTENT_TEMPLATE,\
    METAREVIEW_NOTICE_TEMPLATE, REVIEW_NOTICE_TEMPLATE, REVIEW_FEEDBACK_ONLY_TEMPLATE
from CanvasHacks.Models.student import get_first_name
from CanvasHacks.Definitions.unit import Unit
from CanvasHacks.Repositories.status import StatusRepository, IStatusRepository
from CanvasHacks.TimeTools import getDateForMakingFileName

__author__ = 'adam'

if __name__ == '__main__':
    pass


class PeerReviewInvitationMessenger( SkaaMessenger ):
    """Handles sending message containg student work from the initial content unit
    to the person who will conduct the peer review
    """
    message_template = REVIEW_NOTICE_TEMPLATE

    email_subject_template = "Unit {}: Another student's essay to peer review "

    def __init__( self, unit: Unit, student_repository, content_repository,
                  status_repositories: IStatusRepository ):

        self.activity_inviting_to_complete = unit.review

        super().__init__( unit, student_repository, content_repository, status_repositories )
        # self.message_template = REVIEW_NOTICE_TEMPLATE

    def prepare_message( self, review_assignment, other=None ):
        """This looks up the appropriate data for a review
        unit and returns what will be the message body
        """
        try:
            # We are going to send the original work to the assessor
            # who will do the peer review
            receiving_student = self.student_repository.get_student( review_assignment.assessor_id )

            # The assessee did the work that we want to send
            # to the assessor
            #todo dev MASSIVE HOTFIX
            if env.CONFIG.course.id == 79991 and env.CONFIG.unit.unit_number == 1:
                print('In screwed up unit using Messaging/skaa line 48 hotfix')
                content = self.content_repository.data.loc[review_assignment.assessee_id].body
            else:
                content = self.content_repository.get_formatted_work_by( review_assignment.assessee_id )

            subject = self.email_subject_template.format(self.unit.unit_number)

            return self._make_message_data( receiving_student, content, other=None, subject=subject )

        except Exception as e:
            # todo exception handling
            print( e )
            raise MessageDataCreationError( review_assignment )




class MetareviewInvitationMessenger( SkaaMessenger ):
    """Handles sending message containing feedback from the peer reviewer
    to the author of the content assignment with invite to do metareview
    """
    message_template = METAREVIEW_NOTICE_TEMPLATE

    email_subject_template = "Unit {}: feedback on your essay and invitation to do the metareview"

    def __init__( self, unit: Unit, student_repository, content_repository,
                  status_repositories: StatusRepository ):

        # The activity we are notifying about
        self.activity_inviting_to_complete = unit.metareview

        super().__init__( unit, student_repository, content_repository, status_repositories )

    def prepare_message( self, review_assignment, other=None ):
        """This looks up the appropriate data for a review
        unit and returns what will be the message body
        """
        try:
            if review_assignment is None:
                raise MessageDataCreationError(review_assignment)

            # We are going to send the peer review feedback
            # created by the assessor to the student who was
            # assessed in the peer review stage
            receiving_student = self.student_repository.get_student( review_assignment.assessee_id )

            # The assessor did the work that we want to send
            # to the assessee
            content = self.content_repository.get_formatted_work_by( review_assignment.assessor_id )

            subject = self.email_subject_template.format(self.unit.unit_number )

            return self._make_message_data( receiving_student, content, other=None, subject=subject )

        except Exception as e:
            # todo exception handling
            print( e )
            raise MessageDataCreationError( review_assignment )


class FeedbackFromReviewMessenger(MetareviewInvitationMessenger):
    """
    FOR USE ONLY WHEN THERE IS NO METAREVIEW IN THE UNIT!!!!!!

    We inherit from metareview invitation so can use the same prepare_messages
    method while overwriting the methods on its parent which will require
    a value in activity_inviting_to_complete

    Sends the feedback to the original author with no request to complete
    the metareview
    """

    message_template = REVIEW_FEEDBACK_ONLY_TEMPLATE

    def __init__( self, unit: Unit, student_repository, content_repository,
                  status_repositories: StatusRepository ):

        super().__init__( unit, student_repository, content_repository, status_repositories )

        # The activity we are notifying about
        # Setting to None after the parent initializes so that can overwrite this value
        self.activity_inviting_to_complete = None


    def _make_message_data( self, receiving_student, content, subject=None, other=None ):
        """
        Creates a dictionary with data to be passed to the
        method which actually sends the info to the receiving student
        CAN-82: Added subject to params even though gets ignored so that will be
        consistent with parent, which hopefully fixes an error.
        """
        message = self._make_message_content( content, other, receiving_student )

        return {
            'student_id': receiving_student.id,
            'subject': "Feedback on your Unit {} Essay".format(self.unit.unit_number),
            'body': message
        }

    def _make_template_input( self, content, other, receiving_student ):
        """
        There will be no next assignment with many of the values the
        regular method uses

        Creates the dictionary that will be used to format the message template
        and create the message content
        This is abstracted out to make testing easier
        """

        d = {

            'intro': "Here is the feedback on your essay:",

            'name': get_first_name( receiving_student ),

            # Formatted work for sending
            'responses': content,

            # Add any materials from me
            'other': other if other is not None else "",

            # Add code and link to do reviewing unit
        }
        return d

    def _make_access_code_message( self ):
        """There will be no next assignment with an access code, so returns an empty string
        """
        return ""



class FeedbackFromMetareviewMessenger( SkaaMessenger ):
    """Sends the contents of the metareview to the student who r
    did the initial peer review
    """
    message_template = METAREVIEW_CONTENT_TEMPLATE

    subject = "Unit {}: Feedback on your peer review"

    intro = "Here is the feedback the author gave on your review of their essay. These are the answers they provided in filling out the metareview. "

    def __init__( self, unit: Unit, student_repository, content_repository,
                  status_repositories: IStatusRepository ):

        # None because sending feedback
        self.activity_inviting_to_complete = None

        super().__init__( unit, student_repository, content_repository, status_repositories )

        self.email_subject = self.subject.format(self.unit.unit_number)


    def prepare_message( self, review_assignment, other=None ):
        """This looks up the appropriate data for a review
        unit and returns what will be the message body
        """
        try:
            # We are going to send the metareview feedback
            # created by the assessee (original author) to the student who did
            # the assessing in the peer review stage
            receiving_student = self.student_repository.get_student( review_assignment.assessor_id )

            # The assessee (original author) did the work that we want to send
            # to the assessor (peer reviewer)
            content = self.content_repository.get_formatted_work_by( review_assignment.assessee_id )

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
    # review_assigns = associationRepo.get_associations(activity_inviting_to_complete)
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

                    # Add code and link to do reviewing unit
                    'review_assignment_name': activity.name,
                    'access_code': activity.access_code,
                    'review_url': activity.html_url,
                    'due_date': activity.string_due_date
                }

                message = make_notice( d )

                f.write( "\n=========\n {}".format( message ) )

                if send:
                    subject = activity.invitation_email_subject
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
    # review_assigns = associationRepo.get_associations(activity_inviting_to_complete)
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

                # Add code and link to do reviewing unit
                'review_assignment_name': activity.name,
                'access_code': activity.access_code,
                'review_url': activity.html_url,
                'due_date': activity.string_due_date
            }

            message = make_notice( d )

            if send:
                subject = activity.invitation_email_subject
                # fix this you fucking idiot
                m = send_message_to_student( student_id=rev.assessor_id, subject=subject, body=message )
                print( m )
            else:
                print( message )
        except Exception as e:
            # todo Replace with raise LookupError and hook handler
            print( e )
