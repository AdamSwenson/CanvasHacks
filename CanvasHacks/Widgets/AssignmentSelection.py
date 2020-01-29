"""
Created by adam on 2/14/19
"""
__author__ = 'adam'
from IPython.display import display
from ipywidgets import widgets

from CanvasHacks import environment
from CanvasHacks.RequestTools import get_assignments_needing_grading, \
    get_assignments_with_submissions


def make_assignment_button( assignment_id, name, ):
    """Creates a single selection button
    style is success if the assignment has been selected
    style is primary if not selected
    """
    return make_selection_button( assignment_id, name,
                                  environment.CONFIG.get_assignment_ids,
                                  environment.CONFIG.add_assignment,
                                  environment.CONFIG.remove_assignment )
    #
    #
    # def get_style( assignment_id ):
    #     return 'success' if assignment_id in environment.CONFIG.get_assignment_ids() else 'primary'
    #
    #     # Create the button
    #
    # layout = widgets.Layout( width='50%' )
    # b = widgets.Button( description=name, layout=layout, button_style=get_style( assignment_id ) )
    #
    # def callback( change ):
    #     if assignment_id in environment.CONFIG.get_assignment_ids():
    #         environment.CONFIG.remove_assignment( assignment_id )
    #     else:
    #         environment.CONFIG.add_assignment( assignment_id, name )
    #     b.button_style = get_style( assignment_id )
    #
    # b.on_click( callback )
    # display( b )
    # return b


def make_selection_button( item_id, name, get_func, add_func, remove_func ):
    """Creates a single selection button
    style is success if the assignment has been selected
    style is primary if not selected
    """

    def get_style( item_id ):
        return 'success' if item_id in get_func() else 'primary'

        # Create the button

    layout = widgets.Layout( width='50%' )
    b = widgets.Button( description=name, layout=layout, button_style=get_style( item_id ) )

    def callback( change ):
        if item_id in get_func():
            remove_func( item_id )
        else:
            add_func( item_id, name )
        b.button_style = get_style( item_id )

    b.on_click( callback )
    display( b )
    return b


def make_discussion_selection_button( topic_id, name ):
    return make_selection_button( topic_id, name,
                                  environment.CONFIG.get_discussion_ids,
                                  environment.CONFIG.add_discussion,
                                  environment.CONFIG.remove_discussion )


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
        to_grade += [ (g[ 'name' ].strip(), g[ 'id' ]) for g in assigns ]

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
