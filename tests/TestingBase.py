"""
Created by adam on 2/22/20
"""

import CanvasHacks.testglobals
from CanvasHacks.Models.submission_record import SubmissionRecord

CanvasHacks.testglobals.TEST = True
CanvasHacks.testglobals.use_api = False

from CanvasHacks.Models.status_record import FeedbackReceivedRecord, InvitationReceivedRecord
from CanvasHacks.Repositories.reviewer_associations import assign_reviewers
from CanvasHacks.TimeTools import current_utc_timestamp
from factories.ModelFactories import make_students

__author__ = 'adam'

from CanvasHacks import environment as env

import unittest
from faker import Faker

if __name__ == '__main__':
    pass


class TestingBase( unittest.TestCase ):

    def config_for_test( self, use_api=False ):
        print( 'setting test' )
        env.CONFIG.set_test()
        self.fake = Faker()

    def student_getter( self, sid ):
        """Retrieves a test student from the list of test students"""
        # print("student_getter called on ", sid)
        return [ s for s in self.students if s.student_id == sid ][ 0 ]

    def create_new_and_preexisting_students( self, new=5, old=5 ):
        """
        Creates two groups of students for testing.
        Will be stored in self.new_students and self.preexisting
        Ids will be stored simililarly
        All will be in self.students
        :param new: How many new students to create
        :param old: How many existing students to create
        :return:
        """
        # Create students
        self.new_students = make_students( new )
        self.preexisting_students = make_students( old )

        self.students = self.new_students + self.preexisting_students

        # Store lists of the ids for convienience
        self.student_ids = [ s.student_id for s in self.students ]
        self.preexisting_student_ids = [ s.student_id for s in self.preexisting_students ]
        self.new_students_ids = [ s.student_id for s in self.new_students ]

    def create_preexisting_review_pairings( self, activity_id, preexisting_students, session=None,
                                            check_db_before_run=True ):
        """Populates the in-memory database with ReviewAssociations between
        the provided students
        NB, must have the dao session stored on self.session
        """
        # Here to avoid problems when running tests offline
        from CanvasHacks.Models.review_association import ReviewAssociation

        old_assigns = assign_reviewers( preexisting_students )

        session = session if session is not None else self.session

        for assessor, assessee in old_assigns:
            ra = ReviewAssociation( activity_id=activity_id, assessor_id=int( assessor.student_id ),
                                    assessee_id=int( assessee.student_id ) )
            session.add( ra )
            session.commit()

        self.pairings = session.query( ReviewAssociation ).filter( ReviewAssociation.activity_id == activity_id ).all()

        if check_db_before_run is True:
            self.assertEqual( len( preexisting_students ), len( self.pairings ),
                              "PRE-RUN CHECK: {} students in db".format( len( preexisting_students ) ) )

        return self.pairings

    def make_feedback_received_records( self, number, session=None ):
        session = session if session is not None else self.session
        self.previously_sent = [ ]

        for i in range( 0, number ):
            student_id = self.student_ids[ i ]
            rec = FeedbackReceivedRecord( student_id=student_id,
                                          activity_id=self.activity.id,
                                          sent_at=current_utc_timestamp() )
            session.add( rec )
            session.commit()
            self.previously_sent.append( student_id )

        self.assertEqual( number, len( self.previously_sent ), "dummy check" )

    def make_invitation_received_records( self, number, session=None ):
        session = session if session is not None else self.session
        self.previously_sent = [ ]

        for i in range( 0, number ):
            student_id = self.student_ids[ i ]
            rec = InvitationReceivedRecord( student_id=student_id,
                                            activity_id=self.activity.id,
                                            sent_at=current_utc_timestamp() )
            session.add( rec )
            session.commit()
            self.previously_sent.append( student_id )

        self.assertEqual( number, len( self.previously_sent ), "dummy check" )

    def make_submitted_records( self, number, session=None ):
        session = session if session is not None else self.session
        self.previously_submitted = [ ]

        for i in range( 0, number ):
            student_id = self.student_ids[ i ]
            rec = SubmissionRecord( student_id=student_id,
                                    activity_id=self.activity.id,
                                    submitted_at=current_utc_timestamp() )
            session.add( rec )
            session.commit()
            self.previously_submitted.append( student_id )

        self.assertEqual( number, len( self.previously_submitted ), "dummy check" )
