"""
Created by adam on 2/23/20
"""
__author__ = 'adam'

from sqlalchemy import Column, Integer
from sqlalchemy.dialects.sqlite import DATETIME

from CanvasHacks import environment as env
# from sqlalchemy.ext.declarative import declarative_base
from CanvasHacks.DAOs.sqlite_dao import Base
from CanvasHacks.Models.model import Model
from CanvasHacks.TimeTools import current_utc_timestamp


class StatusRecord( Base, Model ):
    __tablename__ = env.STATUS_TABLE_NAME
    # The student whom this record concerns
    student_id = Column( Integer, primary_key=True, nullable=False )

    # The id of the content assignment
    content_assignment_id = Column( Integer, primary_key=True, nullable=False )

    # Id of student being reviewed by this student
    reviewer_of = Column( Integer, nullable=True )

    # Id of student reviewing this student
    reviewed_by = Column( Integer, nullable=True )

    # ------------------- Dates that this student did things
    # When this student submitted their content assignment
    content_assignment_submitted = Column( DATETIME, nullable=True )

    # When this student submitted their review of the reviewer_of student
    review_submitted = Column( DATETIME, nullable=True )

    # When this student turned in their review of the feedback given by
    # the reviewed_by student
    metareview_submitted = Column( DATETIME, nullable=True )

    # ------------------- Dates when this student was sent things
    # Date that the person who reviews this student was sent the
    # reviewer_of student's content assignment to review
    reviewer_assigned_on = Column( DATETIME, nullable=True )

    # If the student was sent a message that they must wait
    # until someone else submits the assignment before they can review
    # this is when that notificaion was sent
    wait_notification_on = Column( DATETIME, nullable=True )

    # When this student was sent the results of the metareview by
    # the reviewer_of student
    metareview_results_on = Column( DATETIME, nullable=True )

    # When this student was sent the feedback created by
    # the reviewed_by student
    review_results_on = Column( DATETIME, nullable=True )

    def is_under_review( self ):
        """Returns true if someone has been assigned to
        review this students' content assignment, false otherwise
        """
        return self.reviewed_by is not None

    def add_reviewee( self, reviewee, assigned_time=None ):
        """
        Sets the provided student as the person to be reviewed by
        the user whom the record belongs to.
        If assigned_time is set, it will use that as the reviewer_assigned_on value
        Otherwise will use current utc timestamp
        :param reviewee: Student object or id of student to be reviewed
        :param assigned_time:
        :return:
        """
        try:
            reviewee_id = reviewee.id
        except AttributeError:
            reviewee_id = reviewee

        if assigned_time is None:
            assigned_time = current_utc_timestamp()

        self.reviewer_assigned_on = assigned_time
        self.reviewer_of = reviewee_id

    def add_reviewer( self, reviewer ):
        """
        Sets the provided student as the person who is reviewing the
        the user whom the record belongs to.
        :param reviewer: Student object or id of student doing reviewing
        :return:
        """
        try:
            reviewer_id = reviewer.id
        except AttributeError:
            reviewer_id = reviewer

        self.reviewed_by = reviewer_id

    def record_content_assignment_submission( self, submitted_time=None ):
        """
        Called to record the timestamp of when this student submitted
        their content assignment
        :param submitted_time:
        :return:
        """
        if submitted_time is None:
            submitted_time = current_utc_timestamp()
        self.content_assignment_submitted = submitted_time

    def record_sending_metareview_results( self, sent_time=None ):
        """Called to record the feedback from the reviewer_of student being
        sent to this student"""
        if sent_time is None:
            sent_time = current_utc_timestamp()
        self.metareview_results_on = sent_time

    def record_sending_review_results( self, sent_time=None ):
        """Call to record that the student has been sent the content submitted
        by the reviewed_by student"""
        if sent_time is None:
            sent_time = current_utc_timestamp()
        self.review_results_on = sent_time

    def record_wait_notification( self, sent_time=None ):
        """Call to record that the student has been sent a notification that
        they will have to wait to receive student work for them to review"""
        if sent_time is None:
            sent_time = current_utc_timestamp()
        self.wait_notification_on = sent_time




if __name__ == '__main__':
    pass
