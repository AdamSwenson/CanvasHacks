"""
Tools for uploading scores to canvas for journals

Created by adam on 1/29/19
"""
__author__ = 'adam'

import requests
from IPython.display import display
from ipywidgets import widgets

from CanvasHacks.DataManagement import DataStore
from CanvasHacks.RequestTools import make_request_header
from CanvasHacks.UrlTools import make_url


def upload_students_receiving_credit( store: DataStore ):
    """Makes the requests to the server to assign each of the students credit
    for the assignment
    """
    data = { 'submission': { 'posted_grade': 'pass' } }

    url = make_url( store.course_id, 'assignments' )
    url = "%s/%s/submissions" % (url, store.assignment_id)

    for s in store.credit:
        surl = "%s/%s" % (url, s)
        print( 'credit', surl )
        requests.put( surl, headers=make_request_header(), json=data )


def assign_no_credit( course_id, assignment_id, students ):
    """Makes the requests to the server to assign each of the students no credit
    for the assignment
    """
    data = { 'submission': { 'posted_grade': 'fail' } }

    url = make_url( course_id, 'assignments' )
    url = "%s/%s/submissions" % (url, assignment_id)

    for s in students:
        surl = "%s/%s" % (url, s)
        print( 'no credit', surl )


#         requests.put(surl, headers=make_request_header(), json=data)


def make_upload_button( store ):
    """Displays a button for each assignment. When the button
    is clicked it uploads grades for all students in the complete list
    The button's styling changes while uploading and again when complete
    """

    def upload_callback( event ):
        # change button style to indicate working
        b.button_style = 'warning'
        # upload grades for students receiving credit
        upload_students_receiving_credit( store )
        # change button style
        b.button_style = 'success'

    desc = 'Upload grades for {}'.format( store.assignment_name )
    layout = widgets.Layout( width='50%' )
    b = widgets.Button( description=desc, button_style='danger', layout=layout )
    b.on_click( upload_callback )

    display( b )


if __name__ == '__main__':
    pass
