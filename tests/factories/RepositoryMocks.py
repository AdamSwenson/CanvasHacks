"""
Created by adam on 2/22/20
"""
__author__ = 'adam'

from CanvasHacks.Repositories.students import StudentRepository
from CanvasHacks.Repositories.interfaces import IContentRepository
from CanvasHacks.Models.model import StoreMixin
from faker import Faker
fake = Faker()

if __name__ == '__main__':
    pass

from unittest.mock import MagicMock

class StudentRepositoryMock(StudentRepository, StoreMixin):

    def __init__( self, **kwargs ):
        self.handle_kwargs(**kwargs)

    def get_student( self, canvas_id ):
        return self.student

    def get_student_name( self, canvas_id ):
        return self.student_name


class ContentRepositoryMock( IContentRepository, StoreMixin ):

    def __init__( self, **kwargs ):
        self.handle_kwargs(**kwargs)

    def get_formatted_work_by( self, student_id ):
        return self.testText.get(student_id)
        # return [a[1] for a in self.testText if a[0] == student_id][0]

    def create_test_content( self, student_ids ):
        self.testText = { sid : fake.paragraph() for sid in student_ids}

    def remove_student_records( self, student_ids ):
        pass