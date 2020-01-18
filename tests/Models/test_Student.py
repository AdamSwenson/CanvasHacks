"""
Created by adam on 12/24/19
"""
from unittest import TestCase

from faker import Faker

from CanvasHacks.Models.student import Student

fake = Faker()

__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestStudent( TestCase ):

    def test_handle_kwargs( self ):
        td = { 'student_id': fake.isbn10(),
              }
        kws = {
            'name': fake.name(),
            'taco': 'fish',
            'noses': 5 }

        obj = Student( td[ 'student_id' ],  **kws )

        for k in kws.keys():
            self.assertEqual( getattr( obj, k ), kws[ k ] )

    def test_comparison_for_equality( self ):
        s1 = Student(333333)
        s2 = Student(333333)
        self.assertTrue(s1 == s2, "Correctly handles students w same id")

        s1 = Student(333333)
        s3 = Student(222222)
        self.assertFalse(s1 == s3, "Correctly handles students w different ids")
