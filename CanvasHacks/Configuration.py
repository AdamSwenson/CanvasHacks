"""
Created by adam on 1/31/19
"""
__author__ = 'adam'
import configparser
import os

CREDENTIALS_FOLDER_PATH = "{}/private"
LIVE_CREDENTIALS = "{}/canvas-credentials.ini"
TEST_CREDENTIALS = "{}/test-credentials.ini"


class Configuration( object ):
    archive_folder = False
    assignments = [ ]
    course_ids = [ ]
    canvas_token = False
    canvas_url_base = False
    log_folder = False

    @classmethod
    def add_assignment( cls, assignment_id, assignment_name=None ):
        cls.assignments.append( (assignment_id, assignment_name) )
        cls.assignments = list( set( cls.assignments ) )

    @classmethod
    def add_course_id( cls, course_id ):
        cls.course_ids.append( course_id )

    @classmethod
    def add_canvas_token( cls, token ):
        cls.canvas_token = token

    @classmethod
    def add_canvas_url_base( cls, url ):
        cls.canvas_url_base = url

    @classmethod
    def get_assignment_ids( cls ):
        return [ i[ 0 ] for i in cls.assignments ]

    @classmethod
    def remove_assignment( cls, assignment_id ):
        el = list( filter( lambda x: x[ 0 ] == assignment_id, cls.assignments ) )[ 0 ]
        idx = cls.assignments.index( el )
        return cls.assignments.pop( idx )

    @classmethod
    def reset_assignments( cls ):
        cls.assignments = [ ]
        print( "List of assignments is empty" )

    @classmethod
    def reset_course_ids( cls ):
        cls.course_ids = [ ]
        print( "List of course ids is empty" )

    @classmethod
    def reset_canvas_token( cls ):
        cls.canvas_token = False
        print( "Canvas token reset to empty" )

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

    @classmethod
    def handle_url_entry( cls, event ):
        if event[ 'type' ] == 'change' and event[ 'name' ] == 'value':
            v = event[ 'new' ]
            cls.add_canvas_url_base( v )


class FileBasedConfiguration( Configuration ):
    configuration = False
    file_path = False

    def __init__( self, configuration_file_path ):
        super().__init__()
        FileBasedConfiguration.file_path = configuration_file_path

    @classmethod
    def read_config_file( cls ):
        if not cls.file_path:
            # The file path could've been customized by instantiating the class
            # If that didn't happen, we go with the default
            # The folder containing the assets folder
            cls.proj_base = os.path.abspath( os.path.dirname( os.path.dirname( __file__ ) ) )
            # All login credentials are defined in files here.
            # THIS CONTENTS OF THIS FOLDER MUST NOT BE COMMITTED TO VERSION CONTROL!
            folder_path = CREDENTIALS_FOLDER_PATH.format(cls.proj_base)
            creds = TEST_CREDENTIALS if cls.is_test else LIVE_CREDENTIALS
            cls.file_path = creds.format(folder_path )

        cls.configuration = configparser.ConfigParser()
        cls.configuration.read( cls.file_path )
        print( "Reading credentials and settings from %s" % cls.file_path )

    @classmethod
    def load( cls, is_test=False ):
        cls.is_test = is_test
        cls.read_config_file()
        cls.load_token()
        cls.load_url_base()
        cls.load_local_filepaths()
        cls.load_section_ids()

    @classmethod
    def load_section_ids( cls ):
        try:
            for v in cls.configuration[ 'sections' ].values():
                cls.add_course_id( v )
        except:
            pass

    @classmethod
    def load_local_filepaths( cls ):
        root = os.getenv( "HOME" )
        cls.archive_folder = "%s/%s" % (root, cls.configuration[ 'folders' ].get( 'STUDENT_WORK_ARCHIVE_FOLDER' ))
        cls.log_folder = "%s/%s" % (root, cls.configuration[ 'folders' ].get( 'LOG_FOLDER' ))
        cls.data_folder = '%s/data' % cls.proj_base

    @classmethod
    def load_token( cls ):
        if not cls.configuration:
            cls.read_config_file()

        cls.add_canvas_token( cls.configuration[ 'credentials' ].get( 'TOKEN' ) )

    @classmethod
    def load_url_base( cls ):
        cls.add_canvas_url_base( cls.configuration[ 'url' ].get( 'BASE' ) )


if __name__ == '__main__':
    FileBasedConfiguration.load()
    print( FileBasedConfiguration.canvas_token )
