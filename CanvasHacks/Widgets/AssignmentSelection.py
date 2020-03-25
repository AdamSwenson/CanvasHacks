"""
Created by adam on 2/14/19
"""
from CanvasHacks.Definitions.unit import Unit

__author__ = 'adam'
from IPython.display import display
from ipywidgets import widgets, VBox

from CanvasHacks import environment
from CanvasHacks.Api.RequestTools import get_assignments_needing_grading, \
    get_assignments_with_submissions


def make_selection_button( item_id, name, get_func, add_func, remove_func, width='50%', **kwargs ):
    """Creates a single selection button
    style is success if the unit has been selected
    style is primary if not selected
    """

    def get_style( item_id ):
        return 'success' if item_id in get_func() else 'primary'

        # Create the button

    layout = widgets.Layout( width=width )
    b = widgets.Button( description=name, layout=layout, button_style=get_style( item_id ) )

    def callback( change ):
        if item_id in get_func():
            remove_func( item_id )
        else:
            add_func( item_id, name )
        b.button_style = get_style( item_id )

    b.on_click( callback )


    return b


# ------------------------- Discussions
def make_discussion_selection_button( topic_id, name, **kwargs ):
    return make_selection_button( topic_id, name,
                                  environment.CONFIG.get_discussion_ids,
                                  environment.CONFIG.add_discussion,
                                  environment.CONFIG.remove_discussion, **kwargs )


def make_discussion_chooser( course, return_button=False, **kwargs ):
    """Display inputs for selecting assignments
    The selected assignments will be stored in the
    environment.CONFIG
    """
    discussions = [ d for d in course.get_discussion_topics() ]
    # If a particular unit has been selected, just get the component discussions
    # Othewise, just use all course discussions
    if environment.CONFIG.unit_number is not None:
        discussions = environment.CONFIG.unit.find_for_unit(environment.CONFIG.unit_number, discussions)
    buttons = [ ]
    discussions = [ (a.id, a.title) for a in discussions ]
    #     if course_id:
    #         display( widgets.HTML( value="<h4>Course {}</h4>".format( course_id ) ) )
    for discussion_id, discussion_name in discussions:
        buttons.append( make_discussion_selection_button( discussion_id, discussion_name, **kwargs ) )

    if return_button is True:
        # If putting inside a box or something else which will
        # call display
        return buttons
    else:

        display( VBox(buttons) )



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


def make_assignment_button( assignment_id, name, **kwargs ):
    """Creates a single selection button
    style is success if the unit has been selected
    style is primary if not selected
    """
    return make_selection_button( assignment_id, name,
                                  environment.CONFIG.get_assignment_ids,
                                  environment.CONFIG.add_assignment,
                                  environment.CONFIG.remove_assignment,
                                  **kwargs )


def make_assignment_chooser(activity=None,  return_button=False, **kwargs):
    """Display inputs for selecting assignments
    The selected assignments will be stored in the
    environment.CONFIG
    """
    assignments = [ ]
    buttons = [ ]
    # Get list of all assignments for the courses
    for course_id in environment.CONFIG.course_ids:
        assignments += get_assignments_with_submissions( course_id )
    assignments = [ (a[ 'id' ], a[ 'name' ]) for a in assignments ]

    if activity is not None:
        # If we we're passed an activity_inviting_to_complete, filter the assignments
        assignments = [a for a in assignments if activity.is_activity_type(a[1])]

    print( "{} assignments with submissions".format( len( assignments ) ) )
    if course_id:
        display( widgets.HTML( value="<h4>Course {}</h4>".format( course_id ) ) )

    # Make buttons for selecting
    for assignment_id, assignment_name in assignments:
        buttons.append( make_assignment_button( assignment_id, assignment_name , **kwargs) )
    # return buttons

    if return_button is True:
        # If putting inside a box or something else which will
        # call display
        return buttons
    else:

        display( VBox(buttons) )


# ------------------------------ Unit

def make_unit_button( unit_number , **kwargs):
    """Creates a single selection button
    style is success if the unit has been selected
    style is primary if not selected
    """
    name = "Unit {}".format( unit_number )

    def set_callback(unit_number, name=None):
        """ This is used so that can also _initialize all the
        canvas objects on the configuration
        """
        environment.CONFIG.set_unit_number(unit_number, name)
        environment.CONFIG.initialize_canvas_objs()
        environment.CONFIG.unit = Unit(environment.CONFIG.course, unit_number)


    return make_selection_button( unit_number,
                                  name,
                                  environment.CONFIG.get_unit_number,
                                  set_callback,
                                  # environment.CONFIG.set_unit_number,
                                  environment.CONFIG.reset_unit_number,
                                  **kwargs
                                  )


def make_unit_chooser( num_units=6, return_button=False, **kwargs ):
    """Display inputs for selecting assignments
    The selected assignments will be stored in the
    environment.CONFIG
    """
    buttons = [ ]
    #     if course_id:
    #         display( widgets.HTML( value="<h4>Course {}</h4>".format( course_id ) ) )
    num_units += 1
    for i in range( 1, num_units ):
        buttons.append( make_unit_button( i, **kwargs ) )

    if return_button is True:
        # If putting inside a box or something else which will
        # call display
        return buttons
    else:

        display( VBox(buttons) )



if __name__ == '__main__':
    pass
