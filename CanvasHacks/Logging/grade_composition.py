"""
Tools for logging the composition of grades, e.g., how many points were assigned
by what method

Created by adam on 9/26/20
"""
__author__ = 'adam'

import datetime

import pandas as pd

from CanvasHacks import environment as env
from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.TimeTools import getDateForMakingFileName

LOG_PATH_TEMPLATE = "{path}/{date}-Unit{unit_number}{testing} Grade points basis.csv"


def log_points( activity: Activity, list_of_points_records: list, is_dry_run=False ):
    """
    Writes the details of how points were determined to
    the logfile.

    :param studentRepo:
    :param activity:
    :param list_of_points_records:
    :param is_dry_run:
    :return:
    """
    # make the list into a frame
    frame = pd.DataFrame( [ d.data_for_log_entry for d in list_of_points_records ] )
    # add details
    frame[ 'activity' ] = activity.activity_name
    frame[ 'timestamp' ] = datetime.datetime.now().isoformat()

    # Do this if we've been given a student repo for looking up names etc


    # save
    v = { 'path': env.LOG_FOLDER,
          'date': getDateForMakingFileName(),
          'unit_number': activity.unit_number,
          'testing' : "-DRY RUN" if is_dry_run else ""}

    filepath = LOG_PATH_TEMPLATE.format( **v )
    frame.to_csv( filepath )
    print( "Record of grade points saved to ", filepath )


if __name__ == '__main__':
    pass
