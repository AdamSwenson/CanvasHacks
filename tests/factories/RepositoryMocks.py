"""
Created by adam on 2/22/20
"""
__author__ = 'adam'

import pandas as pd
from faker import Faker

from CanvasHacks.Models.model import StoreMixin
from CanvasHacks.Repositories.interfaces import IContentRepository
from CanvasHacks.Repositories.students import StudentRepository
from factories.PeerReviewedFactories import content_repo_data_object_factory

fake = Faker()

if __name__ == '__main__':
    pass


class StudentRepositoryMock( StudentRepository, StoreMixin ):

    def __init__( self, **kwargs ):
        self.handle_kwargs( **kwargs )

    def get_student( self, canvas_id ):
        return self.student

    def get_student_name( self, canvas_id ):
        return self.student_name


class ContentRepositoryMock( IContentRepository, StoreMixin ):
    """Mainly used to avoid creating whole dataframes
    for testing
    """

    def __init__( self, **kwargs ):
        self.handle_kwargs( **kwargs )
        self.data = [ ]

    def get_formatted_work_by( self, student_id ):
        return self.testText.get( student_id )
        # return [a[1] for a in self.testText if a[0] == student_id][0]

    def create_test_content( self, student_ids ):
        """Creates a dictionary with a content / body entry as the value
        for each id passed in and stores it on testText"""
        self.testText = { sid: fake.paragraph() for sid in student_ids }

    # @property
    # def submitter_ids( self ):
    #     return [k for k in self.testText.keys()]

    def remove_student_records( self, student_ids ):
        self.testText = { k: self.testText[ k ] for k in self.testText.keys() if k not in student_ids }

    def add_students_to_data( self, student_ids, make_dataframe=False, **kwargs ):
        """Populates self.data with records of the expected type"""
        for s in student_ids:
            d = content_repo_data_object_factory( student_id=s, **kwargs )
            d[ 'body' ] = self.testText.get( s )
            self.data.append( d )
        if make_dataframe:
            self.data = pd.DataFrame( self.data )

    def create_quiz_repo_data( self, student_ids, submitted_at, make_dataframe=False, num_question_columns=5, **kwargs ):
        """Simulates being a content repo holding quiz data
        """
        self.question_columns = [ (fake.random.randint(1, 99999999), fake.word()) for _ in range( 0, num_question_columns ) ]
        fixed_fields = [ 'course_id', 'quiz_id']
        variable_fields = ['attempt', 'submission_id']

        course_id = kwargs['course_id'] if 'course_id' in kwargs else fake.random.randint(1, 999999)

        quiz_id = kwargs[ 'quiz_id' ] if 'quiz_id' in kwargs else fake.random.randint( 1, 999999 )

        for sid in student_ids:
            d = {
                'student_id': sid,
                'submitted_at': submitted_at,
                # some things look for this still
                'submitted': submitted_at,
                'course_id': course_id,
                'quiz_id': quiz_id
            }
            for f in variable_fields:
                if f in kwargs.keys():
                    d[f] = kwargs[f]
                else:
                    d[f] = fake.random.randint(11111, 9999999)

            for qid, column_name in self.question_columns:
                d[  column_name ] = fake.paragraph()

            self.data.append( d )

        if make_dataframe:
            self.data = pd.DataFrame(self.data)
