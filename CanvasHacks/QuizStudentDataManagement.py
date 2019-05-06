"""
Created by adam on 5/6/19
"""
__author__ = 'adam'

import pandas as pd


def load_student_work( csv_filepath, submissions ):
    """Loads and processes a csv file containing all student work for the assignment
    submissions: DataFrame containing student submission objects
    """
    f = pd.read_csv( csv_filepath )
    # rename id so will be able to join
    f.rename( { 'id': 'student_id' }, axis=1, inplace=True )
    # merge it with matching rows from the submissions frame
    f = pd.merge( f, submissions, how='left', on=[ 'student_id', 'attempt' ] )
    f.set_index( 'name', inplace=True )
    f.sort_index( inplace=True )
    return f


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


if __name__ == '__main__':
    pass
