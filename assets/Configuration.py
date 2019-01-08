from ipywidgets import widgets
from IPython.display import display


class Configuration( object ):
    course_ids = [ ]
    canvas_token = False

    @classmethod
    def add_course_id( cls, course_id ):
        cls.course_ids.append( course_id )

    @classmethod
    def add_canvas_token( cls, token ):
        cls.canvas_token = token


class InteractiveConfiguration( Configuration ):
    def __init__( self ):
        super().__init__()

    @classmethod
    def handle_token_entry( cls, event ):
        if event[ 'type' ] == 'change' and event[ 'name' ] == 'value':
            v = event[ 'new' ]
            cls.add_canvas_token( v )

    @classmethod
    def reset_course_ids( cls ):
        cls.course_ids = [ ]


def make_text_input( indic ):
    text = widgets.Text( description=indic[ 'label' ] )
    display( text )
    text.observe( indic[ 'handler' ] )


def handle_sub( v ):
    print( v )
