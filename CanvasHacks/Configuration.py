"""
Created by adam on 1/31/19
"""
# from CanvasHacks.PeerReviewed.Definitions import Unit

__author__ = 'adam'
import configparser
import os
from canvasapi import Canvas

# Needed for managing some test cases
import CanvasHacks.testglobals
from CanvasHacks.Definitions.unit import Unit

CREDENTIALS_FOLDER_PATH = "{}/private"
LIVE_CREDENTIALS = "{}/canvas-credentials.ini"
TEST_CREDENTIALS = "{}/test-credentials.ini"


class Configuration( object ):
    """
    Holds all global values.

    Attributes
    ---------
    assignments: list
        Which assignments we should be grading

    discussions: list
        Which discussions we should grading

    course: Canvas.Course
         The canvas api object to use for the current course
    course_ids: list
         Id numbers of courses to act upon

    canvas_token: str or False
        The user's access token for the canvas api

    canvas_url_base: str or False
        The url to be used in all calls

    excluded_users: list
        Ids of users, e.g., the teacher to exclude from grading operations

    is_test: bool
        Whether we are currently in the test environment

    unit: Unit
        The unit currently being acted upon

    unit_store: dict
        Other unit objects which have been previously loaded
        to avoid the performance hit of loading them multiple times.

    """
    archive_folder = False
    # Which assignments we should be grading
    assignments = [ ]
    # Which discussions we should grading
    discussions = []
    # canvas api object
    course = None
    course_ids = [ ]
    canvas_token = False
    canvas_url_base = False
    # Ids of users, e.g., the teacher to exclude from grading operations
    excluded_users = []
    # Whether in test environment
    is_test = False
    log_folder = False
    # a Unit definition object
    unit = None
    unit_store = {}
    unit_number = None
    test_course_id = None

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
    def add_discussion( cls, topic_id, name=None ):
        cls.discussions.append( (topic_id, name) )
        cls.discussions = list( set( cls.discussions ) )

    @classmethod
    def add_excluded_user( cls, user_id ):
        cls.excluded_users.append(user_id)
        cls.excluded_users = list(set(cls.excluded_users))

    @classmethod
    def get_assignment_ids( cls ):
        return [ i[ 0 ] for i in cls.assignments ]

    @classmethod
    def get_discussion_ids( cls ):
        return [ i[ 0 ] for i in cls.discussions ]

    @classmethod
    def remove_assignment( cls, assignment_id ):
        el = list( filter( lambda x: x[ 0 ] == assignment_id, cls.assignments ) )[ 0 ]
        idx = cls.assignments.index( el )
        return cls.assignments.pop( idx )

    @classmethod
    def remove_discussion( cls, topic_id ):
        el = list( filter( lambda x: x[ 0 ] == topic_id, cls.discussions ) )[ 0 ]
        idx = cls.discussions.index( el )
        return cls.discussions.pop( idx )

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

    @classmethod
    def load_section_ids( cls ):
        try:
            for v in cls.configuration[ 'sections' ].values():
                cls.add_course_id( int(v) )
        except:
            pass

    # --------------- Test vs live
    @classmethod
    def set_test( cls ):
        """Tells to set all variables to test settings"""
        cls.is_test = True
        # set course id
        test_id = cls.configuration['testing'].get('TEST_COURSE_ID')
        cls.course_ids = [int(test_id)]
        print(" ".join([" TEST " for _ in range(0, 5)]))
        # Set on the global variable (which is only used in certain tests)
        CanvasHacks.testglobals.TEST = True

    @classmethod
    def set_live( cls ):
        """Set all variables to live setting"""
        cls.is_test = False
        # clear out possible test values
        cls.course_ids = []
        # Set to the stored course ids
        cls.load_section_ids()
        print(" ".join([" LIVE " for _ in range(0, 5)]))
        # Set on the global variable (which is only used in certain tests)
        CanvasHacks.testglobals.TEST = False

    # --------------- Unit object management
    @classmethod
    def get_unit_from_storage(cls, unit_number):
        return cls.unit_store

    # ------------ Unit selection
    @classmethod
    def set_unit_number( cls, unit_number, name=None ):
        cls.unit_number = unit_number

    @classmethod
    def set_unit( cls, unit ):
        """
        Takes a unit object or its unit number and sets
        all relevant values.
        This should replace the older versions
        Introduced in CAN-68

        :param unit: int or Unit
        :return:
        """
        if isinstance(unit, int):
            # we presumably received the unit number
            # if we got the unit number, we load the unit object
            # First we see if we already have it in storage
            try:
                unit = cls.retrieve_unit_object(unit)
            except KeyError:
                # The unit is not present in storage, so we load it
                cls.initialize_canvas_objs()
                # unit = {}
                unit = Unit( cls.course, unit )

        # Now we can set it and related values directly
        cls.unit = unit
        cls.unit_number = unit.unit_number
        # We store it for future use
        cls.store_unit_object(unit)
        # Finally, we return it since some other processes
        # will call this as part of assembling their own collection
        # of unit objects
        return unit


    @classmethod
    def initialize_canvas_objs( cls ):
        """Sets a canvas, course, and unit object on the config
        Creates a unit object by downloading from canvas using the first defined course id
        todo Make this work with multiple courses
        """

        COURSE_ID = cls.course_ids[0]
        # print("Working on course: ", COURSE_ID)
        print(f"url base: {cls.canvas_url_base} \n course id: {COURSE_ID}")
        cls.canvas = Canvas(cls.canvas_url_base, cls.canvas_token)
        cls.course = cls.canvas.get_course(COURSE_ID)
        # if cls.unit_number is not None:
        #     cls.unit = Unit(cls.course, cls.unit_number)

    @classmethod
    def reset_unit_number( cls, dummy_param=None):
        cls.unit = None
        cls.unit_number = None

    @classmethod
    def get_unit_number( cls ):
        """I know, stupid. But it parallels other methods
        so the selection buttons will work the same"""
        return [cls.unit_number]

    @classmethod
    def store_unit_object( cls, unit ):
        """
        Puts a unit object which has already been loaded from
        canvas into storage so we don't need to load it again
        :param unit:
        :return:
        """
        cls.unit_store[unit.unit_number] = unit

    @classmethod
    def retrieve_unit_object( cls, unit_number ):
        """
        Tries to retrieve a stored unit object
        :param unit_number:
        :raises: KeyError
        :return:
        """
        try:
            return cls.unit_store[unit_number]
        except KeyError as e:
            # if create_if_absent:
            #     # todo
            #     pass
            raise e


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

    @classmethod
    def set_test( cls ):
        cls.is_test = True

    @classmethod
    def set_live( cls ):
        cls.is_test = False


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
        cls.semester_name = cls.configuration['names'].get('SEMESTER')
        cls.load_token()
        cls.load_email_password()
        cls.load_url_base()
        cls.load_local_filepaths()
        cls.load_section_ids()
        cls.load_excluded_users()
        cls.initialize_canvas_objs()


    @classmethod
    def load_local_filepaths( cls ):
        root = os.getenv( "HOME" )
        # class related data
        cls.archive_folder = "{}/{}".format(root, cls.configuration[ 'folders' ].get( 'STUDENT_WORK_ARCHIVE_FOLDER' ))
        cls.log_folder = "{}/{}".format(root, cls.configuration[ 'folders' ].get( 'LOG_FOLDER' ))
        cls.assessment_data_folder = "{}/{}".format(root, cls.configuration[ 'folders' ].get( 'ASSESSMENT_DATA_FOLDER' ))

        # canvas hacks program folders
        cls.data_folder = '{}/data'.format(cls.proj_base)

        cls.course_folder_root = f"{root}/{cls.configuration['folders'].get('COURSE_FOLDER_ROOT')}/Phil305 {cls.semester_name}"

    @classmethod
    def load_email_password(cls):
        cls.email_password = cls.configuration['credentials'].get('EMAIL_PASSWORD')

    @classmethod
    def load_token( cls ):
        if not cls.configuration:
            cls.read_config_file()

        cls.add_canvas_token( cls.configuration[ 'credentials' ].get( 'TOKEN' ) )

    @classmethod
    def load_url_base( cls ):
        cls.add_canvas_url_base( cls.configuration[ 'url' ].get( 'BASE' ) )

    @classmethod
    def load_excluded_users( cls ):
        try:
            for v in cls.configuration[ 'excluded_users' ].values():
                cls.add_excluded_user(int(v))
            print("Will ignore work by users: ", cls.excluded_users)
        except:
            pass


class TestingConfiguration( Configuration ):
    def __init__( self ):
        type(self).is_test = True

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

    @classmethod
    def set_test( cls ):
        cls.is_test = True

    @classmethod
    def set_live( cls ):
        cls.is_test = False



if __name__ == '__main__':
    FileBasedConfiguration.load()
    print( FileBasedConfiguration.canvas_token )
