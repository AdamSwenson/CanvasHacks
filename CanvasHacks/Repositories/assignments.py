"""
Created by adam on 2/26/20
"""
__author__ = 'adam'

from CanvasHacks.Messaging.skaa import make_prompt_and_response
from CanvasHacks.Models.QuizModels import StoredDataFileMixin
from CanvasHacks.Models.student import Student
from CanvasHacks.Processors.cleaners import TextCleaner
from CanvasHacks.Repositories.interfaces import IContentRepository
from CanvasHacks.Repositories.mixins import SelectableMixin, StudentWorkMixin, FrameStorageMixin
from CanvasHacks.Repositories.submissions import AssignmentSubmissionRepository
from CanvasHacks.Text.stats import WordCount
from CanvasHacks.Widgets.AssignmentSelection import make_selection_button
import pandas as pd

if __name__ == '__main__':
    pass


class AssignmentRepository( IContentRepository, StoredDataFileMixin, StudentWorkMixin, SelectableMixin, FrameStorageMixin ):
    """Manages the data for a non-quiz type unit
    """

    def __init__( self, activity, course=None ):
        self.course = course
        self.activity = activity

        # An assignment will only come in with a 'body' attribute
        # to line this up with things that use questions (i.e., quizzes)
        self.body_column_name = AssignmentSubmissionRepository.body_column_name
        self.question_columns = [ self.body_column_name ]

        # The cleaner class that will be called to
        # remove html and other messy stuff from student
        # work
        self.text_cleaner = TextCleaner()

        self.analyzer = WordCount()


    def process( self, student_work_frame ):
        self.data = student_work_frame
        self._cleanup_data()

    def _cleanup_data( self ):
        """This is abstracted out so it can be
        called independently for use with test data
        """
        prev_len = len( self.data )
        # todo copy dataframe or run on original data?
        self.data = self.data[ self.data.grade != 'complete' ].copy( deep=True )
        # self.data = [j for j in self.data if j[0].grade != 'complete']
        print( "Removed {} rows which have already been graded".format( prev_len - len( self.data ) ) )

        # Remove html and other artifacts from student answers
        # DO NOT UNCOMMENT UNTIL CAN-59 HAS BEEN FULLY TESTED
        for c in self.question_columns:
            self.data[c] = self.data.apply(lambda x: self.text_cleaner.clean(x[c]), axis=1)


        # We set to student id to make look ups easier
        self.data.set_index( 'student_id', inplace=True )

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
        rs = [ { 'prompt': column_name, 'response': work[ column_name ] } for column_name in
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
        return self.assignment.points_possible / len( self.question_columns )

    @property
    def assignment( self ):
        """Returns the canvasapi.unit.Assignment object associated
        with this repository.
        Automatically initializes it if not set
        """
        try:
            if self._assignment:
                pass
        except AttributeError:
            self._assignment = self.course.get_assignment( self.activity.id )
        return self._assignment

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
        d = []
        for i, row in self.data.iterrows():
            s = {'student_id': i }
            for c in self.question_columns:
                s[c] = self.analyzer.analyze(row[c])
            d.append(s)
        return pd.DataFrame(d)
