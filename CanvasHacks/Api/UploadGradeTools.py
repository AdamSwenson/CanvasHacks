"""
Tools for uploading scores to canvas for journals

Created by adam on 1/29/19
"""
__author__ = 'adam'

import requests
from IPython.display import display
from ipywidgets import widgets

from CanvasHacks.Repositories.DataManagement import DataStore, DataStoreNew
from CanvasHacks.Api.RequestTools import make_request_header
from CanvasHacks.Api.UrlTools import make_url


def upload_students_receiving_credit( store: DataStore ):
    """Makes the requests to the server to assign each of the students credit
    for the unit
    Hits https://canvas.instructure.com/doc/api/submissions.html#method.submissions_api.update
    """
    if isinstance(store, DataStoreNew):
        print("uploading from new data store")
        for sub, score in store.results:
            sid = sub.user_id
            upload_credit(store.course_id, store.assignment_id, sid, score)
    else:
        for sid in store.credit:
            upload_credit(store.course_id, store.assignment_id, sid, 100)


def upload_credit( course_id, assignment_id, student_id, pct_credit ):
    """
    Handles actual upload to server.

    Hits https://canvas.instructure.com/doc/api/submissions.html#method.submissions_api.update
    :param pct_credit: 100 for full
    :param course_id:
    :param assignment_id:
    :param student_id:
    :return:
    """
    if pct_credit is not None:
        pct = "{}%".format(pct_credit) if isinstance(pct_credit, int) or pct_credit[-1:] != '%' else pct_credit

        data = { 'submission': { 'posted_grade': pct } }

        url_temp = "{url_base}/{assignment_id}/submissions/{student_id}"

        url = url_temp.format( url_base=make_url( course_id, 'assignments' ),
                               assignment_id=assignment_id,
                               student_id=student_id )

        print( 'Uploading {} credit'.format(pct), url )
        requests.put( url, headers=make_request_header(), json=data )


def assign_no_credit( course_id, assignment_id, students ):
    """Makes the requests to the server to assign each of the students no credit
    for the unit
    """
    data = { 'submission': { 'posted_grade': 'fail' } }

    url = make_url( course_id, 'assignments' )
    url = "%s/%s/submissions" % (url, assignment_id)

    for s in students:
        surl = "%s/%s" % (url, s)
        print( 'no credit', surl )


#         requests.put(surl, headers=make_request_header(), json=data)


def make_upload_button( store ):
    """Displays a button for each unit. When the button
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
