"""
Created by adam on 2/14/19
"""
__author__ = 'adam'
from IPython.display import display
from ipywidgets import widgets

from CanvasHacks import environment
from CanvasHacks.RequestTools import get_all_course_assignments, get_assignments_needing_grading


def make_assignment_button( assignment_id, name, ):
    """Creates a single selection button
    style is success if the assignment has been selected
    style is primary if not selected
    """

    def get_style( assignment_id ):
        return 'success' if assignment_id in environment.CONFIG.get_assignment_ids() else 'primary'

        # Create the button

    layout = widgets.Layout( width='50%' )
    b = widgets.Button( description=name, layout=layout, button_style=get_style( assignment_id ) )

    def callback( change ):
        if assignment_id in environment.CONFIG.get_assignment_ids():
            environment.CONFIG.remove_assignment( assignment_id )
        else:
            environment.CONFIG.add_assignment( assignment_id, name )
        b.button_style = get_style( assignment_id )

    b.on_click( callback )
    display( b )
    return b


def get_assignments_with_submissions( course_id ):
    """Queries the server and returns only the assignments
    in the course which at least one
    student has submitted."""
    assignments = get_all_course_assignments( course_id )
    return [ a for a in assignments if a[ "has_submitted_submissions" ] is True ]


def view_selected_assignments():
    out = widgets.Output( layout={ 'border': '1px solid black' } )
    with out:
        for aid, name in environment.CONFIG.assignments:
            print( name )
    display( out )


def view_ungraded_assignments():
    print( "These assignments need grading: " )
    out = widgets.Output( layout={ 'border': '1px solid black' } )
    to_grade = [ ]
    for sec in environment.CONFIG.course_ids:
        assigns = get_assignments_needing_grading( sec )
        # assigns = assigns[ sec ]
        with out:
            to_grade += [ print( g[ 0 ] ) for g in assigns ]
    display( out )


def make_assignment_chooser():
    """Display inputs for selecting assignments
    The selected assignments will be stored in the
    environment.CONFIG
    """
    assignments = [ ]
    buttons = [ ]
    # Get list of all assignments for the courses
    for course_id in environment.CONFIG.course_ids:
        assignments += get_assignments_with_submissions( course_id )
    print( "{} assignments with submissions".format( len( assignments ) ) )
    # Make buttons for selecting
    assignments = [ (a[ 'id' ], a[ 'name' ]) for a in assignments ]
    if course_id:
        display( widgets.HTML( value="<h4>Course {}</h4>".format( course_id ) ) )
    for assignment_id, assignment_name in assignments:
        buttons.append( make_assignment_button( assignment_id, assignment_name ) )
    # return buttons


if __name__ == '__main__':
    pass
