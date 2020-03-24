"""
Created by adam on 9/14/18
"""
__author__ = 'adam'

import os

import CanvasHacks.testglobals

if CanvasHacks.testglobals.TEST:
    print( "RUNNING IN TEST MODE" )

# Putting this here for an easy place to manually
# toggle, since it only needs to be true when
# testing against server.
CanvasHacks.testglobals.TEST_WITH_FILE_DB = False

from CanvasHacks.Configuration import FileBasedConfiguration, InteractiveConfiguration, TestingConfiguration

ROOT = os.getenv( "HOME" )

if CanvasHacks.testglobals.use_api:
    # Check whether it is being run on my machine or remotely
    if ROOT[ :12 ] == '/Users/adam':
        FileBasedConfiguration.load( CanvasHacks.testglobals.TEST )
        CONFIG = FileBasedConfiguration
        TEMP_DATA_PATH = "%s/temp" % FileBasedConfiguration.proj_base
        ARCHIVE_FOLDER = FileBasedConfiguration.archive_folder
        JOURNAL_ARCHIVE_FOLDER = "%s/Journals" % ARCHIVE_FOLDER
        LOG_FOLDER = FileBasedConfiguration.log_folder
        DATA_FOLDER = "%s/data" % FileBasedConfiguration.proj_base
        DOWNLOAD_FOLDER = "{}/Downloads"
        # Testing
        TEST_DATA_PATH = "{}/tests/testdata".format( FileBasedConfiguration.proj_base )

        TOKEN = FileBasedConfiguration.canvas_token
        URL_BASE = FileBasedConfiguration.canvas_url_base

    else:
        CONFIG = InteractiveConfiguration
        TOKEN = InteractiveConfiguration.canvas_token
        URL_BASE = InteractiveConfiguration.canvas_url_base
        # Logging should stream
        LOG_FOLDER = None
else:
    # Testing without api access
    CONFIG = TestingConfiguration
    if CanvasHacks.testglobals.TEST:
        CONFIG.is_test = CanvasHacks.testglobals.TEST
    LOG_FOLDER = None

# DB
REVIEW_ASSOCIATIONS_TABLE_NAME = "review_associations"
STATUS_TABLE_NAME = 'status'
COMPLEX_STATUS_TABLE_NAME = 'complexstatus'
FEEDBACK_RECEIVED_STATUS_TABLE_NAME = 'feedback_received'
INVITATION_RECEIVED_STATUS_TABLE_NAME = 'invitation_received'
SUBMISSION_TABLE_NAME = 'submissions'

STUDENT_TABLE_NAME = 'students'

# Logging
t = "TEST-" if CONFIG.is_test else ""
STUDENT_WORK_PROCESSING_LOGNAME = '{}student-work-processing-log.txt'.format( t )
MESSAGE_LOGNAME = "{}message-log.txt".format( t )
RUN_LOGNAME = "{}run-log.txt".format( t )

# Plotting stuff
LIKERT_PLOT_ORDER = [ 'Forgot', 'Strongly disagree', 'Disagree', 'Agree', 'Strongly agree' ]
LIKERT_NUM_MAP = { 'Forgot': 0, 'Strongly disagree': 1, 'Disagree': 2, 'Agree': 3, 'Strongly agree': 4 }

# File stuff
REPORT_KEEP_COLUMNS = [ 'attempt', 'course_id', 'finished_at_date',
                        'fudge_points', 'id', 'name', 'quiz_id', 'score',
                        'section_sis_id', 'student_id', 'submission_id', 'user_id', 'workflow_state' ]
