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
    
    Here is another student's assignment for you to review:
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
