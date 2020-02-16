"""
Created by adam on 2/14/19
"""
__author__ = 'adam'
from IPython.display import display
from ipywidgets import widgets

from CanvasHacks import environment
from CanvasHacks.RequestTools import get_assignments_needing_grading, \
    get_assignments_with_submissions


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


# ------------------------- Discussions
def make_discussion_selection_button( topic_id, name ):
    return make_selection_button( topic_id, name,
                                  environment.CONFIG.get_discussion_ids,
                                  environment.CONFIG.add_discussion,
                                  environment.CONFIG.remove_discussion )


def make_discussion_chooser( course ):
    """Display inputs for selecting assignments
    The selected assignments will be stored in the
    environment.CONFIG
    """
    discussions = [ d for d in course.get_discussion_topics() ]
    buttons = [ ]
    discussions = [ (a.id, a.title) for a in discussions ]
    #     if course_id:
    #         display( widgets.HTML( value="<h4>Course {}</h4>".format( course_id ) ) )
    for discussion_id, discussion_name in discussions:
        buttons.append( make_discussion_selection_button( discussion_id, discussion_name ) )


# ---------------------------- Assignments

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


def make_assignment_button( assignment_id, name, ):
    """Creates a single selection button
    style is success if the assignment has been selected
    style is primary if not selected
    """
    return make_selection_button( assignment_id, name,
                                  environment.CONFIG.get_assignment_ids,
                                  environment.CONFIG.add_assignment,
                                  environment.CONFIG.remove_assignment )


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


# ------------------------------ Unit

def make_unit_button( unit_number ):
    """Creates a single selection button
    style is success if the unit has been selected
    style is primary if not selected
    """
    name = "Unit {}".format( unit_number )

    def set_callback(unit_number, name=None):
        """ This is used so that can also initialize all the
        canvas objects on the configuration
        """
        environment.CONFIG.set_unit_number(unit_number, name)
        environment.CONFIG.initialize_canvas_objs()

    return make_selection_button( unit_number,
                                  name,
                                  environment.CONFIG.get_unit_number,
                                  set_callback,
                                  # environment.CONFIG.set_unit_number,
                                  environment.CONFIG.reset_unit_number
                                  )


def make_unit_chooser( num_units=6 ):
    """Display inputs for selecting assignments
    The selected assignments will be stored in the
    environment.CONFIG
    """
    buttons = [ ]
    #     if course_id:
    #         display( widgets.HTML( value="<h4>Course {}</h4>".format( course_id ) ) )
    num_units += 1
    for i in range( 1, num_units ):
        buttons.append( make_unit_button( i ) )


if __name__ == '__main__':
    pass
