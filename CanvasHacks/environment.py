"""
Created by adam on 9/14/18
"""
__author__ = 'adam'

import os
from CanvasHacks.Configuration import FileBasedConfiguration, InteractiveConfiguration

ROOT = os.getenv( "HOME" )

# Check whether it is being run on my machine or remotely
if ROOT[:12] == '/Users/adam':
    FileBasedConfiguration.load()
    CONFIG = FileBasedConfiguration
    TEMP_DATA_PATH = "%s/temp" % FileBasedConfiguration.proj_base
    ARCHIVE_FOLDER = FileBasedConfiguration.archive_folder
    JOURNAL_ARCHIVE_FOLDER = "%s/Journals" % ARCHIVE_FOLDER
    LOG_FOLDER = FileBasedConfiguration.log_folder
    DATA_FOLDER = FileBasedConfiguration.proj_base

    TOKEN = FileBasedConfiguration.canvas_token
    URL_BASE = FileBasedConfiguration.canvas_url_base

else:
    CONFIG = InteractiveConfiguration
    TOKEN = InteractiveConfiguration.canvas_token
    URL_BASE = InteractiveConfiguration.canvas_url_base
