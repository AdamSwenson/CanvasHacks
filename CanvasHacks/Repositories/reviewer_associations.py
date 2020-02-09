"""
Tools for handling and maintaining who is assigned to review whom

Created by adam on 12/28/19
"""
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Models.review_association import ReviewAssociation
from CanvasHacks.PeerReviewed.Definitions import Activity

__author__ = 'adam'
import numpy as np
import random
import datetime


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


def force_to_ids( list_of_students ):
    """We could receive a list of ids, Student
    objects or canvasapi User objects. This returns
    a list of ids"""
    out = [ ]

    for s in list_of_students:
        if isinstance( s, int ):
            out.append( s )
        else:
            # Both Student and User objects will have an id attribute
            # which contains the canvas id of the student
            out.append( s.id )
    return out


class AssociationRepository:

    def __init__( self, dao: SqliteDAO, activity: Activity ):
        """
        Create a repository to handle review assignments for a
        particular activity
        """
        self.activity = activity
        self.session = dao.session

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

    def assign_reviewers( self, submitters ):
        """Assigns every student in submitters to review one other
        student.
        This is the main method to call
        """
        # Force list of submitters to be a list of ids
        submitters = force_to_ids( submitters )
        # Filter out anyone who has already been assigned to review
        # someone. That will leave anyone who is just now submitting
        # and anyone who was left hanging without a reviewee in a previous
        # run.
        submitters = self.filter_assigned_reviewers( submitters )

        # Pair up the remaining students
        assoc_to_make = self._make_associations( submitters )
        # assoc_to_make = assign_reviewers( [ s for s in submitters ] )

        assocs = [ ]
        for s1, s2 in assoc_to_make:
            print( s1, s2 )
            a = self._create_association( self.activity, assessor_id=s1, assessee_id=s2 )
            assocs.append( a )
        print( '{} Review associations created for {} submitters and stored in db'.format( len( assocs ),
                                                                                           len( submitters ) ) )
        # return assocs

    def _create_association( self, activity, assessor_id, assessee_id ):
        """Creates a ReviewAssociation object for the given students and
        saves it to the db
        Leaving activity as a param even though it is now a property of the object
        so test methods can call on its own
        """
        ra = ReviewAssociation( activity_id=activity.id,
                                assessor_id=int( assessor_id ),
                                assessee_id=int( assessee_id ),
                                created_at=datetime.datetime.utcnow()
                                )
        self.session.add( ra )
        self.session.commit()
        return ra

    def get_associations( self, activity ):
        """Returns all review assignments for the activity
        Leaving activity as a param even though it is now a property of the object
        so test methods can call on its own """
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .all()

    def get_assessor( self, activity, submitter_id ):
        """Returns the id of the student assigned to review the submitter
        or None if no student has been assigned
        Leaving activity as a param even though it is now a property of the object
        so test methods can call on its own
        """
        r = self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .filter( ReviewAssociation.assessee_id == submitter_id ) \
            .one_or_none()
        if r:
            return r.assessor_id
        return r

    def get_assessee( self, activity, reviewer_id ):
        """Returns the student assigned to be reviewed by the reviewer
        or None if no student has been assigned
        Leaving activity as a param even though it is now a property of the object
        so test methods can call on its own
        """
        r = self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .filter( ReviewAssociation.assessor_id == reviewer_id ) \
            .one_or_none()
        if r:
            return r.assessee_id
        return r

    def get_for_assignment( self, assignment ):
        """Returns list of all submitter, reviewer tuples"""
        pass

    def filter_assigned_reviewers( self, submitters ):
        """Removes entries from list who have already
        been assigned to review someone"""
        prev = len( submitters )
        submitters = [ s for s in submitters if self.get_assessee( self.activity, s ) is None ]
        print( "Removed {} submitters who were already assigned".format( prev - len( submitters ) ) )
        return submitters

    def get_most_recent_date( self, activity ):
        """will return the most recent date (in utc) of the
        review assignments for the activity.
        This can be used to determine which students have
        submitted after the last run
        """
        results = self.get_associations( activity )
        results.sort( key=lambda x: x.created_at, reverse=True )
        return results


if __name__ == '__main__':
    pass
