"""
Created by adam on 2/24/20
"""
import json

from CanvasHacks import environment as env

__author__ = 'adam'

if __name__ == '__main__':
    pass


def save_to_log_folder( frame ):
    section = frame.iloc[ 0 ][ 'section' ]
    qid = frame.iloc[ 0 ][ 'quiz_id' ]
    fname = "%s/%s-%s-results.xlsx" % (env.LOG_FOLDER, section, qid)
    print( "Saving to ", fname )
    frame.to_excel( fname )


def save_json( grade_data, quiz_data_obj ):
    fpath = "%s/%s-%s-all-submissions.json" % (env.LOG_FOLDER, quiz_data_obj.course_id, quiz_data_obj.id)
    # save submissions
    with open( fpath, 'w' ) as fpp:
        json.dump( grade_data, fpp )