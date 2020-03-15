"""
Created by adam on 5/6/19
"""
from unittest import TestCase

from CanvasHacks.Processors.quiz import make_drop_list

__author__ = 'adam'


class TestQuizStudentDataManagement( TestCase ):

    def test_load_student_work( self ):
        self.skipTest('todo')

    def test_make_drop_list( self ):
        test = [ 'name', 'id', 'sis_id', '1.0', '1.0.1', '1.0.2' ]
        result = make_drop_list( test )
        expected = [ '1.0', '1.0.1', '1.0.2' ]
        for e in expected:
            # doing it this way so won't automatically fail if add
            # additional stems to the list which defines what to drop
            self.assertIn( e, result)
