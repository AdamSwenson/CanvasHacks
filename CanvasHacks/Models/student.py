"""
Created by adam on 12/20/19
"""
__author__ = 'adam'

from CanvasHacks.Models.model import Model

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from CanvasHacks import environment as env
from CanvasHacks.Models.model import Model

Base = declarative_base()

def ensure_student(v):
    """
    For functions/methods which require a student object
    but may have received either the object or just the id
    this checks what was passed and returns a student object
    :param v:
    :return:
    """
    if isinstance(v, Student): return v

    return Student(v)


class Student( Base, Model ):
    __tablename__ = env.STUDENT_TABLE_NAME
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
        return self.student_id

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
