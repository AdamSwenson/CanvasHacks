"""
Tools for handling and maintaining who is assigned to review whom

Created by adam on 12/28/19
"""
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Errors.review_pairings import NoAvailablePartner, AllAssigned
from CanvasHacks.Models.review_association import ReviewAssociation
from CanvasHacks.Definitions.activity import Activity
import pandas as pd

__author__ = 'adam'
import numpy as np
import random

from CanvasHacks.Repositories.mixins import ObjectHandlerMixin


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


# def force_to_ids(list_of_students):
#     """We could receive a list of ids, Student
#     objects or canvasapi User objects. This returns
#     a list of ids"""
#     out = []
#
#     for s in list_of_students:
#         if isinstance(s, int):
#             out.append(s)
#         else:
#             # Both Student and User objects will have an id attribute
#             # which contains the canvas id of the student
#             out.append(s.id)
#     return out


class AssociationRepository(ObjectHandlerMixin):

    def __init__( self, dao: SqliteDAO, activity: Activity):
        """
        Create a repository to handle review assignments for a
        particular activity
        """
        self.activity = activity
        self.session = dao.session

    def _make_associations( self, submitters ):
        """Handles creating the review unit associations.
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
                    # self unit so start over
                    bad = True
            if bad:
                continue
            else:
                # if we completed the loops, no one is reviewing themselves
                return candidate

    def assign_reviewers( self, submitters ):
        """
        Assigns every student in submitters to review one other
        student.
        This is the main method to call
        :param submitters: List of ids or students
        :return list of ReviewAssociation objects
        :raises AllAssigned, NoAvailablePartner,
        """
        # Force list of submitters to be a list of ids
        submitters = self.force_to_ids(submitters)

        # Filter out anyone who has already been assigned to review
        # someone. That will leave anyone who is just now submitting
        # and anyone who was left hanging without a reviewee in a previous
        # run.
        filtered_submitters = self.filter_assigned_reviewers(submitters)

        # Check whether everyone is already paired up
        if len(filtered_submitters) == 0:
            # We will return the original list because this likely
            # indicates people have done something wierd like resubmit late
            raise AllAssigned(submitters)

        # Check whether we only have 1 new submitter
        # and thus will not be able to partner them up
        if len(filtered_submitters) == 1:
            raise NoAvailablePartner(filtered_submitters)

        # Pair up the remaining students
        assoc_to_make = self._make_associations(  filtered_submitters)

        self.new_assignments = []
        for assessor, assessee in assoc_to_make:
            # print(assessor, assessee)
            a = self._create_association( self.activity, assessor_id=assessor, assessee_id=assessee )
            self.new_assignments.append(a)
        print( '{} Review associations created for {} submitters and stored in db'.format(len(self.new_assignments), len( filtered_submitters ) ) )
        print("See this object's audit_frame method for details")

        # make_review_audit_file(self, self.student_repository)
        return self.new_assignments

    def audit_frame( self, student_repository ):
        """
        Returns a data frame with all the current review
        pairings
        :return: DataFrame
        """
        review_audit = []
        for rev in self.get_associations():
            # print(rev.assessor_id, rev.assessee_id)
            assessor = student_repository.get_student( rev.assessor_id )
            assessee = student_repository.get_student( rev.assessee_id )
            # print(assessor)

            review_audit.append({
                'activity_inviting_to_complete' : self.activity.name,
                'assessor_name' : assessor.short_name,
                'assessor_sis_id': assessor.sis_user_id,
                'assessor_canvas_id': assessor.id,
                'assessee_name' : assessee.short_name,
                'assessee_sis_id': assessee.sis_user_id,
                'assessee_canvas_id': assessee.id,
            })

        return pd.DataFrame(review_audit)

    def _create_association( self, activity, assessor_id, assessee_id ):
        """Creates a ReviewAssociation object for the given students and
        saves it to the db
        Leaving activity_inviting_to_complete as a param even though it is now a property of the object
        so test methods can call on its own
        """
        ra = ReviewAssociation( activity_id=activity.id, assessor_id=int(assessor_id), assessee_id=int(assessee_id) )
        self.session.add( ra )
        self.session.commit()
        return ra

    def get_associations( self, activity=None ):
        """Returns all review assignments for the activity_inviting_to_complete
        Leaving activity_inviting_to_complete as a param even though it is now a property of the object
        so test methods can call on its own """
        if activity is None:
            activity = self.activity
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .all()

    def get_assessor_object( self, activity, author_id ):
        """Returns the ReviewAssociation object containing the
        of the student assigned to review the submitter
        or None if no student has been assigned
        Leaving activity_inviting_to_complete as a param even though it is now a property of the object
        so test methods can call on its own
        """
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .filter( ReviewAssociation.assessee_id == author_id ) \
            .one_or_none()

    @property
    def data( self):
        return self.get_associations()

    def get_assessor( self, activity, submitter_id ):
        """Returns the id of the student assigned to review the submitter
        or None if no student has been assigned
        Leaving activity_inviting_to_complete as a param even though it is now a property of the object
        so test methods can call on its own
        """
        r = self.get_assessor_object(activity, submitter_id)
        # r = self.session.query( ReviewAssociation ) \
        #     .filter( ReviewAssociation.activity_id == activity_inviting_to_complete.id ) \
        #     .filter( ReviewAssociation.assessee_id == submitter_id ) \
        #     .one_or_none()
        if r:
            return r.assessor_id
        return r

    def get_by_assessor( self, activity, reviewer_id ):
        """
        Returns the review object where the student is the assessor
        :param activity:
        :param reviewer_id:
        :return:
        """
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .filter( ReviewAssociation.assessor_id == reviewer_id ) \
            .one_or_none()

    def get_by_assessee( self, activity, author_id ):
        """
        Returns the review object where the student is the author of
        the original work
        :param activity:
        :param author_id:
        :return:
        """
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .filter( ReviewAssociation.assessee_id == author_id ) \
            .one_or_none()

    def get_by_author( self, author ):
        """
        Returns the review object where the student is the author of
        the original work
        Introduced in preparation for CAN-52
        :param author: Student or student id
        :return: ReviewAssociation or None
        """
        author_id = self._handle_id(author)
        return self.session.query( ReviewAssociation )\
            .filter( ReviewAssociation.activity_id == self.activity.id )\
            .filter( ReviewAssociation.assessee_id == author_id )\
            .one_or_none()

    def get_by_reviewer( self, reviewer ):
        """
        Returns the review object where the student is the assessor of the
        original work

        Introduced in preparation for CAN-52

        :param reviewer: Student or student id
        :return:
        """
        reviewer_id = self._handle_id(reviewer)
        return self.session.query( ReviewAssociation )\
            .filter( ReviewAssociation.activity_id == self.activity.id )\
            .filter( ReviewAssociation.assessor_id == reviewer_id )\
            .one_or_none()

    def get_assessee_object( self, activity, reviewer_id ):
        """Returns the ReviewAssociation object containing the student
         assigned to be reviewed by the reviewer
        or None if no student has been assigned
        Leaving activity_inviting_to_complete as a param even though it is now a property of the object
        so test methods can call on its own
        """
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .filter( ReviewAssociation.assessor_id == reviewer_id ) \
            .one_or_none()

    def get_assessee( self, activity, reviewer_id ):
        """Returns the student assigned to be reviewed by the reviewer
        or None if no student has been assigned
        Leaving activity_inviting_to_complete as a param even though it is now a property of the object
        so test methods can call on its own
        """
        r = self.get_assessee_object(activity, reviewer_id)
        if r:
            return r.assessee_id
        return r

    def get_for_assignment( self, assignment ):
        """Returns list of all submitter, reviewer tuples"""
        pass

    def filter_assigned_reviewers( self, submitters ):
        """Removes entries from list who have already
        been assigned to review someone"""
        prev = len(submitters)
        submitters = [ s for s in submitters if self.get_assessee(self.activity, s) is None]
        print("Removed {} submitters who were already assigned".format(prev - len(submitters) ))
        return submitters


if __name__ == '__main__':
    pass
