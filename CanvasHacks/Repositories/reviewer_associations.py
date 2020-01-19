"""
Tools for handling and maintaining who is assigned to review whom

Created by adam on 12/28/19
"""
from CanvasHacks.Models.review_association import ReviewAssociation

__author__ = 'adam'
import numpy as np

from CanvasHacks.Models.student import Student


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
        # make an assignment
        assoc_to_make = []
        bad = False
        while bad:
        # while len(assoc_to_make) == 0:
            candidates = assign_reviewers( [ s for s in submitters])
            # Perform checks
            # check no self-assignment
            for s1, s2 in assoc_to_make:
                if s1 == s2:
                    bad = True

        return assoc_to_make


    def get_associations( self, activity ):
        return self.session.query( ReviewAssociation )\
            .filter( ReviewAssociation.activity_id == activity.id )\
            .all()
        #
        #
        # query = """FROM {table_name} SELECT assessor, assessee WHERE activity_id = {activity_id}"""
        #
        # data = {'table_name' : self.table_name, 'activity_id' : activity.id }
        #
        # results = []
        #
        # for row in self.cursor.execute(query.format(**data)):
        #     ra = ReviewAssociation( activity, row[0], row[1])
        #     results.append(ra)
        #
        # return results

    def create( self, activity, submitters ):
        """Sets up a list of associations and then stores them
        This is the main thing to call
        todo: Need to ensure that a person can't be assigned to review themselves since there may be multiple submissions per person
        """
        assoc_to_make = assign_reviewers( [ s for s in submitters])
        for s1, s2 in assoc_to_make:
            self.create_association(activity, assessor=s1, assessee=s2)
        print('Review associations created for {} submitters'.format(len(submitters)))

    def create_association( self, activity, assessor, assessee ):
        ra = ReviewAssociation( activity_id=activity.id, assessor_id=assessor.id, assessee_id=assessee.id )
        self.session.add( ra )
        self.session.commit()

    def get_reviewer( self, activity, submitter: Student ):
        """Returns the student assigned to review the submitter"""
        return self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity.id ) \
            .filter( ReviewAssociation.assessor_id == submitter.id ) \
            .one()

    def get_submitter( self, activity, reviewer: Student ):
        """Returns the student assigned to review the submitter"""
        return self.session.query( ReviewAssociation )\
            .filter( ReviewAssociation.activity_id == activity.id )\
            .filter( ReviewAssociation.assessor_id == reviewer.id )\
            .one()

    def get_for_assignment( self, assignment ):
        """Returns list of all submitter, reviewer tuples"""
        pass


if __name__ == '__main__':
    pass
