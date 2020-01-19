"""
Created by adam on 1/18/20
"""
__author__ = 'adam'

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

from CanvasHacks import environment as env
from CanvasHacks.Models.model import Model
from CanvasHacks.Models.student import Student

Base = declarative_base()


class ReviewAssociation( Base, Model ):
    __tablename__ = env.REVIEW_ASSOCIATIONS_TABLE_NAME
    id = Column( Integer, primary_key=True )
    activity_id = Column( Integer )
    assessor_id = Column( Integer )
    assessee_id = Column( Integer )

    # def __init__(self, activity, assessor, assessee):
    #     self.activity = activity
    #     self.assessor = assessor
    #     self.assessee = assessee
    def __repr__( self ):
        return "<ReviewAssociation(activity_id={}, assessor_id={}, assessee_id={}".format(self.activity_id, self.assessor_id, self.assessee_id)
        # "<User(name='%s', fullname='%s', nickname='%s')>" % (
        # ...                             self.name, self.fullname, self.nickname)

    @property
    def assessee( self ):
        return Student(self.assessee_id)

    @property
    def assessor( self ):
        return Student(self.assessor_id)



if __name__ == '__main__':
    pass
