"""
Created by adam on 2/24/20
"""
import pandas as pd

__author__ = 'adam'

if __name__ == '__main__':
    pass


def process_work( work_frame, submissions_frame ):
    try:
        v = work_frame[ 'student_id' ]
    except KeyError:
        work_frame.rename( { 'id': 'student_id' }, axis=1, inplace=True )
    # merge it with matching rows from the submissions frame
    frame = pd.merge( work_frame, submissions_frame, how='left', on=[ 'student_id', 'attempt' ] )
    try:
        # Try to sort it on student names if possible
        frame.set_index( 'name', inplace=True )
        frame.sort_index( inplace=True )
    except KeyError:
        pass
    return frame


def remove_non_final_attempts( frame ):
    """Can only be ran after submission has been added?"""
    frame.dropna( subset=[ 'submission_id' ], inplace=True )


def make_drop_list( columns ):
    """The canvas exports will have some annoying fields
        These should be added to the droppable list
        If there are columns with a common initial string (e.g., 1.0, 1.0.1, ...) just
        add the common part
    """

    droppable = [ '1.', 'Unnamed' ]
    to_drop = ['n correct', 'n incorrect' ]
    for c in columns:
        try:
            if float( c ):
                to_drop.append( c )
        except ValueError:
            for d in droppable:
                if c[ :len( d ) ] == d:
                    to_drop.append( c )
    return to_drop


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


def drop_columns_from_frame( frame ):
    to_drop = make_drop_list( frame.columns )
    frame.drop( to_drop, axis=1, inplace=True )
    print( "Removed: ", to_drop )