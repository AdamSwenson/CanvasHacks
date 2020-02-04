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
    <h3>{prompt}</h3>

    <p>{response}</p>
    """
    rs = [ temp.format( **r ) for r in response_list ]
    return " ".join( rs )


def make_notice( data ):
    """Should define
    name, responses, review_assignment_name, access_code
    """

    # data['responses'] = make_prompt_and_response(data['response_list'])

    return """
    <p>Hi {name},</p>
    
    <p>Here is another student's assignment for you to review:</p>
    
    {responses}
    
    {other}
    
    <p>To complete your review, open the quiz named {review_assignment_name} </br>
    
    and use the access code <strong>{access_code}</strong>
    </p>
    
    """.format( **data )
