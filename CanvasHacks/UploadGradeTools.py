"""
Tools for uploading scores to canvas for journals

Created by adam on 1/29/19
"""
__author__ = 'adam'

import requests

from CanvasHacks.UrlTools import make_url
from CanvasHacks.RequestTools import make_request_header
from CanvasHacks.DataManagement import DataStore


def upload_students_receiving_credit( store: DataStore ):
    """Makes the requests to the server to assign each of the students credit
    for the assignment
    """
    data = {'submission' : {'posted_grade' : 'pass'}}

    url = make_url(store.course_id, 'assignments')
    url = "%s/%s/submissions" % (url, store.assignment_id)

    for s in store.credit:
        surl = "%s/%s" % (url, s)
        print('credit', surl)
        requests.put(surl, headers=make_request_header(), json=data)


def assign_no_credit(course_id, assignment_id, students):
    """Makes the requests to the server to assign each of the students no credit
    for the assignment
    """
    data = {'submission' : {'posted_grade' : 'fail'}}

    url = make_url(course_id, 'assignments')
    url = "%s/%s/submissions" % (url, assignment_id)

    for s in students:
        surl = "%s/%s" % (url, s)
        print('no credit', surl)
#         requests.put(surl, headers=make_request_header(), json=data)

if __name__ == '__main__':
    pass