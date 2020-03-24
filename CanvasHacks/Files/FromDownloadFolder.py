"""
This contains the tools for finding reports in the downloads folder
and moving them to the appropriate locations

Created by adam on 3/24/20
"""
__author__ = 'adam'

import os
import re
import shutil
from functools import wraps
from CanvasHacks import environment as env
from CanvasHacks.PeerReviewed.Definitions import Unit
from CanvasHacks.TimeTools import current_utc_timestamp, timestamp_for_unique_filenames


UNIT_RX = re.compile( r"(\bunit\b) (\d+)" )

DOWNLOAD_FOLDER = "{}/Downloads".format(env.ROOT)


def normalize_filename( f ):
    @wraps( f )
    def d( *args, **kwargs ):
        fname = args[ 0 ].strip().lower()
        return f( fname, **kwargs )

    return d


@normalize_filename
def is_csv( filename ):
    """
    Returns true if filename ends in csv
    :param filename:
    :return:
    """
    # f = filename.strip().lower()
    return filename[ -4: ] == '.csv'


@normalize_filename
def is_report( filename ):
    """
    Returns true if seems to be a report, false otherwise
    :param filename:
    :return:
    """
    # f = filename.strip().lower()

    return UNIT_RX.search( filename ) is not None


@normalize_filename
def get_unit_number( filename ):
    # f = filename.strip().lower()
    match = UNIT_RX.search( filename )
    # start = match.span[0]
    # stop = match.span[1]
    return int( match.group( 2 ) )


@normalize_filename
def get_activity_type( filename ):
    for c in Unit.component_types:
        if c.is_activity_type( filename ):
            return c


def report_file_iterator( folderPath, exclude=[ ] ):
    exclude = exclude if any( exclude ) else [ '.DS_Store' ]
    for root, dirs, files in os.walk( folderPath ):
        for name in files:
            if name not in exclude:
                if is_csv( name ) and is_report( name ):
                    path = os.path.join( root, name )
                    d = {
                        'unit_number': get_unit_number( name ),
                        'file_name': name,
                        'path': path,
                        'activity': get_activity_type( name )
                    }
                    yield d


def file_reports(download_folder_path, unit_start=1, unit_stop=6):
    """
    Moves reports found in the download folder to the
    correct folder
    :param download_folder_path:
    :return:
    """

    units = { u:  Unit( env.CONFIG.course, u ) for u in range(unit_start, unit_stop + 1) }
    fiter = report_file_iterator( download_folder_path )
    moved_files = []
    try:
        while True:
            f = next(fiter)
            if f['activity'] is not None:
                unit = units.get(f['unit_number'])
                activity = unit.get_by_class(f['activity'])
                src = f['path']

                # Rename with timestamp so no collisions
                # THIS DOES NOT GUARANTEE THAT THE NEWEST FILE CAN BE DETERMINED BY
                # TIMESTAMP!
                to = "{}/{} {}".format(activity.folder_path, timestamp_for_unique_filenames(), f['file_name'])
                shutil.move(src, to)
                moved_files.append({'from': src, 'to': to})

    except StopIteration:
        for f in moved_files:
            print("\n----\n FROM: {from} \n TO: {to}".format(**f))
        return moved_files


if __name__ == '__main__':
    DOWNLOAD_FOLDER = "{}/Downloads".format( env.ROOT )

    file_reports(DOWNLOAD_FOLDER)
