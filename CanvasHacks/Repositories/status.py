"""
Created by adam on 2/23/20
"""
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Models.status_record import ComplexStatusRecord, StatusRecord
from CanvasHacks.PeerReviewed.Definitions import Unit, Activity
from CanvasHacks.Repositories.interfaces import IRepo

__author__ = 'adam'

from CanvasHacks.Repositories.mixins import StudentWorkMixin

if __name__ == '__main__':
    pass


class StatusRepository(StudentWorkMixin, IRepo):

    def __init__( self, dao: SqliteDAO, activity: Activity):
        """
        Create a repository to handle events for a
        particular activity_inviting_to_complete
        """
        self.activity = activity
        self.session = dao.session

    def create_record( self, student_or_id ):
        """Creates and returns a record for the student on the activity_inviting_to_complete.
        It does not set the submitted or notified values
        """
        student_id = self._handle_id(student_or_id)
        rec = StatusRecord( student_id=student_id, activity_id=self.activity.id )
        self.session.add( rec )
        # todo Consider bulk commits if slow
        self.session.commit()
        return rec

    @property
    def previously_notified_students( self ):
        """Returns a list of ids of students who have
        already been notified
        """
        records = self.session.query( StatusRecord ) \
            .filter( StatusRecord.activity_id == self.activity.id ) \
            .filter( StatusRecord.notified.isnot(None)  ) \
            .all()
        return [r.student_id for r in records]
        # record = self.get_record(student_or_id)
        # if record is not None:
        #     # this will be true if notified is a datetime
        #     return record.notified is not None
        # # If the record hasn't been created yet, it will
        # # return false. That way this check can be run before
        # # the process that creates the records
        # return False

    @property
    def previously_sent_results( self ):
        """Returns a list of ids of students who have
        already been notified
        """
        records = self.session.query( StatusRecord ) \
            .filter( StatusRecord.activity_id == self.activity.id ) \
            .filter( StatusRecord.results.isnot(None)  ) \
            .all()
        return [r.student_id for r in records]

    def get_record( self, student_or_id ):
        """
        Returns the record for the student for this assignment or none
        if no record has been created yet
        :param student_or_id:
        :return:
        """
        student_id = self._handle_id(student_or_id)
        return self.session.query( StatusRecord )\
            .filter( StatusRecord.activity_id == self.activity.id ) \
            .filter( StatusRecord.student_id == student_id ) \
            .one_or_none()

    def get_or_create_record( self, student_or_id ):
        """Keeping the 2 required methods separate in
        case have some use to do them separately
        """
        record = self.get_record(student_or_id)
        if record is None:
            record = self.create_record(student_or_id)
        return record

    def record( self, student, time_to_record=None ):
        """
        Generic version which will normally record via
        record_opened. However, can be overriden by other
        repos
        :param student:
        :param time_to_record:
        :return:
        """
        self.record_opened(student, time_to_record)

    def record_opened( self, student, time_to_record=None ):
        """Record that the student was notified that the activity_inviting_to_complete
         is available
        """
        print("record_opened", student)
        record = self.get_or_create_record(student)
        record.record_opened( time_to_record )
        self.session.commit()

    def record_submitted( self, student, time_to_record=None):
        """Record that the student has submitted
        the activity_inviting_to_complete
        """
        record = self.get_or_create_record(student)
        record.record_submission(time_to_record)
        self.session.commit()

    def record_sent_results( self, student, time_to_record=None ):
        """Records when feedback from this student was sent out

        This is only relevant for the metareview since need to record when the
        feedback from this student was sent out to the person who did the peer review.
        NB, notified already represents when they were
        invited to do the metareview assignment, the results of which we are now sending
        """
        print('record_sent', student)
        record = self.get_or_create_record(student)
        record.record_sent_results(time_to_record)
        self.session.commit()


class MetareviewResultsStatusRepository(StatusRepository):
    def __init__( self, dao: SqliteDAO, activity: Activity):
        """
        Create a repository to handle events for a
        particular activity_inviting_to_complete
        """
        self.activity = activity
        self.session = dao.session

    def record( self, student, time_to_record=None ):
        self.record_sent_results(student, time_to_record)



class ComplexStatusRepository:
    """This likely won't be used. Keeping it until done simplifying"""

    def __init__( self, dao: SqliteDAO, unit: Unit):
        """
        Create a repository to handle review assignments for a
        particular activity_inviting_to_complete
        """
        self.content_assignment_id = unit.initial_work.id
        self.session = dao.session

    def _handle_id( self, student_or_int ):
        """
        Takes either a student object or the int value of their id
        and returns the id
        :param student_or_int:
        :return: int
        """
        try:
            student_id = int(student_or_int)
        except TypeError:
            student_id = student_or_int.id
        return student_id

    def load( self ):
        """
        Populates self.data with all existing records for the unit
        :return:
        """
        self.data = self.get_unit_records()

    def get_unit_records( self):
        """
        Returns all existing records for the unit
        :return: list of StatusReord objects
        """
        return self.session.query( ComplexStatusRecord ) \
            .filter( ComplexStatusRecord.content_assignment_id == self.content_assignment_id ) \
            .all()

    def get_student_record( self, student_or_id ):
        """
        Returns the record for the student for this assignment or none
        if no record has been created yet
        :param student_or_id:
        :return:
        """
        student_id = self._handle_id(student_or_id)
        return self.session.query( ComplexStatusRecord ) \
            .filter( ComplexStatusRecord.content_assignment_id == self.content_assignment_id ) \
            .filter( ComplexStatusRecord.student_id == student_id )\
            .one_or_none()

    def create_record( self, student_or_id ):
        student_id = self._handle_id(student_or_id)
        reviewer_rec = ComplexStatusRecord( student_id=student_id, content_assignment_id=self.content_assignment_id )
        self.session.add( reviewer_rec )
        # commit here?
        return reviewer_rec

    def record_review_assignments( self, list_of_tuples ):
        """
        Expects a list of ( reviewer student, reviewee student) tuples
        :param list_of_tuples:
        :return:
        """
        for reviewer, reviewee in list_of_tuples:
            reviewer_rec = self.get_student_record( reviewer )
            # Get the student. If no record exists, create it
            if reviewer_rec is None:
                reviewer_rec = self.create_record(reviewer)

            # Make sure that a record exists for the reviewee
            reviewee_rec = self.get_student_record( reviewee )
            if reviewee_rec is None:
                reviewer_rec = self.create_record(reviewee)

            reviewer_rec.add_reviewee(reviewee)

        # also store reviewor here?

        # todo commit here or wait for successful notification?
        self.session.commit()

    def record_peer_review_results_sent( self, list_of_students ):
        """
        For each of the students (id or object), records that the initial
        assignment has been sent to the reviewer
        :param list_of_students:
        :return:
        """
        for s in list_of_students:
            record = self.get_student_record( s )
            record.record_sending_review_results()

        self.session.commit()

    def record_metareview_results_sent( self, list_of_students ):
        """
        For each of the students (id or object), records that the results of
        the metareview has been sent to the reviewer
        :param list_of_students:
        :return:
        """
        for s in list_of_students:
            record = self.get_student_record( s )
            record.record_sending_metareview_results()

        self.session.commit()

