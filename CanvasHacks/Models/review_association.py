"""
Created by adam on 1/18/20
"""
__author__ = 'adam'

from sqlalchemy import Column, Integer
# from sqlalchemy.ext.declarative import declarative_base

from CanvasHacks import environment as env
from CanvasHacks.Models.model import Model
from CanvasHacks.Models.student import Student

from CanvasHacks.DAOs.sqlite_dao import Base
# Base = declarative_base()


class ReviewAssociation( Base, Model ):
    __tablename__ = env.REVIEW_ASSOCIATIONS_TABLE_NAME
    id = Column( Integer, primary_key=True )
    activity_id = Column( Integer )
    assessor_id = Column( Integer )
    assessee_id = Column( Integer )

    def __repr__( self ):
        return "<ReviewAssociation(id={}, activity_id={}, assessor_id={}, assessee_id={}".format(self.id, self.activity_id, self.assessor_id, self.assessee_id)

    @property
    def is_self_assignment( self ):
        """This will be an invalid unit
        but we will leave it up to something checking this property
        to raise an error or determine what to do"""
        return self.assessee_id == self.assessor_id

    # @property
    # def assessee( self ):
    #     return Student(self.assessee_id)
    #
    # @property
    # def assessor( self ):
    #     return Student(self.assessor_id)



if __name__ == '__main__':
    pass
