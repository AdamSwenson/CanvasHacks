"""
Created by adam on 12/26/19
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass


def make_conversation_data(me_id, student_id, subject, body):
    """Creates the request data to be sent to canvas"""
    return {
        # must include self
        'recipients' : [me_id, student_id],
        'body': body,
        'subect' : subject,
        'force_new' : True
    }


def make_prompt_and_response(response_list):
    temp = """
    <h3>{prompt}</h3>

    <p>{response}</p>
    """
    rs = [ temp.format(**r) for r in response_list]
    return " ".join(rs)


def make_notice(data):
    """Should define
    name, response_list, review_assignment_name, access_code
    """

    data['responses'] = make_prompt_and_response(data['response_list'])

    return """
    Hi {name},
    
    Here is another student's assignment for you to review:
    
    {responses}
    
    <p>To complete your review, open the quiz named {review_assignment_name} </br>
    
    and use the access code <strong>{access_code}</strong>
    </p>
    
    """.format(**data)

