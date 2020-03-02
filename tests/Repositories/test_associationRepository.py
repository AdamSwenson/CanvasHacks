"""
Created by adam on 1/18/20
"""
from unittest import TestCase
from tests.TestingBase import TestingBase
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from tests.factories.PeerReviewedFactories import unit_factory
from CanvasHacks.Errors.review_pairings import NoAvailablePartner, AllAssigned

from tests.factories.ModelFactories import student_factory
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from faker import Faker
fake = Faker()

__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestAssociationRepository( TestingBase ):
    def setUp(self):
        dao = SqliteDAO()
        self.session = dao.session
        # self.student_ids = [i for i in range(0,5)]
        self.create_new_and_preexisting_students()

        self.unit = unit_factory()
        self.activity = self.unit.initial_work
        self.activity_id = self.activity.id
        self.obj = AssociationRepository(dao, self.activity)

    def test__make_associations_single_submissions( self ):
        # Students only submit once
        # id case
        assoc = self.obj._make_associations(self.student_ids)
        self.assertEqual(len(self.students), len(assoc) , "single submission; ids")

        # obj case
        assoc = self.obj._make_associations(self.students)
        self.assertEqual(len(self.students), len(assoc) , "single submission; objects" )

    def test__make_associations_3_submissions( self ):
        # Students only submit once
        # id case
        self.student_ids = [i for i in range(0,3)]
        assoc = self.obj._make_associations(self.student_ids)
        self.assertEqual(3, len(assoc) , "single submission; ids")

        # obj case
        self.students = [student_factory() for i in range(0,3)]
        assoc = self.obj._make_associations(self.students)
        self.assertEqual(3, len(assoc) , "single submission; objects" )

    def test__make_associations_double_submissions( self ):
        # Students only submit twice adjacent
        s = []
        for so in self.students:
            s.append(so)
            s.append(so)
        # obj case
        assoc = self.obj._make_associations(s)
        for a, b in assoc:
            self.assertNotEqual(a, b,  "self-unit multi submission; objects"  )

    def test__make_associations_double_submissions_ids( self ):
        s = []
        for so in self.student_ids:
            s.append(so)
            s.append(so)
        # obj case
        assoc = self.obj._make_associations(s)
        for a, b in assoc:
            self.assertNotEqual(a, b,  "self-unit multi submission; objects"  )

    def test_assign_reviewer_raises_when_all_submitters_already_assigned( self ):
        preexisting_pairings = self.create_preexisting_review_pairings(self.activity_id, self.preexisting_students)

        with self.assertRaises(AllAssigned):
            self.obj.assign_reviewers(self.preexisting_students)

    def test_assign_reviewer_raises_when_only_one_submitter( self ):
        with self.assertRaises(NoAvailablePartner):
            self.obj.assign_reviewers(self.preexisting_students[:1])


#
    # def test_get_associations( self ):
    #     self.fail()
    #
    # def test_create( self ):
    #     self.fail()
    #
    # def test_create_association( self ):
    #     self.fail()
    #
    # def test_get_reviewer( self ):
    #     self.fail()
    #
    # def test_get_submitter( self ):
    #     self.fail()
    #
    # def test_get_for_assignment( self ):
    #     self.fail()
