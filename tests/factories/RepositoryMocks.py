"""
Created by adam on 2/22/20
"""
__author__ = 'adam'

from CanvasHacks.Repositories.students import StudentRepository
from CanvasHacks.Repositories.IRepositories import ContentRepository
from CanvasHacks.Models.model import StoreMixin
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


class ContentRepositoryMock(ContentRepository, StoreMixin):

    def __init__( self, **kwargs ):
        self.handle_kwargs(**kwargs)

    def get_formatted_work_by( self, student_id ):
        return self.formatted_work

