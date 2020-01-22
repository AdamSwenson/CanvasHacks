"""
Tools for handling and maintaining who is assigned to review whom

Created by adam on 12/28/19
"""
from CanvasHacks.Models.review_association import ReviewAssociation

__author__ = 'adam'
import numpy as np
import random
from CanvasHacks.Models.student import Student, ensure_student


def assign_reviewers( student_ids ):
    """
    Takes a list of students or student ids and creates a dict
    of reviewers by shifting them all one to the right

    >>>test_ids = [1, 2, 3, 4]
    >>>test_ids = [1, 2, 3, 4, 5, 6, 7]
    >>>r = assign_reviewers(test_ids)
    >>>for a, b in r:
    >>>   assert(a != b) # no id assigned to self
    """
    return list( zip( student_ids, np.roll( student_ids, 1 ) ) )


class AssociationRepository:

    def __init__( self, dao ):
        """
        :param db_loc: Where to find the sqlite database or 'sqlite:///:memory:'
        """
        self.session = dao.session

    #     self._connect()
    #
    # def _connect( self ):
    #     self.engine = create_engine(self.db_loc)
    #
    #
    # self.connection = sqlite3.connect(self.db_loc)
    # self.cursor = self.connection.cursor()

    # def _handle_result( self, row ):
    #     """Loads a ReviewAssociation object """

    def _make_associations( self, submitters ):
        """Handles creating the review assignment associations.
        We use this since it builds in checks for problem cases given that
        for some assignments students may submit more than
        one item."""
        while True:
            # randomize list of submitters
            # to hopefully (further) split up adjacent submissions by the
            # same student
            random.shuffle( submitters )
            # Making a list upon input incase we've been passed an iterator
            candidate = assign_reviewers( [ s for s in submitters ] )
            bad = False
            for b, c in candidate:
                # Perform checks
                # Note that this should work regardless of whether
                # received list of student objects or just their ids
                if b == c:
                    # self assignment so start over
                    bad = True
            if bad:
                continue
            else:
                # if we completed the loops, no one is reviewing themselves
                return candidate

    def assign_reviewers( self, activity, submitters ):
        """Assigns every student in submitters to review one other
        student.
        This is the main method to call
        todo: Need to ensure that a person can't be assigned to review themselves since there may be multiple submissions per person
        """
        assoc_to_make = self._make_associations(  submitters)
        # assoc_to_make = assign_reviewers( [ s for s in submitters ] )
        assocs = []
        for s1, s2 in assoc_to_make:
            a = self._create_association( activity, assessor=ensure_student(s1), assessee=ensure_student(s2) )
            assocs.append(a)
        print( 'Review associations created for {} submitters and stored in db'.format( len( submitters ) ) )
        # return assocs

    def _create_association( self, activity, assessor, assessee ):
        """Creates a ReviewAssociation object for the given students and
        saves it to the db
        """
        ra = ReviewAssociation( activity_id=activity.id, assessor_id=assessor.id, assessee_id=assessee.id )
        self.session.add( ra )
        self.session.commit()
        return ra

    def get_associations( self, activity ):
        """Returns all review assignments for the activity"""
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .all()

    def get_reviewer( self, activity, submitter: Student ):
        """Returns the student assigned to review the submitter"""
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .filter( ReviewAssociation.assessor_id == submitter.id ) \
            .one()

    def get_submitter( self, activity, reviewer: Student ):
        """Returns the student assigned to review the submitter"""
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .filter( ReviewAssociation.assessor_id == reviewer.id ) \
            .one()

    def get_for_assignment( self, assignment ):
        """Returns list of all submitter, reviewer tuples"""
        pass


if __name__ == '__main__':
    pass
