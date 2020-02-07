"""
Created by adam on 12/26/19
"""
from CanvasHacks.RequestTools import send_post_request

__author__ = 'adam'

if __name__ == '__main__':
    pass


def notify_student( student_id, subject, body ):
    """Sends a new message to the student.
    Returns the result object which will contain the conversation id
    if needed for future use
    """
    d = make_conversation_data( student_id, subject, body )

    return send_post_request( 'https://canvas.csun.edu/api/v1/conversations', d )


def make_conversation_data( student_id, subject, body ):
    """Creates the request data to be sent to canvas"""
    return {
        'recipients': [ student_id ],
        'body': body,
        'subject': subject,
        'force_new': True
    }


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
