"""
Created by adam on 2/23/20
"""
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Models.status_record import StatusRecord
from CanvasHacks.PeerReviewed.Definitions import Unit

__author__ = 'adam'

if __name__ == '__main__':
    pass


class StatusRepository:

    def __init__( self, dao: SqliteDAO, unit: Unit):
        """
        Create a repository to handle review assignments for a
        particular activity
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
        return self.session.query( StatusRecord ) \
            .filter( StatusRecord.content_assignment_id == self.content_assignment_id ) \
            .all()

    def get_student_record( self, student_or_id ):
        """
        Returns the record for the student for this assignment or none
        if no record has been created yet
        :param student_or_id:
        :return:
        """
        student_id = self._handle_id(student_or_id)
        return self.session.query( StatusRecord ) \
            .filter( StatusRecord.content_assignment_id == self.content_assignment_id ) \
            .filter(StatusRecord.student_id == student_id)\
            .one_or_none()

    def create_record( self, student_or_id ):
        student_id = self._handle_id(student_or_id)
        reviewer_rec = StatusRecord(student_id=student_id, content_assignment_id=self.content_assignment_id )
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

