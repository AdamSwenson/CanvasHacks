"""
Created by adam on 12/24/19
"""
from unittest import TestCase

from faker import Faker

from CanvasHacks.Models.student import Student, ensure_student
from tests.factories.ModelFactories import student_factory

fake = Faker()

__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestStudentUtilities( TestCase ):

    def test_ensure_student_when_student( self ):
        s = student_factory()
        r = ensure_student( s )
        self.assertIsInstance( r, Student, "Returns student" )
        self.assertTrue( s == r )

    def test_ensure_student_int_id( self ):
        s = 1111114
        r = ensure_student( s )
        self.assertIsInstance( r, Student, "Returns student" )
        self.assertTrue( s == r.student_id )

    def test_ensure_student_string_id( self ):
        s = '1111114'
        r = ensure_student( s )
        self.assertIsInstance( r, Student, "Returns student" )
        self.assertTrue( int( s ) == r.student_id )

    def test_ensure_student_dict( self ):
        s = {'student_id' : '1111114',
             'other' : 'taco'}
        r = ensure_student( s )
        self.assertIsInstance( r, Student, "Returns student in dictionary case" )
        self.assertTrue( int( s['student_id'] ) == r.id )

    def test_ensure_student_obj( self ):
        self.skipTest('unsure if needed')
        # s = object()
        # setattr(s, 'student_id', '1111114')
        # r = ensure_student( s )
        # self.assertIsInstance( r, Student, "Returns student in object case" )
        # self.assertTrue( int( s['student_id'] ) == r.id )
        #


class TestStudent( TestCase ):

    # def test_handle_kwargs( self ):
    #     td = { 'student_id': fake.isbn10(),
    #            }
    #     kws = {
    #         'name': fake.name(),
    #         'taco': 'fish',
    #         'noses': 5 }
    #
    #     obj = Student( td[ 'student_id' ], **kws )
    #
    #     for k in kws.keys():
    #         self.assertEqual( getattr( obj, k ), kws[ k ] )

    def test_comparison_for_equality( self ):
        s1 = Student( student_id=333333 )
        s2 = Student( student_id=333333 )
        self.assertTrue( s1 == s2, "Correctly handles students w same id" )

        s1 = Student( student_id=333333 )
        s3 = Student( student_id=222222 )
        self.assertFalse( s1 == s3, "Correctly handles students w different ids" )
