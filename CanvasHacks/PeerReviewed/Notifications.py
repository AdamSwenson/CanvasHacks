"""
Created by adam on 12/26/19
"""
from CanvasHacks.Logging import log_message
from CanvasHacks.Messaging.SendTools import send_message_to_student
from CanvasHacks.Models.student import get_first_name
from CanvasHacks import environment as env
from CanvasHacks.FileTools import getDateForMakingFileName
__author__ = 'adam'

if __name__ == '__main__':
    pass


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

    # data['responses'] = make_prompt_and_response(data['response_list'])

    return """
    Hi {name},
    
    {intro}
    =======================
    
    {responses}
    
    =======================
    {other}
    
     Please make sure you read the instructions in {review_assignment_name} before getting started.
     
     To complete your review, open the quiz named 
             {review_assignment_name} 
             {review_url}
    and use the access code: 
            {access_code}
    
    As always, canvas will lie to you about time limits by displaying an ominous, but meaningless in this course, 'Time Elapsed' timer. There is no time-limit other than you must submit your review before 11.59PM on {due_date}. 
    
    You may open and look at the peer review assignment as many times as you like.
    
    (Apologies for the terrible formatting of this message, Canvas is being annoying).
    
    Enjoy,
    /a
   
    """.format( **data )


def make_metareview_notice(data):

    return """
    Hi {name},
    
    The peer-review responses from the student who read your work are below. Please read them carefully and re-read your original assignment. Then follow the instructions at the bottom of this message to give the reviewer feedback on their review :
    =======================
    
    {responses}
    
    =======================
    {other}
    
    Personally, whenever I get critical feedback on something I've written, my first impression is always wrong ---I either think the problems mentioned are more trivial than they are or go in the opposite direction and overinflate every minor thing into something huge. Thus it may be a good idea to take a break before completing the metareview. 
    
    When you're ready to complete the metareview and give the reviewer feedback, please make sure you read the instructions in {review_assignment_name} before getting started.
     
     To complete your review of thier review, open the quiz named 
             {review_assignment_name} 
             {review_url}
    and use the access code: 
            {access_code}
    
    As always, canvas will lie to you about time limits by displaying an ominous, but meaningless in this course, 'Time Elapsed' timer. There is no time-limit other than you must submit your review before 11.59PM on {due_date}. 
    
    You may open and look at the metareview assignment as many times as you like.
    
    (Apologies for the terrible formatting of this message, Canvas is being annoying).
    
    Enjoy,
    /a
   
    """.format( **data )


def metareview_send_message_to_reviewers(review_assignments, studentRepo, contentRepo, activity, send=False):
    # # Load list of ReviewAssociation objects representing who reviews whom
    # review_assigns = associationRepo.get_associations(activity)
    # print("loaded {} student reviewer assignments".format(len(review_assigns)))
    log_file = "{}/{}-metareview-message-log.txt".format(env.LOG_FOLDER, getDateForMakingFileName())
    with open(log_file, 'a') as f:
        for rev in review_assignments:
            try:
                assessee = studentRepo.get_student(rev.assessee_id)

                content = contentRepo.get_formatted_work_by(rev.assessor_id)

                d = {
                    'intro': activity.email_intro,

                    'name': get_first_name(assessee),

                    # Formatted work for sending
                    'responses': content,

                    # Add any materials from me
                    'other': '',

                    # Add code and link to do reviewing assignment
                    'review_assignment_name': activity.name,
                    'access_code': activity.access_code,
                    'review_url': activity.html_url,
                    'due_date' : activity.string_due_date
                }

                message = make_notice(d)

                f.write("\n=========\n {}".format(message))

                if send:
                    subject = activity.email_subject
                    m = send_message_to_student(
                        student_id=rev.assessee_id,
                        subject=subject,
                        body=message )
                    print(m)
                else:
                    print(message)
            except Exception as e:
                # todo Replace with raise LookupError and hook handler
                f.write("\n=========\n {}".format(e))
                print(e)


def review_send_message_to_reviewers(review_assignments, studentRepo, contentRepo, activity, send=False):

    #THIS IS UNUSABLE. MUST FIX ERROR

    # # Load list of ReviewAssociation objects representing who reviews whom
    # review_assigns = associationRepo.get_associations(activity)
    # print("loaded {} student reviewer assignments".format(len(review_assigns)))

    for rev in review_assignments:
        try:
            assessor = studentRepo.get_student(rev.assessor_id)

            content = contentRepo.get_formatted_work(rev.assessee_id)

            d = {
                'intro': activity.email_intro,

                'name': get_first_name(assessor),

                # Formatted work for sending
                'responses': content,

                # Add any materials from me
                'other': '',

                # Add code and link to do reviewing assignment
                'review_assignment_name': activity.name,
                'access_code': activity.access_code,
                'review_url': activity.html_url,
                'due_date' : activity.string_due_date
            }

            message = make_notice(d)

            if send:
                subject = activity.email_subject
                # fix this you fucking idiot
                m = send_message_to_student( student_id=rev.assessor_id, subject=subject, body=message )
                print(m)
            else:
                print(message)
        except Exception as e:
            # todo Replace with raise LookupError and hook handler
            print(e)


class SkaaMessaging:

    def __init__(self, activity):
        self.activity = activity

    def make_message_content( self, receiving_student, content, other=None ):
        """Creates the message to be sent to the receiving student"""

        d = {
            'intro': self.activity.email_intro,

            'name': get_first_name(receiving_student),

            # Formatted work for sending
            'responses': content,

            # Add any materials from me
            'other': other,

            # Add code and link to do reviewing assignment
            'review_assignment_name': self.activity.name,
            'access_code': self.activity.access_code,
            'review_url': self.activity.html_url,
            'due_date' : self.activity.string_due_date
        }

        return make_notice(d)

    def make_send_data( self, receiving_student_id, message_body ):
        """Creates a dictionary with data to be passed to the
        method which actually sends the info"""
        return {'subject' : self.activity.email_subject,
                'to' : receiving_student_id,
                'message' : message_body
                }



class ReviewMessaging(SkaaMessaging):

    def __init__(self, activity, student_repository, content_repository):
        self.student_repository = student_repository
        self.content_repository = content_repository
        self.activity = activity

    def prepare_message( self, review_assignment, other=None ):
        try:
            assessor = self.studentRepo.get_student(review_assignment.assessor_id)
            receiving_student = assessor

            content = self.contentRepo.get_formatted_work(review_assignment.assessee_id)

            message = self.make_message_content(receiving_student, content, other=None)

            send_data = self.make_send_data(receiving_student.id)


        except Exception as e:
            # todo exception handling
            print(e)



