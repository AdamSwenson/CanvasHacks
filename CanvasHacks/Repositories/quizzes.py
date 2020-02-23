"""
Created by adam on 5/6/19
"""
from CanvasHacks.Models.QuizModels import QuizDataMixin
from CanvasHacks.Models.student import Student
from CanvasHacks.PeerReviewed.Definitions import Review
from CanvasHacks.Repositories.IRepositories import IRepo, StudentWorkRepo
from CanvasHacks.Widgets.AssignmentSelection import make_selection_button

__author__ = 'adam'

import pandas as pd

from CanvasHacks import environment as env
import json

from CanvasHacks.PeerReviewed.Notifications import make_prompt_and_response
from CanvasHacks.Repositories.IRepositories import ContentRepository

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
    """Can only be ran after submission has been added?"""
    frame.dropna( subset=[ 'submission_id' ], inplace=True )


#     return frame[pd.notnull(frame['submission_id'])]

def make_drop_list( columns ):
    """The canvas exports will have some annoying fields
        These should be added to the droppable list
        If there are columns with a common initial string (e.g., 1.0, 1.0.1, ...) just
        add the common part
    """

    droppable = [ '1.' ]
    to_drop = [ ]
    for c in columns:
        try:
            if float( c ):
                to_drop.append( c )
        except ValueError:
            for d in droppable:
                if c[ :len( d ) ] == d:
                    to_drop.append( c )
    return to_drop


#     to_drop = [ ]
#     for d in droppable:
#         for c in columns:
#             if c[ :len( d ) ] == d:
#                 to_drop.append( c )
#     return to_drop


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


def save_json( grade_data, quiz_data_obj ):
    fpath = "%s/%s-%s-all-submissions.json" % (env.LOG_FOLDER, quiz_data_obj.course_id, quiz_data_obj.id)
    # save submissions
    with open( fpath, 'w' ) as fpp:
        json.dump( grade_data, fpp )


class SelectableMixin:
    """Allows to store a list of column names
    that have been specially designaged by the user
    """

    def _init_selected( self ):
        try:
            if len( self.selected ) > 0:
                pass
        except Exception as e:
            print( e )
            self.selected = [ ]

    def select( self, identifier, name=None ):
        self._init_selected()
        self.selected.append( identifier )

    def deselect( self, identifier ):
        self.selected.pop( self.selected.index( identifier ) )

    def get_selections( self ):
        self._init_selected()
        return self.selected

    def reset_selections( self ):
        self.selected = [ ]


class WorkRepositoryFactory:
    """Decides what kind of repository is needed
    and instantiates it"""

    def make( self, activity, course=None ):
        # Get quiz submission objects
        if isinstance( activity, Review ):
            repo = ReviewRepository( activity, course )
        else:
            repo = QuizRepository( activity, course )
        return repo


    # def __init__( self, activity, course=None ):
    #     # Get quiz submission objects
    #     if isinstance( activity, Review ):
    #         repo = ReviewRepository( activity, course )
    #     else:
    #         repo = QuizRepository( activity, course )
    #     return repo


class QuizRepository( ContentRepository, QuizDataMixin, StudentWorkRepo, SelectableMixin ):
    """Manages the data for a quiz type assignment"""

    def __init__( self, activity, course=None ):
        self.course = course
        self.activity = activity
        self.question_columns = [ ]

    def _process( self, work_frame, submissions ):
        self.submissions = submissions
        if not isinstance( submissions, pd.DataFrame ):
            submissions_frame = pd.DataFrame( submissions )
        else:
            submissions_frame = submissions

        # If we are loading from file the student_id may
        # already have been set
        # try:
        #     v = submissions_frame['student_id']
        # except KeyError:
        submissions_frame[ 'student_id' ] = submissions_frame.user_id
        self.data = process_work( work_frame, submissions_frame )
        remove_non_final_attempts( self.data )
        # finish setting up the dataframe
        self._cleanup_data()
        # Store the text column names
        self.set_question_columns( self.data )

    # def _initialize_quiz( self):
    #     """Downloads the quiz object corresponding to
    #     the activity. That's where things like number
    #     of points will be stored"""
    #     try:
    #         if self._quiz:
    #             pass
    #     except AttributeError:
    #         self._quiz = self.course.get_quiz(self.activity.quiz_id)

    def _cleanup_data( self ):
        """This is abstracted out so it can be
        called independently for use with test data
        """
        # Store ids so we don't have to reset the index for submitters prop
        # self.student_ids = list(set(self.data.student_id.tolist()))
        # the name will be set as index from sorting
        # so we set to student id to make look ups easier
        self.data.set_index( 'student_id', inplace=True )
        # Remove unneeded columns
        # self.data = self.data[self.activity.question_columns]

    def get_student_work( self, student_id ):
        try:
            return self.data.loc[ student_id ]
        except (ValueError, KeyError):
            # The student id may not be set as the index, depending
            # on the source of the data
            return self.data.set_index( 'student_id' ).loc[ student_id ]

    def get_formatted_work_by( self, student_id ):
        """Returns all review entries by the student, formatted for
        sending out for review or display"""
        work = self.get_student_work( student_id )
        # narrow down to just the relevant columns
        rs = [ { 'prompt': column_name, 'response': work[ column_name ] } for col_id, column_name in
               self.question_columns ]
        r = make_prompt_and_response( rs )
        return self._check_empty( r )

    def make_question_selection_buttons( self ):
        """Given a repository containing a dataframe and a
        list of names in question_names, this will allow to select
        which questions are used for things"""
        buttons = [ ]
        for q in self.question_names:
            b = make_selection_button( q, q, self.get_selections, self.select, self.deselect, '100%' )
            buttons.append( b )

    @property
    def points_per_question( self ):
        return self.quiz.points_possible / self.quiz.question_count

    @property
    def quiz( self ):
        """Returns the canvasapi.quiz.Quiz object associated
        with this repository.
        Automatically initializes it if not set
        """
        try:
            if self._quiz:
                pass
        except AttributeError:
            self._quiz = self.course.get_quiz( self.activity.quiz_id )
        return self._quiz

    @property
    def submitters( self ):
        """returns a list of student objects for whom work has been submitted"""
        return [ Student( s ) for s in self.student_ids ]


class ReviewRepository( QuizRepository ):
    """Quiz repo specific to needs of reviews.
    Basically just differs in implementation of
    get_formatted_work and related methods
    """

    def __init__( self, activity, course=None ):
        self.course = course
        self.activity = activity
        self.question_columns = [ ]
        if course:
            self.questions = self.course.get_quiz( self.activity.quiz_id ).get_questions()

    #
    # def _set_question_types( self ):
    #     def __init__( self, activity ):
    #         self.activity = activity
    #     self.question_columns = []

    # @property
    # def questions( self ):
    #     """Returns canvasapi questions for the activity"""
    #     print('getting qs')
    #     return self.course.get_quiz(self.activity.quiz_id).get_questions()

    def _fix_forgot_answers( self ):
        def r( v ):
            if v == 'They forgot to do this':
                return 'Forgot'
            return v

        for c in self.multiple_choice_names:
            self.data[ c ] = self.data.apply( lambda x: r( x[ c ] ), axis=1 )

    @property
    def essay_questions_names( self ):
        essay_questions = [ q.id for q in self.questions if q.question_type == 'essay_question' ]
        return [ c[ 1 ] for c in self.question_columns if int( c[ 0 ] ) in essay_questions ]

    @property
    def multiple_choice_names( self ):
        multiple_choice = [ q.id for q in self.questions if q.question_type == 'multiple_choice_question' ]
        return [ c[ 1 ] for c in self.question_columns if int( c[ 0 ] ) in multiple_choice ]

    @property
    def question_names( self ):
        return self.multiple_choice_names + self.essay_questions_names

    def get_formatted_work_by( self, student_id ):
        """Returns all entries by the indicated student, formatted for
        sending in a message or display"""

        def format_feedback( prompt, response ):
            return """
            ========
            Prompt: 
            {}
            
            Response: 
            {}
            =========
            """.format( prompt, response )

        # todo Add a check to make sure content is non empty. Raise an error if it is so other methods can decide what to do
        work = self.get_student_work( student_id )

        content = [ ]
        for c in self.question_names:
            content.append( format_feedback( c.split( ':' )[ 1 ], work[ c ] ) )

        content = "\n".join( content )
        return content


if __name__ == '__main__':
    pass
