"""
Created by adam on 3/22/20
"""
__author__ = 'adam'

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Models.submission_record import SubmissionRecord
from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.Repositories.interfaces import IRepo
from CanvasHacks.Repositories.mixins import StudentWorkMixin
from CanvasHacks.TimeTools import current_utc_timestamp

if __name__ == '__main__':
    pass


class SubmissionRecordRepository( StudentWorkMixin, IRepo ):
    
    def __init__( self, dao: SqliteDAO, activity: Activity ):
        """
        Create a repository to handle events for a
        particular activity_inviting_to_complete
        """
        self.activity = activity
        self.session = dao.session

    def get( self, student ):
        """
        Returns the record for the student for this activity or none
        if no record has been created yet
        :param student: Student or student id
        :return: SubmissionRecord or None
        """
        student_id = self._handle_id( student )
        return self.session.query( SubmissionRecord )\
            .filter( SubmissionRecord.activity_id == self.activity.id )\
            .filter( SubmissionRecord.student_id == student_id )\
            .one_or_none()

    def has_submitted( self, student ):
        """
        Returns true if the student has submitted the activity 
        :param student: Student or student id
        :return:
        """
        record = self.get( student )
        return record is not None

    def submitted_at( self, student ):
        """Returns the timestamp of when the
        student submitted the activity or None if they haven't
        """
        rec = self.get( student )
        if rec is not None:
            return rec.sent_at
        return None

    @property
    def previously_submitted( self ):
        """
        Returns SubmissionRecord for all students
        who have been invited to complete the activity
        :return: list
        """
        return self.session\
            .query( SubmissionRecord )\
            .filter( SubmissionRecord.activity_id == self.activity.id )\
            .all()

    @property
    def previously_submitted_ids( self ):
        """Returns a list of ids of students who have
        already submitted
        """
        recs = self.previously_submitted
        if len( recs ) == 0:
            return recs
        return [ r.student_id for r in recs ]

    def record( self, student, time_to_record=None ):
        """
        Records that a student has submitted  an activity

        # todo Consider bulk commits if slow

        :param student: Student or student id
        :param time_to_record: If none, we will record the current utc time
        :return: SubmissionRecord
        """
        student_id = self._handle_id( student )
        if time_to_record is None:
            time_to_record = current_utc_timestamp()

        rec = SubmissionRecord( student_id=student_id,
                                activity_id=self.activity.id,
                                submitted_at=time_to_record )

        self.session.add( rec )
        self.session.commit()
        return rec
