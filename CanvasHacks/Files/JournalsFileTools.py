"""
todo This is very much tied to my own filesystem and needs. Should be abstracted.
Created by adam on 10/26/18
"""
__author__ = 'adam'

import csv
import json
import os

from CanvasHacks import environment

# DATA_FOLDER = '%s/data' % environment.CONFIG.proj_base

# JOURNAL_ARCHIVE_FOLDER = "%s/Journals" % environment.CONFIG.archive_folder
# LOG_FOLDER = environment.CONFIG.log_folder


# ----------------- create files

def journal_folder_name( journal_name, course_id, journal_folder=None ):
    """Creates a folder to store student work for the unit
    If want to use a custom destination, set that via journal_folder
    otherwise keeping the call to environment inside the function so won't
    kill everything on system load
    """
    journal_folder = environment.JOURNAL_ARCHIVE_FOLDER if journal_folder is None else journal_folder
    folder_name = journal_name.replace( '(', '' ).replace( ')', '' ).replace( ' ', '-' )
    return "%s/%s-%s" % (journal_folder, course_id, folder_name)


def get_journal_folders( journal_archive=None ):
    """Constructs paths to all journal folders and returns the list
        example result: [
            '/Users/adam/Box Sync/Phil 305 Business ethics/Student work/41181-Journal-week-2',
             '/Users/adam/Box Sync/Phil 305 Business ethics/Student work/41181-Journal-week-3',
             ....
    """
    journal_archive = environment.JOURNAL_ARCHIVE_FOLDER if journal_archive is None else journal_archive
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


def load_words_to_ignore( file=None ):
    file = environment.IGNORE_FILE if file is None else file
    words = [ ]
    with open( file, 'r' ) as csvfile:
        reader = csv.DictReader( csvfile )  # , delimiter=',', quotechar='|')
        for row in reader:
            #             print (row['journals'])
            words.append( row[ 'journals' ] )
    return words


def week_key_gen(start=2, stop=16):
    """Create an iterator for all the keys to the various dictionaries"""
    for i in range(start, stop):
        yield "w%s" % i


if __name__ == '__main__':
    pass
