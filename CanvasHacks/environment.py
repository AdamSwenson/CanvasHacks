"""
Created by adam on 9/14/18
"""
__author__ = 'adam'

# TEST = True
TEST = False
if TEST:
    print("RUNNING IN TEST MODE")

import os
from CanvasHacks.Configuration import FileBasedConfiguration, InteractiveConfiguration

ROOT = os.getenv( "HOME" )

REVIEW_ASSOCIATIONS_TABLE_NAME = "review_associations"
STUDENT_TABLE_NAME = 'students'

STUDENT_WORK_PROCESSING_LOGNAME = '{}/student-work-processing-log.txt'

# Check whether it is being run on my machine or remotely
if ROOT[:12] == '/Users/adam':
    FileBasedConfiguration.load(TEST)
    CONFIG = FileBasedConfiguration
    TEMP_DATA_PATH = "%s/temp" % FileBasedConfiguration.proj_base
    ARCHIVE_FOLDER = FileBasedConfiguration.archive_folder
    JOURNAL_ARCHIVE_FOLDER = "%s/Journals" % ARCHIVE_FOLDER
    LOG_FOLDER = FileBasedConfiguration.log_folder
    DATA_FOLDER = "%s/data" % FileBasedConfiguration.proj_base

    TOKEN = FileBasedConfiguration.canvas_token
    URL_BASE = FileBasedConfiguration.canvas_url_base

else:
    CONFIG = InteractiveConfiguration
    TOKEN = InteractiveConfiguration.canvas_token
    URL_BASE = InteractiveConfiguration.canvas_url_base
    # Logging should stream
    LOG_FOLDER = None
