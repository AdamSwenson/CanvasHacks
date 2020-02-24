"""
Created by adam on 2/23/20
"""
__author__ = 'adam'


from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

from CanvasHacks import environment as env
from CanvasHacks.Models.model import Model
from CanvasHacks.Models.student import Student

Base = declarative_base()


class StatusRecord( Base, Model ):
    __tablename__ = env.REVIEW_ASSOCIATIONS_TABLE_NAME
    id = Column( Integer, primary_key=True )
    activity_id = Column( Integer )
    assessor_id = Column( Integer )
    assessee_id = Column( Integer )


if __name__ == '__main__':
    pass