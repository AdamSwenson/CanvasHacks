"""
Created by adam on 2/22/20
"""
from CanvasHacks.Models.review_association import ReviewAssociation
from CanvasHacks.Repositories.reviewer_associations import assign_reviewers
from factories.ModelFactories import make_students

__author__ = 'adam'

import CanvasHacks.globals

CanvasHacks.globals.TEST = True
CanvasHacks.globals.use_api = False

from CanvasHacks import environment as env

import unittest


if __name__ == '__main__':
    pass


class TestingBase(unittest.TestCase):

    def config_for_test( self ):
        print('setting test')
        env.CONFIG.set_test()

    def student_getter( self, sid ):
        """Retrieves a test student from the list of test students"""
        print("student_getter called on ", sid)
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
        self.student_ids = [s.student_id for s in self.students]
        self.preexisting_student_ids = [ s.student_id for s in self.preexisting_students ]
        self.new_students_ids = [ s.student_id for s in self.new_students ]

    def create_preexisting_review_pairings( self, activity_id, preexisting_students ):
        """Populates the in-memory database with ReviewAssociations between
        the provided students
        NB, must have the dao session stored on self.session
        """
        old_assigns = assign_reviewers( preexisting_students )

        for assessor, assessee in old_assigns:
            ra = ReviewAssociation( activity_id=activity_id,
                                    assessor_id=int( assessor.student_id ), assessee_id=int( assessee.student_id )
                                    )
            self.session.add( ra )
            self.session.commit()
        pairings = self.session.query( ReviewAssociation ) \
            .filter( ReviewAssociation.activity_id == activity_id ).all()
        self.assertEqual( len( preexisting_students ), len( pairings  ),  "PRE-RUN CHECK: {} students in db".format( len(preexisting_students ) ) )
        return pairings

