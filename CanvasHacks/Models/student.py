"""
Created by adam on 12/20/19
"""
__author__ = 'adam'

from CanvasHacks.Models.model import Model


class Student( Model ):

    def __init__( self, student_id=None, **kwargs ):
        self.student_id = student_id
        # self.name = name

        super().__init__( kwargs )

    def __eq__(self, other):
        return self.student_id == other.student_id

    @property
    def id( self ):
        return self.student_id

if __name__ == '__main__':
    pass
