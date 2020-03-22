"""
Created by adam on 5/6/19
"""
from CanvasHacks.Models.QuizModels import StoredDataFileMixin, QuizDataMixin
from CanvasHacks.Models.student import Student
from CanvasHacks.Definitions.skaa import Review
from CanvasHacks.Processors.cleaners import TextCleaner
from CanvasHacks.Processors.quiz import process_work, remove_non_final_attempts
from CanvasHacks.Files.QuizReportFileTools import retrieve_quiz_data, save_downloaded_report
from CanvasHacks.Repositories.mixins import StudentWorkMixin, SelectableMixin, FrameStorageMixin
from CanvasHacks.Repositories.submissions import QuizSubmissionRepository
from CanvasHacks.Text.stats import WordCount
from CanvasHacks.Widgets.AssignmentSelection import make_selection_button

__author__ = 'adam'

import pandas as pd

from CanvasHacks.Messaging.skaa import make_prompt_and_response
from CanvasHacks.Repositories.interfaces import IContentRepository


# def detect_question_columns(columns):
#     """Return a list of columns which contain a colon,
#     those probably contain the question answers
#     """
#     return [c for c in columns if len(c.split(':')) > 1]


# test = [ 'submitted', 'attempt',"1785114: \nWhat is an example of persuasive advertising?", '1.0']
# assert(detect_question_columns(test) == [ "1785114: \nWhat is an example of persuasive advertising?"])
# Limit to just the final attempts


#     return frame[pd.notnull(frame['submission_id'])]


#     to_drop = [ ]
#     for d in droppable:
#         for c in columns:
#             if c[ :len( d ) ] == d:
#                 to_drop.append( c )
#     return to_drop


# test = [ 'name', 'id', 'sis_id', '1.0', '1.0.1', '1.0.2' ]
# assert (make_drop_list( test ) == [ '1.0', '1.0.1', '1.0.2' ])


class QuizRepository( IContentRepository, QuizDataMixin, StoredDataFileMixin, StudentWorkMixin, SelectableMixin, FrameStorageMixin ):
    """Manages the data for a quiz type unit"""

    def __init__( self, activity, course=None ):
        self.course = course
        self.activity = activity
        self.question_columns = [ ]

        # The cleaner class that will be called to
        # remove html and other messy stuff from student
        # work
        self.text_cleaner = TextCleaner()

        self.analyzer = WordCount()

    def process( self, work_frame, submissions ):
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

    def _cleanup_data( self ):
        """
        Runs cleanup operations specific to this kind of data
        """
        # the name will be set as index from sorting
        # so we set to student id to make look ups easier
        self.data.set_index( 'student_id', inplace=True )
        # Remove unneeded columns
        # self.data = self.data[self.activity_inviting_to_complete.question_columns]

        # Remove html and other artifacts from student answers
        # DO NOT UNCOMMENT UNTIL CAN-59 HAS BEEN FULLY TESTED
        for c in self.question_columns:
            self.data[c] = self.data.apply(lambda x: self.text_cleaner.clean(x[c]), axis=1)


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

    @property
    def submitter_ids( self ):
        """Returns a list of canvas ids of students who have submitted the unit"""
        # try:
        return list( set( self.data.reset_index().student_id.tolist() ) )
        # except (ValueError, KeyError):


    def word_counts( self ):
        """
        Returns a dataframe with columns student_id, and all
        question columns. Question columns contain word counts
        :return:
        """
        d = []
        for i, row in self.data.iterrows():
            s = {'student_id': i }
            for c in self.question_columns:
                s[c] = self.analyzer.analyze(row[c])
            d.append(s)
        return pd.DataFrame(d)


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
    #     def __init__( self, activity_inviting_to_complete ):
    #         self.activity_inviting_to_complete = activity_inviting_to_complete
    #     self.question_columns = []

    # @property
    # def questions( self ):
    #     """Returns canvasapi questions for the activity_inviting_to_complete"""
    #     print('getting qs')
    #     return self.course.get_quiz(self.activity_inviting_to_complete.quiz_id).get_questions()

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


def make_quiz_repo( course, activity, save=True ):
    """Gets all student work data for the activity_inviting_to_complete that's part of the unit
    loads it into a QuizRepository or ReviewRepository and
    returns the repository.
    This is the main method called to get data
    """
    # Get quiz submission objects
    # repo = WorkRepositoryFactory.make( activity_inviting_to_complete, course )
    if isinstance(activity, Review):
        repo = ReviewRepository(activity, course)
    else:
        repo = QuizRepository(activity, course)

    # Download student work
    # This will work if the 'Create Report' button has been manually clicked
    student_work_frame = retrieve_quiz_data( repo.quiz )

    if save:
        # Want to have all the reports be formatted the same
        # regardless of whether we manually or programmatically
        # downloaded them. Thus we save before doing anything to them.
        save_downloaded_report( activity, student_work_frame )

    # Download submissions
    subRepo = QuizSubmissionRepository( repo.quiz )

    # Doing the combination with submissions after saving to avoid
    # mismatches of new and old data
    repo.process( student_work_frame, subRepo.frame )

    return repo