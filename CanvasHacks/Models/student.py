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

from CanvasHacks.DAOs.sqlite_dao import Base


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


def get_first_name(user):
    """Given a canvas api user object representing a student
    returns the first name
    """
    return user.sortable_name.split(',')[1]


class StoredStudent( Base, StoreMixin ):
    """
    Storable model of student

    as of CAN-55


    """
    __tablename__ = env.STUDENT_TABLE_NAME
    # canvas id
    id = Column( Integer, primary_key=True )
    name = Column( String )
    short_name = Column(String)
    sortable_name = Column(String)
    csun_id = Column(Integer)
    email = Column(String)

    created_at = Column(String)
    integration_id = Column(String)
    login_id = Column(String)

    # def __init__( self, **kwargs ):
    #     self.handle_kwargs(**kwargs)
    #     self.student_id = int(student_id)
    #     # self.name = name
    #
    #     super().__init__( kwargs )

    def __eq__(self, other):
        return self.student_id == other.student_id

    @property
    def student_id( self ):
        """Guaranteed to be an integer since there
        are some cases of creation which may not
        have student_id set as an int
        """
        return int(self.id)

    @property
    def sis_user_id( self ):
        return self.csun_id

    @sis_user_id.setter
    def sis_user_id( self, sid ):
        self.csun_id = sid

    @property
    def canvas_id( self ):
        return self.id

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



class Student( StoreMixin ):
    """
    NON stored model

    Removed the association with Base
    but did not change the definition of properties
    so won't break anything

    """
    __tablename__ = env.STUDENT_TABLE_NAME
    # Not guaranteed to be an int unless loaded from db
    student_id = Column( Integer, primary_key=True )
    name = Column( String )
    short_name = Column(String)
    sis_user_id = Column(Integer)

    def __init__( self, **kwargs ):
        self.handle_kwargs(**kwargs)
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
