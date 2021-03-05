"""
Created by adam on 10/18/20
"""

import datetime

import pandas as pd

from CanvasHacks import environment as env
from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.TimeTools import getDateForMakingFileName

LOG_PATH_TEMPLATE = "{path}/{date}-Unit{unit_number}{testing} {assignment} Nagging message log.csv"


def log_nag_messages( activity: Activity, list_of_sent_messages: list, is_dry_run=False ):
    """
    Writes the details of how points were determined to
    the logfile.

    :param list_of_sent_messages: [ (student id, message text) ]
    :param activity:
    :param is_dry_run:
    :return:
    """
    ms = [ {'student_id' : m[0], 'message': m[1]} for m in list_of_sent_messages]
    # make the list into a frame
    frame = pd.DataFrame( ms )
    # add details
    frame[ 'activity' ] = activity.activity_name
    frame[ 'timestamp' ] = datetime.datetime.now().isoformat()


    # save
    v = { 'path': env.LOG_FOLDER,
          'date': getDateForMakingFileName(),
          'unit_number': activity.unit_number,
          'assignment' : activity.activity_name,
          'testing' : "-DRY RUN" if is_dry_run else ""
          }

    filepath = LOG_PATH_TEMPLATE.format( **v )
    frame.to_csv( filepath )
    print( "Record of nagging saved to ", filepath )

