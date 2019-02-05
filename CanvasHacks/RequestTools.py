"""
Created by adam on 9/20/18
"""
__author__ = 'adam'

import requests

from CanvasHacks import environment
from CanvasHacks.UrlTools import make_url


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
# Get assignment list
def get_all_course_assignments( course_id ):
    """Returns a list of all the assignments for the course
    Uses api: GET /api/v1/courses/:course_id/assignments
    """
    url = make_url( course_id, 'assignments' )
    url = "%s?per_page=50" % url
    return send_get_request( url, { 'include': 'submissions' } )


def get_assignment( course_id, assignment_id ):
    """Retrieves the specified assignment and returns it as a dictionary"""
    url = make_url( course_id, 'assignments' )
    url = "%s/%s" % (url, assignment_id)
    #     print(url)
    return send_get_request( url )


def get_assignments_needing_grading( course_id ):
    """Returns a list of tuples (name, id) of assignments which
    have at least one ungraded submission"""
    assigns = get_all_course_assignments( course_id )
    to_grade = [ a for a in assigns if a[ 'needs_grading_count' ] > 0 ]

    to_grade = [ (g[ 'name' ].strip(), g[ 'id' ]) for g in to_grade ]
    return to_grade


if __name__ == '__main__':
    pass
