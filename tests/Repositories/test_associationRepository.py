"""
Created by adam on 1/18/20
"""
from unittest import TestCase

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from tests.factories.ModelFactories import student_factory
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestAssociationRepository( TestCase ):
    def setUp(self):
        dao = SqliteDAO()
        self.students = [student_factory() for i in range(0,5)]
        # for i in range(0,5):
        #     self.students.append(student_factory())
        self.obj = AssociationRepository(dao)

    def test__make_associations_single_submissions( self ):
        # Students only submit once
        assoc = self.obj._make_associations(self.students)
        self.assertEqual(5, len(assoc) )

    def test__make_associations_double_submissions( self ):
        # Students only submit twice adjacent
        s = []
        for so in self.students:
            s.append(so)
            s.append(so)
        assoc = self.obj._make_associations(s)
        self.assertEqual(10, len(assoc) )



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
