"""
Created by adam on 5/6/19
"""
from CanvasHacks.Models.student import Student
from CanvasHacks.QuizGrading import get_penalty

__author__ = 'adam'

import pandas as pd

from CanvasHacks import environment as env
import json

def process_work( work_frame, submissions_frame ):
    work_frame.rename( { 'id': 'student_id' }, axis=1, inplace=True )
    # merge it with matching rows from the submissions frame
    frame = pd.merge( work_frame, submissions_frame, how='left', on=[ 'student_id', 'attempt' ] )
    frame.set_index( 'name', inplace=True )
    frame.sort_index( inplace=True )
    return frame


def load_student_work( csv_filepath, submissions ):
    """Loads and processes a csv file containing all student work for the assignment
    submissions: DataFrame containing student submission objects
    NB, process_work has been refactored out in CAN-11 but load_student_work
    is still here for legacy uses
    """
    f = pd.read_csv( csv_filepath )
    return process_work( f, submissions )
    # # rename id so will be able to join
    # f.rename( { 'id': 'student_id' }, axis=1, inplace=True )
    # # merge it with matching rows from the submissions frame
    # f = pd.merge( f, submissions, how='left', on=[ 'student_id', 'attempt' ] )
    # f.set_index( 'name', inplace=True )
    # f.sort_index( inplace=True )
    # return f


# def detect_question_columns(columns):
#     """Return a list of columns which contain a colon,
#     those probably contain the question answers
#     """
#     return [c for c in columns if len(c.split(':')) > 1]


# test = [ 'submitted', 'attempt',"1785114: \nWhat is an example of persuasive advertising?", '1.0']
# assert(detect_question_columns(test) == [ "1785114: \nWhat is an example of persuasive advertising?"])
# Limit to just the final attempts

def remove_non_final_attempts( frame ):
    frame.dropna( subset=[ 'submission_id' ], inplace=True )


#     return frame[pd.notnull(frame['submission_id'])]

def make_drop_list( columns ):
    """The canvas exports will have some annoying fields
        These should be added to the droppable list
        If there are columns with a common initial string (e.g., 1.0, 1.0.1, ...) just
        add the common part
    """
    droppable = [ '1.0' ]
    to_drop = [ ]
    for d in droppable:
        for c in columns:
            if c[ :len( d ) ] == d:
                to_drop.append( c )
    return to_drop


# test = [ 'name', 'id', 'sis_id', '1.0', '1.0.1', '1.0.2' ]
# assert (make_drop_list( test ) == [ '1.0', '1.0.1', '1.0.2' ])


def drop_columns_from_frame( frame ):
    to_drop = make_drop_list( frame.columns )
    frame.drop( to_drop, axis=1, inplace=True )
    print( "Removed: ", to_drop )


def check_responses( row, question_columns ):
    score = 0
    for c in question_columns:
        try:
            if pd.isnull( row[ c ] ):
                raise Exception

            # No credit for 1 word answers
            if len( row[ c ] ) < 2:
                raise Exception

            # If we made it past the tests, increment the score
            score += 1
        except Exception:
            pass

    return score


def add_graded_total_field( frame, question_columns ):
    frame[ 'graded_total' ] = frame.apply( lambda r: check_responses( r, question_columns ), axis=1 )


def save_to_log_folder( frame ):
    section = frame.iloc[ 0 ][ 'section' ]
    qid = frame.iloc[ 0 ][ 'quiz_id' ]
    fname = "%s/%s-%s-results.xlsx" % (env.LOG_FOLDER, section, qid)
    print( "Saving to ", fname )
    frame.to_excel( fname )


def grade( frame, quiz_data_obj, grace_period=None ):
    """
    This handles the actual grading

    quiz_data_obj will have the payload format:
        "quiz_submissions": [{
        "attempt": int(attempt),
        "fudge_points": total_score
      },
          "questions": {
      "QUESTION_ID": {
        "score": null, // null for no change, or an unsigned decimal
        "comment": null // null for no change, '' for no comment, or a string
      }
    """
    results = [ ]
    #     questions = detect_question_columns(frame.columns)

    for i, row in frame.iterrows():
        fudge_points = 0
        out = {
            'student_id': int( row[ 'student_id' ] ),
            'attempt': int( row[ 'attempt' ] ),
            'submission_id': int( row[ 'submission_id' ] ),
            'course_id': int( row[ 'course_id' ] ),
            'quiz_id': int( row[ 'quiz_id' ] ),
            'data': { }
        }
        # used for computing penalty
        total_score = 0
        questions = { }

        for qid, column_name in quiz_data_obj.question_columns:
            if pd.isnull( row[ column_name ] ):
                questions[ qid ] = { 'score': 0 }
            else:
                questions[ qid ] = { 'score': 1.0 }
                total_score += 1

        # compute penalty if needed
        penalty = get_penalty( row[ 'submitted' ], quiz_data_obj.due_date, quiz_data_obj.quarter_credit_date,
                               grace_period )
        # will be 0 if not docking
        fudge_points = total_score * -penalty
        if penalty > 0:
            print( 'Student #{}: Submitted on {}; was due {}. Penalized {}'.format( row[ 'student_id' ], row[ 'submitted' ], quiz_data_obj.due_date, penalty ) )

        out[ 'data' ][ "quiz_submissions" ] = [
            {
                "attempt": int( row[ 'attempt' ] ),
                "fudge_points": fudge_points,
                "questions": questions
            }
        ]

        results.append( out )
    return results


def save_json( grade_data, quiz_data_obj ):
    fpath = "%s/%s-%s-all-submissions.json" % (env.LOG_FOLDER, quiz_data_obj.course_id, quiz_data_obj.id)
    # save submissions
    with open( fpath, 'w' ) as fpp:
        json.dump( grade_data, fpp )


class QuizRepository( object ):
    """Manages the data for a quiz type assignment"""

    def __init__( self, activity ):
        self.activity = activity

    def _process( self, work_frame, submissions ):
        self.submissions = submissions
        if not isinstance(submissions, pd.DataFrame):
            submissions_frame = pd.DataFrame(submissions)
        else:
            submissions_frame = submissions
        submissions_frame['student_id'] = submissions_frame.user_id
        self.data = process_work( work_frame, submissions_frame )
        remove_non_final_attempts(self.data)
        # the name will be set as index from sorting
        # so we set to student id to make look ups easier
        self.data.set_index('student_id', inplace=True)
        # Remove unneeded columns
        # self.data = self.data[self.activity.question_columns]

    def get_student_work( self, student ):
        return self.data.iloc[student.student_id]

    @property
    def submitters( self ):
        """returns a list of student objects for whom work has been submitted"""
        return [ Student(s) for s in self.data.student_id.tolist() ]



if __name__ == '__main__':
    pass
