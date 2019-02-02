"""
Created by adam on 10/26/18
"""
__author__ = 'adam'

import csv
import json
import os

from assets import environment

DATA_FOLDER = '%s/data' % environment.PROJ_BASE
IGNORE_FILE = "%s/ignore.csv" % DATA_FOLDER


# ----------------- create files

def journal_folder_name( journal_name, course_id, journal_folder=environment.JOURNAL_ARCHIVE_FOLDER ):
    """Creates a folder to store student work for the assignment"""
    folder_name = journal_name.replace( '(', '' ).replace( ')', '' ).replace( ' ', '-' )
    return "%s/%s-%s" % (journal_folder, course_id, folder_name)


def create_folder( folder_path ):
    try:
        os.mkdir( folder_path )
        print( "created: %s" % folder_path )
    except:
        print( "error creating: %s" % folder_path )
        pass


def get_journal_folders( journal_archive=environment.JOURNAL_ARCHIVE_FOLDER ):
    """Constructs paths to all journal folders and returns the list
        example result: [
            '/Users/adam/Box Sync/Phil 305 Business ethics/Student work/41181-Journal-week-2',
             '/Users/adam/Box Sync/Phil 305 Business ethics/Student work/41181-Journal-week-3',
             ....
    """
    journal_folders = [ ]
    for root, dirs, files in os.walk(journal_archive):
        for d in dirs:
            journal_folders.append( os.path.join( root, d ) )
    return journal_folders


def make_folder_list( sections, week_num ):
    return [ "%s-Journal-week-%s" % (s, week_num) for s in sections ]


# counts from each week
def calculate_journal_counts( journal_folders, data_file_name='all-submissions' ):
    """Returns the count of journals for each week"""
    cnt = [ ]
    for r in journal_folders:
        with open( "%s/%s.json" % (r, data_file_name), 'r' ) as f:
            j = json.load( f )
        cnt.append( (r.split( '/' )[ -1: ], len( j )) )
    return cnt


def load_words_to_ignore( file=IGNORE_FILE ):
    words = [ ]
    with open( file, 'r' ) as csvfile:
        reader = csv.DictReader( csvfile )  # , delimiter=',', quotechar='|')
        for row in reader:
            #             print (row['journals'])
            words.append( row[ 'journals' ] )
    return words


if __name__ == '__main__':
    pass
