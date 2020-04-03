"""
Created by adam on 2/23/20
"""
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Models.review_association import ReviewAssociation
from CanvasHacks.Models.status_record import ComplexStatusRecord, FeedbackReceivedRecord, InvitationReceivedRecord,\
    StatusRecord
from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.Definitions.unit import Unit
from CanvasHacks.Repositories.interfaces import IRepo

__author__ = 'adam'

from CanvasHacks.Repositories.mixins import StudentWorkMixin
from CanvasHacks.TimeTools import current_utc_timestamp

if __name__ == '__main__':
    pass


class IStatusRepository( StudentWorkMixin, IRepo ):

    def record( self, student, time_to_record=None ):
        """
        Main method called.
        The invitiation repo will record when the student was
        invited to do a review.
        The version which will normally record via
        record_invited. However, can be overriden by other
        repos
        :param student:
        :param time_to_record:
        :return:
        """
        raise NotImplementedError

    def has_received( self, student_id ):
        raise NotImplementedError

    @property
    def previously_received( self ):
        """
        Returns the correct kind of status record for all students
        who have been sent the thing
        :return: list
        """
        raise NotImplementedError

    def get( self, student ):
        """
        Returns the status record for the student or none
        :param student:
        :return:
        """
        raise NotImplementedError


class InvitationStatusRepository( IStatusRepository ):
    """
    This repository handles records of when a student
    was invited to do a particular activity.

    InitialWork: Not called

    Review: Invite sent is recorded on the reviewer once they are sent the content
     of an author's initial work assignment.

    Metareview: Invite sent is recorded on the author once they are sent the feedback
    created in the Review assignment.

    """

    def __init__( self, dao: SqliteDAO, activity: Activity ):
        """
        Create a repository to handle events for a
        particular activity_inviting_to_complete
        """
        self.activity = activity
        self.session = dao.session

    def get( self, student ):
        """
        Returns the record for the student for this unit or none
        if no record has been created yet
        :param student: Student or student id
        :return: FeedbackReceivedRecord or None
        """
        student_id = self._handle_id( student )
        return self.session.query( InvitationReceivedRecord )\
            .filter( InvitationReceivedRecord.activity_id == self.activity.id )\
            .filter( InvitationReceivedRecord.student_id == student_id )\
            .one_or_none()

    def has_received( self, student ):
        """
        Returns true if the student has been invited to
        complete the assignment
        :param student: Student or student id
        :return:
        """
        record = self.get( student )
        return record is not None

    def received_at( self, student ):
        """Returns the timestamp of when the
        student was invited or None if they haven't been
        """
        rec = self.get( student )
        if rec is not None:
            return rec.sent_at
        return None

    @property
    def previously_received( self ):
        """
        Returns InvitationReceivedRecord for all students
        who have been invited to complete the activity
        :return: list
        """
        return self.session\
            .query( InvitationReceivedRecord )\
            .filter( InvitationReceivedRecord.activity_id == self.activity.id )\
            .all()

    @property
    def previously_received_ids( self ):
        """Returns a list of ids of students who have
        already received invitation
        """
        recs = self.previously_received
        if len( recs ) == 0:
            return recs
        return [ r.student_id for r in recs ]

    def record( self, student, time_to_record=None ):
        """
        Records that a student has been invited to
        complete an activity

        # todo Consider bulk commits if slow

        :param student: Student or student id
        :param time_to_record:
        :return:
        """
        student_id = self._handle_id( student )
        if time_to_record is None:
            time_to_record = current_utc_timestamp()

        rec = InvitationReceivedRecord( student_id=student_id, activity_id=self.activity.id, sent_at=time_to_record )

        self.session.add( rec )
        self.session.commit()
        return rec


class FeedbackStatusRepository( IStatusRepository ):
    """
    Handles records of when a student received feedback
    on their work in the activity.

    InitialWork: Feedback sent is recorded once the reviewer turns in the
    review assignment and the feedback is sent to the author of the initial work

    Review: Feedback sent is recorded once the author turns in the metareview assignment
    and the feedback is sent to the person who peer reviewed the initial work

    Metareview: Not called.

    """

    def __init__( self, dao: SqliteDAO, activity: Activity, review_pairings_activity=None ):
        """
         Create a repository to handle events for a
        particular activity

        :param dao:
        :param activity: The activity feedback is sent on
        :param review_pairings_activity: Activity which the review associations are based upon
        """
        self.activity = activity
        self.session = dao.session

        # if None, that means there's no difference between the activities
        # so we can just use the activity
        self.review_pairings_activity = review_pairings_activity if review_pairings_activity is not None else self.activity

    def get( self, student ):
        """
        Returns the record for the student for this activity or none
        if no record has been created yet
        :param student: Student or student id
        :return: FeedbackReceivedRecord or None
        """
        student_id = self._handle_id( student )
        return self.session\
            .query( FeedbackReceivedRecord )\
            .filter( FeedbackReceivedRecord.activity_id == self.activity.id )\
            .filter( FeedbackReceivedRecord.student_id == student_id )\
            .one_or_none()

    def has_received( self, student ):
        """
        Returns true if the student has been sent feedback on
        the assignment
        :param student: Student or student id
        :return:
        """
        record = self.get( student )
        return record is not None

    @property
    def previously_received( self ):
        """
        Returns FeedbackReceivedRecord for all students
        associated with the activity
        :return: list
        """
        return self.session.query( FeedbackReceivedRecord ).filter(
            FeedbackReceivedRecord.activity_id == self.activity.id ).all()

    @property
    def previously_received_ids( self ):
        """Returns a list of ids of students who have
        already received feedback from another student
        """
        recs = self.previously_received
        if len( recs ) == 0:
            return recs
        return [ r.student_id for r in recs ]

    def record( self, student, time_to_record=None ):
        """
        Creates a record that the student was sent
        feedback.
        NB, student id and activity are primary keys so trying to create
        a new record if one already exists should raise an error

        # todo Consider bulk commits if slow

        :param student: Student object or student id
        :param time_to_record:
        :return: FeedbackReceivedRecord
        """
        student_id = self._handle_id( student )
        if time_to_record is None:
            time_to_record = current_utc_timestamp()

        rec = FeedbackReceivedRecord( student_id=student_id, activity_id=self.activity.id, sent_at=time_to_record )

        self.session.add( rec )
        self.session.commit()

        return rec

    def received_at( self, student ):
        """
        Returns the timestamp of when the student was notified or
        None if they haven't been
        :param student:
        :return:
        """
        rec = self.get( student )
        if rec is not None:
            return rec.sent_at
        return None

    @property
    def reviewers_with_authors_sent_feedback( self ):
        """
        Returns the ids of reviewers who have already had their feedback
        sent to the authors
        Used to filter for sending peer review results to authors
        :return:
        """
        notified = self.session\
            .query( ReviewAssociation )\
            .outerjoin( FeedbackReceivedRecord, FeedbackReceivedRecord.student_id == ReviewAssociation.assessee_id )\
            .filter( ReviewAssociation.activity_id == self.review_pairings_activity.id )\
            .filter( FeedbackReceivedRecord.activity_id == self.activity.id )\
            .filter( FeedbackReceivedRecord.student_id.isnot( None ) )\
            .all()
        # ids of reviewers whose authors have been notified
        notified = [ n.assessor_id for n in notified ]
        return notified

    def remove_reviewers_with_notified_authors( self, reviewers ):
        """
        Given a list of reviewers, checks whether the author
        for each reviewer has received their feedback
        and returns the ids of the reviewers who have not
        :param reviewers: list
        :return: list
        """
        notified = self.reviewers_with_authors_sent_feedback
        # print( "n", notified )

        # Make sure we have a list of ids
        reviewers = [ self._handle_id( r ) for r in reviewers ]
        # print( reviewers )

        # Filter out those who have been notified
        reviewers = [ r for r in reviewers if r not in notified ]
        # print( reviewers )

        return reviewers
        # # has_unnotified = [r for r in reviewers if r ]  #  # authors = []  # for student in reviewers:  #     reviewer_id = self._handle_id(student)  #     r = [ra for ra in notified if ra.assessor_id ]  #  #     authors.append()

        #  #     result = self.session \  #         .query(FeedbackReceivedRecord) \  #         .join(ReviewAssociation, FeedbackReceivedRecord.activity_id == ReviewAssociation.activity_id and FeedbackReceivedRecord.student_id == ReviewAssociation.assessee_id).all()  #         # .filter(FeedbackReceivedRecord.activity_id == self.activity.id) \  #         # .filter(ReviewAssociation.activity_id == self.activity.id) \  #         # .filter(ReviewAssociation.assessor_id == reviewer_id) \  #         # .all()

        # result = self.session\  #     .query(FeedbackReceivedRecord)\  #     .outerjoin(ReviewAssociation, FeedbackReceivedRecord.student_id == ReviewAssociation.assessee_id)\  #     .filter(FeedbackReceivedRecord.activity_id == self.activity.id)\  #     .filter(ReviewAssociation.activity_id == self.activity.id)\  #     .filter(ReviewAssociation.assessor_id == reviewer_id)\  #     .one_or_none()  # .filter(FeedbackReceivedRecord.student_id.is_(None))\  # .one_or_none()

        #     if result is not None:  #         result  #         # authors.append( result.student_id )  #  # return authors

        #  #  # td = {'review_association_table' : env.REVIEW_ASSOCIATIONS_TABLE_NAME,  #       'feedback_sent_table': env.FEEDBACK_RECEIVED_STATUS_TABLE_NAME}  # query = """  # SELECT fb.student_id FROM {feedback_sent_table} fb  # INNER JOIN {review_association_table} ra  # ON fb.student_id = ra.assessee_id  # WHERE ra.assessor_id = :student_id  # AND ra.activity_id = :activity_id  # AND fb.activity_id = :activity_id  # """.format(**td)  #  # authors = []  # for student in reviewers:  #     student_id = self._handle_id(student)  #  #     params = {  #         'activity_id' : self.activity.id,  #           'student_id' : student_id  #     }  #  #     stmt = text(query)  #     stmt = stmt.columns( FeedbackReceivedRecord.student_id)  #     result = self.session.query( FeedbackReceivedRecord.student_id)\  #         .from_statement( stmt )\  #         .params( **params )\  #         .one_or_none()  #     if result is not None:  #         authors.append(result)  # return authors


# class MetareviewStatusRepository( IStatusRepository ):
#     """
#     Since the invitation for the metareview needs to
#     record that the invite was sent and that the invitee received
#     feedback, this will handle both
#     """
#
#     def __init__( self, dao: SqliteDAO, unit: Unit ):
#         """
#         Create a repository to handle events for a
#         particular activity
#         """
#         # The activity that we're recording the student as receiving
#         # feedback on
#         self.feedback_activity = unit.initial_work
#         # The activity that we're inviting the student to complete
#         self.invitation_activity = unit.metareview
#
#         self.invite_repo = InvitationStatusRepository( dao, self.invitation_activity )
#         self.feedback_repo = FeedbackStatusRepository( dao, self.feedback_activity )
#
#     def record( self, student, time_to_record=None ):
#         """
#         Create a record that the student was sent their feedback
#         and invited to complete the metareview
#         :param student:
#         :param time_to_record:
#         :return:
#         """
#         self.invite_repo.record( student, time_to_record )
#         self.feedback_repo.record( student, time_to_record )


# ===================== old


class StatusRepository( StudentWorkMixin, IRepo ):
    """
    The status repository tracks when things were sent to
    particular students.

    DEPRECATED. BEING REPLACED AS OF CAN-44 AND CAN-53

    There are two kinds of things that are sent to students:
        Invitations to complete some activity
        Feedback created by another student on that student's work
    """

    def __init__( self, dao: SqliteDAO, activity: Activity ):
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
        student_id = self._handle_id( student_or_id )
        rec = StatusRecord( student_id=student_id, activity_id=self.activity.id )
        self.session.add( rec )
        # todo Consider bulk commits if slow
        self.session.commit()
        return rec

    @property
    def previously_invited( self ):
        """Returns a list of ids of students who have
        already been notified
        """
        records = self.session.query( StatusRecord ).filter( StatusRecord.activity_id == self.activity.id ).filter(
            StatusRecord.notified.isnot( None ) ).all()
        return [ r.student_id for r in
                 records ]  # record = self.get_record(student_or_id)  # if record is not None:  #     # this will be true if notified is a datetime  #     return record.notified is not None  # # If the record hasn't been created yet, it will  # # return false. That way this check can be run before  # # the process that creates the records  # return False

    @property
    def previously_received_feedback( self ):
        """Returns a list of ids of students who have
        already received feedback from another student
        """
        records = self.session.query( StatusRecord ).filter( StatusRecord.activity_id == self.activity.id ).filter(
            StatusRecord.results.isnot( None ) ).all()
        return [ r.student_id for r in records ]

    def get_record( self, student_or_id ):
        """
        Returns the record for the student for this unit or none
        if no record has been created yet
        :param student_or_id:
        :return:
        """
        student_id = self._handle_id( student_or_id )
        return self.session.query( StatusRecord ).filter( StatusRecord.activity_id == self.activity.id ).filter(
            StatusRecord.student_id == student_id ).one_or_none()

    def get_or_create_record( self, student_or_id ):
        """Keeping the 2 required methods separate in
        case have some use to do them separately
        """
        record = self.get_record( student_or_id )
        if record is None:
            record = self.create_record( student_or_id )
        return record

    def record( self, student, time_to_record=None ):
        """
        Main method called.
        The invitiation repo will record when the student was
        invited to do a review.
        The version which will normally record via
        record_invited. However, can be overriden by other
        repos
        :param student:
        :param time_to_record:
        :return:
        """
        raise NotImplementedError

    def record_invited( self, student, time_to_record=None ):
        """Record that the student was notified that the activity_inviting_to_complete
         is available
        """
        print( "record_invited", student )
        record = self.get_or_create_record( student )
        record.record_opened( time_to_record )
        self.session.commit()

    # def record_submitted( self, student, time_to_record=None):
    #     """Record that the student has submitted
    #     the activity_inviting_to_complete
    #     """
    #     record = self.get_or_create_record(student)
    #     record.record_submission(time_to_record)
    #     self.session.commit()

    def record_sent_feedback( self, student, time_to_record=None ):
        """Records when feedback was sent to this student

        This is only relevant for the metareview since need to record when the
        feedback from this student was sent out to the person who did the peer review.
        NB, notified already represents when they were
        invited to do the metareview unit, the results of which we are now sending
        """
        print( 'record_sent', student )
        record = self.get_or_create_record( student )
        record.record_sent_results( time_to_record )
        self.session.commit()

    def has_received_message( self, student_id ):
        raise NotImplementedError


class ComplexStatusRepository:
    """This likely won't be used. Keeping it until done simplifying"""

    def __init__( self, dao: SqliteDAO, unit: Unit ):
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
            student_id = int( student_or_int )
        except TypeError:
            student_id = student_or_int.id
        return student_id

    def load( self ):
        """
        Populates self.data with all existing records for the unit
        :return:
        """
        self.data = self.get_unit_records()

    def get_unit_records( self ):
        """
        Returns all existing records for the unit
        :return: list of StatusReord objects
        """
        return self.session.query( ComplexStatusRecord ).filter(
            ComplexStatusRecord.content_assignment_id == self.content_assignment_id ).all()

    def get_student_record( self, student_or_id ):
        """
        Returns the record for the student for this unit or none
        if no record has been created yet
        :param student_or_id:
        :return:
        """
        student_id = self._handle_id( student_or_id )
        return self.session.query( ComplexStatusRecord ).filter(
            ComplexStatusRecord.content_assignment_id == self.content_assignment_id ).filter(
            ComplexStatusRecord.student_id == student_id ).one_or_none()

    def create_record( self, student_or_id ):
        student_id = self._handle_id( student_or_id )
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
                reviewer_rec = self.create_record( reviewer )

            # Make sure that a record exists for the reviewee
            reviewee_rec = self.get_student_record( reviewee )
            if reviewee_rec is None:
                reviewer_rec = self.create_record( reviewee )

            reviewer_rec.add_reviewee( reviewee )

        # also store reviewor here?

        # todo commit here or rest_timeout for successful notification?
        self.session.commit()

    def record_peer_review_results_sent( self, list_of_students ):
        """
        For each of the students (id or object), records that the initial
        unit has been sent to the reviewer
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
