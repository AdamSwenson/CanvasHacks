"""
Created by adam on 1/31/19
"""
__author__ = 'adam'
import configparser
import os, sys


class Configuration( object ):
    course_ids = [ ]
    canvas_token = False
    canvas_url_base = False

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


class FileBasedConfiguration(Configuration):
    configuration = False
    file_path = False

    def __init__(self, configuration_file_path):
        super().__init__()
        FileBasedConfiguration.file_path = configuration_file_path

    @classmethod
    def read_config_file( cls):
        if not cls.file_path:
            # The file path could've been customized by instantiating the class
            # If that didn't happen, we go with the default
            # The folder containing the assets folder
            PROJ_BASE = os.path.abspath( os.path.dirname( os.path.dirname( __file__ )) )
            # All login credentials are defined in files here.
            # THIS CONTENTS OF THIS FOLDER MUST NOT BE COMMITTED TO VERSION CONTROL!
            CREDENTIALS_FOLDER_PATH = "%s/private" % PROJ_BASE
            cls.file_path = "%s/canvas-credentials.ini" % CREDENTIALS_FOLDER_PATH

        cls.configuration = configparser.ConfigParser()
        cls.configuration.read( cls.file_path )
        print( "Reading credentials and settings from %s" % cls.file_path  )

    @classmethod
    def load( cls ):
        cls.read_config_file()
        cls.load_token()
        cls.load_url_base()

    @classmethod
    def load_token( cls ):
        if not cls.configuration:
            cls.read_config_file()

        cls.add_canvas_token(cls.configuration[ 'credentials' ].get( 'TOKEN' ))

    @classmethod
    def load_url_base( cls ):
        cls.add_canvas_url_base(cls.configuration[ 'url' ].get( 'BASE' ))


if __name__ == '__main__':
    FileBasedConfiguration.load()
    print(FileBasedConfiguration.canvas_token)
