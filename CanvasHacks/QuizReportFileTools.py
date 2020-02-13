"""
Created by adam on 2/10/20
"""
__author__ = 'adam'

import pandas as pd

from CanvasHacks.FileTools import makeDataFileIterator

def get_newest_data(activity):
    # get data from newest file
    fiter = makeDataFileIterator( activity.folder_path )
    report_frames = [ ]
    try:
        while True:
            f = next( fiter )
            # print( "loading: ", f )
            frame = pd.read_csv( f )
            frame.submitted = pd.to_datetime( frame.submitted )
            if 'student_id' not in frame.index:
                frame.rename( { 'id': 'student_id' }, axis=1, inplace=True )
            # this makes it freak out for some reason
            #         frame.set_index('student_id', inplace=True)
            report_frames.append( frame )
    except StopIteration:
        return sort_frames_by_age( report_frames )[0]


def sort_frames_by_age( quiz_report_frames ):
    """Sorts the list of frames so that the newest
    is first, the oldest is last"""
    # assumes submitted is a datetime
    quiz_report_frames.sort( key=lambda x: x.submitted.max(), reverse=True )
    return quiz_report_frames


def get_whats_new( quiz_report_frames ):
    """Given a list of quiz report dataframes, returns a dataframe
    of the things that are new since the last time the data was checked
    """
    if len( quiz_report_frames ) == 1:
        return quiz_report_frames[ 0 ]
    sort_frames_by_age( quiz_report_frames )
    latest = quiz_report_frames[ 0 ]
    previous = quiz_report_frames[ 1 ]
    # Anything which happened after the last check of the data
    return latest[ latest.submitted > previous.submitted.max() ]


def load_new( activity ):
    """Returns a dataframe containing everything that is new in the most
    recent file since the next most recent file.

    NB, this is not equivalent to all the records which have not been
    acted upon since it is possible that no action was taken on the
    records in the next most recent file."""
    fiter = makeDataFileIterator( activity.folder_path )
    report_frames = [ ]
    try:
        while True:
            f = next( fiter )
            print( "loading: ", f )
            frame = pd.read_csv( f )
            frame.submitted = pd.to_datetime( frame.submitted )
            if 'student_id' not in frame.index:
                frame.rename( { 'id': 'student_id' }, axis=1, inplace=True )
            # this makes it freak out for some reason
            #         frame.set_index('student_id', inplace=True)
            report_frames.append( frame )
    except StopIteration:
        newstuff = get_whats_new( report_frames )
        print( "{} new records since previous file".format( len( newstuff ) ) )
        return newstuff


if __name__ == '__main__':
    pass
