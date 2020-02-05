"""
Created by adam on 12/20/19
"""
__author__ = 'adam'
from canvasapi.user import User
from CanvasHacks.Models.model import Model

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from CanvasHacks import environment as env
from CanvasHacks.Models.model import Model, StoreMixin

Base = declarative_base()

#
# def get_student_id(student_like_thing):
#     """In some contexts poor programming means that there could
#     be either the student id (int), a canvas User, or a Student model"""

def ensure_student(v):
    """
    For functions/methods which require a student object
    but may have received either the object or just the id
    this checks what was passed and returns a student object.
    NB, the object may be new and not stored in db
    :param v:
    :return: Student
    """
    if isinstance(v, Student): return v

    if isinstance(v, User):
        return student_from_canvas_user(v)

    s = Student()
    try:
        # integer and string integer input cases
        s.student_id = int(v)
    except (ValueError, TypeError):
        # dict and object cases
        if not isinstance(v, dict):
            # object case
            v = v.__dict__
        s.handle_kwargs(**v)
    return s


def student_from_canvas_user(user_obj):
    """Makes a student object from a canvas User"""
    s = Student()
    s.student_id = user_obj.id
    # The id will cause a collision with the student.id
    vals = { k : user_obj.attributes[k] for k in user_obj.attributes if k != 'id'}
    s.handle_kwargs(**vals)
    return s


class Student( Base, StoreMixin ):
    """
    Storable model of student
    """
    __tablename__ = env.STUDENT_TABLE_NAME
    # Not guaranteed to be an int unless loaded from db
    student_id = Column( Integer, primary_key=True )
    name = Column( String )
    short_name = Column(String)
    sis_user_id = Column(Integer)

    # def __init__( self, student_id=None, **kwargs ):
    #     self.student_id = int(student_id)
    #     # self.name = name
    #
    #     super().__init__( kwargs )

    def __eq__(self, other):
        return self.student_id == other.student_id

    @property
    def id( self ):
        """Guaranteed to be an integer since there
        are some cases of creation which may not
        have student_id set as an int
        """
        return int(self.student_id)

    @property
    def first_name( self ):
        """Returns first name"""
        # if self.short_name is not None:
        # this is always the same as name it seems...
        #     return self.short_name
        if ',' in self.name:
            return self.name.split(',')[1]
        else:
            return self.name.split(' ')[1]

if __name__ == '__main__':
    pass
