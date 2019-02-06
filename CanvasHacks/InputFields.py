"""
Created by adam on 1/7/19
"""
__author__ = 'adam'

from IPython.display import display
from ipywidgets import widgets

from CanvasHacks.Configuration import InteractiveConfiguration


# -------- General
def make_text_input( input_dict ):
    """Creates a text input field. The given dictionary should have keys 'label' and 'handler'"""
    text = widgets.Text( description=input_dict[ 'label' ] )
    display( text )
    text.observe( input_dict[ 'handler' ] )
    return text


# -------- Canvas specific
def make_canvas_token_input():
    """Creates the input field for the canvas api token"""
    canvas_token_input = { 'label': 'Canvas token', 'handler': InteractiveConfiguration.handle_token_entry }
    return make_text_input( canvas_token_input )


def make_canvas_url_input():
    """Creates the input field for the canvas api token"""
    canvas_url_input = { 'label': 'Canvas url', 'handler': InteractiveConfiguration.handle_url_entry }
    make_text_input( canvas_url_input )


def make_course_ids_input():
    """
    Make box and buttons for course id entry.
    On submit button click, class ids updates with the value in the text box
    """
    t = widgets.Text( description='Class id' )
    submit = widgets.Button( description='Add id', button_style='success' )
    reset = widgets.Button( description='Reset ids' )
    out = widgets.Output( layout={ 'border': '1px solid black' } )

    def handle_add( change ):
        InteractiveConfiguration.add_course_id( t.value )
        # Clear the box
        t.value = ''
        show_class_ids()

    def handle_reset( change ):
        InteractiveConfiguration.reset_course_ids()
        show_class_ids()

    def show_class_ids():
        out.clear_output()
        with out:
            print( '    ----Canvas class ids----    ' )
            for cid in InteractiveConfiguration.course_ids:
                print( cid )

    submit.on_click( handle_add )
    reset.on_click( handle_reset )
    button_box = widgets.HBox( [ reset, submit ] )
    input_box = widgets.VBox( [ t, button_box ] )
    display( widgets.HBox( [ input_box, out ] ) )


def make_general_reset_button():
    rb = widgets.Button( description='Clear canvas token and class ids' )

    def reset_all( change ):
        InteractiveConfiguration.reset_config()

    display( rb.on_click( reset_all ) )


if __name__ == '__main__':
    pass
