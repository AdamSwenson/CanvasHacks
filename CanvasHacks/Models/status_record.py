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

# Deprecated
class StatusRecord( Base, Model ):
    """
    :deprecated

    Keeps track of when an activity_inviting_to_complete was made available to a
    student and when they submitted it.

    NB, No need for recording when a rest_timeout notification is sent.
    That can go in the logs for auditing
    """
    __tablename__ = env.STATUS_TABLE_NAME

    # Id of the relevant activity_inviting_to_complete
    activity_id = Column(Integer, primary_key=True, nullable=False)

    # The student whom this record concerns
    student_id = Column( Integer, primary_key=True, nullable=False )

    # When this student submitted the activity_inviting_to_complete
    submitted = Column( DATETIME, nullable=True )

    # When the student was notified this was available
    # e.g., for metareview, this would be immediately after review submitted
    # by other party
    notified = Column( DATETIME, nullable=True )

    # When they were sent metareview feedback was sent out
    #
    # This is only relevant for the metareview since need to record when the
    # feedback from this student was sent out to the person who did the peer review.
    # Notified already represents when they were invited to do the metareview unit
    results = Column(DATETIME, nullable=True)

    def record_submission( self, time_to_record=None ):
        """
        Called to record the timestamp of when this student submitted
        their content unit
        :param time_to_record:
        :return:
        """
        if time_to_record is None:
            time_to_record = current_utc_timestamp()
        self.submitted = time_to_record

    def record_opened( self, time_to_record=None ):
        """
        Called to record the timestamp of when this student was
        notified that the activity_inviting_to_complete was available.
        With activities like peer review, this is also the
        time that they were sent someone else's work
        :param time_to_record:
        :return:
        """
        if time_to_record is None:
            time_to_record = current_utc_timestamp()
        self.notified = time_to_record

    def record_sent_results( self, time_to_record=None ):
        """
        Called to record the timestamp of when they were sent
        feedback on the unit
        :param time_to_record:
        :return:
        """

        if time_to_record is None:
            time_to_record = current_utc_timestamp()
        self.results = time_to_record



class FeedbackReceivedRecord( Base, Model ):
    """
    Keeps track of when a student was sent feedback from
    another student

    Created in CAN-53

    """
    __tablename__ = env.FEEDBACK_RECEIVED_STATUS_TABLE_NAME

    activity_id = Column(Integer, primary_key=True, nullable=False)
    """Id of the activity in which the feedback was created"""

    student_id = Column( Integer, primary_key=True, nullable=False )
    """ The student whom this record concerns """

    sent_at = Column(DATETIME, nullable=True)
    """ Timestamp of when the feedback was sent to them"""



class InvitationReceivedRecord( Base, Model ):
    """
    Keeps track of when a student was sent an invitation to
     provide feedback on another student

    Created in CAN-53

    """
    __tablename__ = env.INVITATION_RECEIVED_STATUS_TABLE_NAME

    # Id of the relevant activity_inviting_to_complete
    activity_id = Column(Integer, primary_key=True, nullable=False)
    """Id of the activity which we are inviting the student to complete"""

    # The student whom this record concerns
    student_id = Column( Integer, primary_key=True, nullable=False )
    """ The student whom this record concerns """

    sent_at = Column(DATETIME, nullable=True)
    """ Timestamp of when the feedback was sent to them"""












class ComplexStatusRecord( Base, Model ):
    __tablename__ = env.COMPLEX_STATUS_TABLE_NAME
    # The student whom this record concerns
    student_id = Column( Integer, primary_key=True, nullable=False )

    # The id of the content unit
    content_assignment_id = Column( Integer, primary_key=True, nullable=False )

    # Id of student being reviewed by this student
    reviewer_of = Column( Integer, nullable=True )

    # Id of student reviewing this student
    reviewed_by = Column( Integer, nullable=True )

    # ------------------- Dates that this student did things
    # When this student submitted their content unit
    content_assignment_submitted = Column( DATETIME, nullable=True )

    # When this student submitted their review of the reviewer_of student
    review_submitted = Column( DATETIME, nullable=True )

    # When this student turned in their review of the feedback given by
    # the reviewed_by student
    metareview_submitted = Column( DATETIME, nullable=True )

    # ------------------- Dates when this student was sent things
    # Date that the person who reviews this student was sent the
    # reviewer_of student's content unit to review
    reviewer_assigned_on = Column( DATETIME, nullable=True )

    # If the student was sent a message that they must rest_timeout
    # until someone else submits the unit before they can review
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
        review this students' content unit, false otherwise
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
        their content unit
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
        they will have to rest_timeout to receive student work for them to review"""
        if sent_time is None:
            sent_time = current_utc_timestamp()
        self.wait_notification_on = sent_time


if __name__ == '__main__':
    pass
