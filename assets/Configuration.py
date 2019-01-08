
class Configuration( object ):
    course_ids = [ ]
    canvas_token = False

    @classmethod
    def add_course_id( cls, course_id ):
        cls.course_ids.append( course_id )

    @classmethod
    def add_canvas_token( cls, token ):
        cls.canvas_token = token

    @classmethod
    def reset_course_ids( cls ):
        cls.course_ids = [ ]
        print("List of course ids is empty")

    @classmethod
    def reset_canvas_token( cls ):
        cls.canvas_token = False
        print("Canvas token reset to empty")

    @classmethod
    def reset_config( cls ):
        cls.reset_canvas_token()
        cls.reset_course_ids()


class InteractiveConfiguration( Configuration ):
    def __init__( self ):
        super().__init__()

    @classmethod
    def handle_token_entry( cls, event ):
        if event[ 'type' ] == 'change' and event[ 'name' ] == 'value':
            v = event[ 'new' ]
            cls.add_canvas_token( v )



