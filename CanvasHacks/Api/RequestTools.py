"""
Created by adam on 9/20/18
"""
__author__ = 'adam'

import requests
from requests.exceptions import HTTPError

from CanvasHacks import environment
from CanvasHacks.Api.UrlTools import make_url


def make_request_header():
    """Creates the request header with Authorization value expected by canvas"""
    return { 'Authorization': 'Bearer {}'.format( environment.CONFIG.canvas_token ) }


def send_get_request( url, data={ } ):
    """Makes a get request to the given url, using the data.
    Returns a dictionary from the json
    """
    head = { 'Authorization': 'Bearer {}'.format( environment.CONFIG.canvas_token ) }
    response = requests.get( url, headers=make_request_header(), json=data )
    return response.json()


def send_multi_page_get_request(url, data={}, per_page=45):
    responses = []

    url = "{}/?per_page={}".format(url, per_page)

    try:
        while True:
            print( url )
            response = requests.get( url, headers=make_request_header(), json=data )
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
            # Continuing on since was successful
            responses += response.json()
            url = response.links[ 'next' ][ 'url' ]

    except KeyError:
        return responses

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
        return responses

    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
        return responses



def send_post_request( url, data ):
    """Makes a post request to the given url, using the data.
    Returns a dictionary from the json
    """
    head = { 'Authorization': 'Bearer {}'.format( environment.CONFIG.canvas_token ) }
    response = requests.post( url, headers=head, json=data )
    return response.json()


def send_put_request( url, data ):
    """Makes a put request to the given url, using the data.
    Returns a dictionary from the json
    """
    response = requests.put( url, headers=make_request_header(), json=data )
    return response.json()


# Assignments
# Get unit list
def get_all_course_assignments( course_id ):
    """Returns a list of all the assignments for the course
    Uses api: GET /api/v1/courses/:course_id/assignments
    """
    url = make_url( course_id, 'assignments' )
    url = "%s?per_page=50" % url
    return send_get_request( url, { 'include': 'submissions' } )


def get_assignment( course_id, assignment_id ):
    """Retrieves the specified unit and returns it as a dictionary"""
    url = make_url( course_id, 'assignments' )
    url = "%s/%s" % (url, assignment_id)
    #     print(url)
    return send_get_request( url )


def get_assignments_needing_grading( course_id ):
    """Returns a list of tuples (name, id) of assignments which
    have at least one ungraded submission"""
    assigns = get_all_course_assignments( course_id )
    assigns = [ a for a in assigns if a[ 'needs_grading_count' ] > 0 ]

    # to_grade = [ (g[ 'name' ].strip(), g[ 'id' ]) for g in to_grade ]
    return assigns



def get_assignments_with_submissions( course_id, needs_grading=True ):
    """Queries the server and returns only the assignments
    in the course which at least one
    student has submitted."""
    assignments = get_all_course_assignments( course_id )
    if needs_grading:
        assignments = [ a for a in assignments if a[ 'needs_grading_count' ] > 0 ]
    assignments = [ a for a in assignments if a[ "has_submitted_submissions" ] is True ]
    return assignments



def get_all_course_quizzes(course_id):
    """ GET /api/v1/courses/:course_id/quizzes """
    url = make_url(course_id, 'quizzes')
    #     print(url)
    return send_get_request(url)


def get_all_quiz_submissions(course_id, quiz_id, per_page=42):
    """
    GET /api/v1/courses/:course_id/quizzes/:quiz_id/submissions
    """
    url = make_url(course_id, 'quizzes')
    url += "/%s/submissions?per_page=%s" % (quiz_id, per_page)

    print(url)
    #     return send_get_request(url)
    responses = [ ]
    #     url = make_url( course_id, assign_type )
    #     url = "%s/%s/submissions?per_page=%s" % (url, quiz_id, per_page)
    try:
        while True:
            print( url )
            response = requests.get( url, headers=make_request_header() )
            responses += response.json()['quiz_submissions']
            url = response.links[ 'next' ][ 'url' ]
    except KeyError:
        return responses


if __name__ == '__main__':
    pass
