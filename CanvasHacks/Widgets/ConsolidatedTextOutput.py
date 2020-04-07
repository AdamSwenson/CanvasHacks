"""
This contains tools for displaying all student submitted
text along with toggle buttons for assigning credit or
no credit

For testing

# credit_list = [0, 2]

# make_consolidated_text_fields(test_results, credit_list)

Created by adam on 2/5/19
"""
__author__ = 'adam'
import json

from IPython.display import display
from ipywidgets import widgets


def make_assignment_header( store ):
    """Displays the header for each unit"""
    entry = """
    <h1>{}</h1>
    <h2>Class id: {}</h2>"""
    return display( widgets.HTML( entry.format( store.assignment_name, store.course_id ) ) )


def make_text_display( student_id, text, student_name='' ):
    """Handles the formatting of the student's text"""
    entry = """
          <div id='%s'>
            <h3>%s</h3>
            <p>
                %s
            </p>
        </div>"""
    student_name = "{}  |  ".format(student_name) if len(student_name) > 1 else student_name
    header = "{}{}".format(student_name, student_id)
    e = entry % (student_id, header, text)
    return widgets.HTML( e )


def make_submission_output( text, student_id, store,  studentRepository=None ):
    """Creates the display of the submitted text with a toggle button to
    update whether the student receives credit
    """
    bval = 'Credit' if student_id in store.credit else 'No credit'
    credit_button = widgets.ToggleButtons(
        options=[ 'Credit', 'No credit' ],
        value=bval,
        description='',
        disabled=False
    )
    student_name = ''

    if studentRepository:
        student_name = studentRepository.get_student_name(student_id)

    ta = make_text_display( student_id, text, student_name )

    def on_value_change( change ):
        """The relevant callback
        NB the use of scope to define student_id"""
        v = change[ 'new' ]
        print( v, student_id )
        try:
            if v == 'Credit':
                store.assign_student_credit( student_id )
            elif v == 'No credit':
                store.assign_student_no_credit( student_id )
        except ValueError:
            pass

    credit_button.observe( on_value_change, names='value' )
    display( widgets.VBox( [ ta, credit_button ] ) )


def make_consolidated_text_fields( store, studentRepository=None ):
    """Displays each entry with a toggle to adjust whether the
    student receives credit"""
    for r in store.submissions:
        make_submission_output( r[ 'body' ], r[ 'student_id' ], store, studentRepository )


def make_consolidated_text_file( journal_folder, filename='compiled-text.txt', studentRepository=None ):
    """Reads the data from the relevant json file and then
    writes each entry in to a single text file for ease of reading
    todo: This should be refactored out of the widgets file
    """
    entry = """
    {student_id} \n
    {body} \n
    \n
    """
    to_write = "%s/%s" % (journal_folder, filename)
    with open( "%s/all-submissions.json" % journal_folder, 'r' ) as f:
        j = json.load( f )
        with open( to_write, 'w+' ) as cf:
            for rec in j:
                txt = entry.format( **rec )
                if studentRepository:
                    name = studentRepository.get_student_name(rec['student_id'])
                    txt = "{} \n {}".format(name, txt)
                #     print(entry.format(**rec))
                cf.write(  txt )

    print( "Consolidated file written to {}".format( to_write ) )


def make_test_data( number_students ):
    return [ { 'student_id': i, 'body': 'Body text for student {}'.format( i ) } for i in range( 0, number_students ) ]


if __name__ == '__main__':
    pass
