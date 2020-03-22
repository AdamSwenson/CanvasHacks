"""
Created by adam on 3/22/20
"""
__author__ = 'adam'

from sqlalchemy import Column, Integer
from sqlalchemy.dialects.sqlite import DATETIME

from CanvasHacks import environment as env
# from sqlalchemy.ext.declarative import declarative_base
from CanvasHacks.DAOs.sqlite_dao import Base
from CanvasHacks.Models.model import Model
from CanvasHacks.TimeTools import current_utc_timestamp

if __name__ == '__main__':
    pass


class SubmissionRecord( Base, Model ):
    """
    Record of a student completing an assignment.
    The first time the student completed the assignment.

    Created in CAN-61

    """
    __tablename__ = env.SUBMISSION_TABLE_NAME

    activity_id = Column(Integer, primary_key=True, nullable=False)
    """Id of the activity in which the feedback was created"""

    student_id = Column( Integer, primary_key=True, nullable=False )
    """ The student whom this record concerns """

    submitted_at = Column(DATETIME, nullable=True)
    """ Timestamp of when the feedback was sent to them"""
