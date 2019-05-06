"""
Created by adam on 5/6/19
"""
from unittest import TestCase

from CanvasHacks.QuizStudentDataManagement import make_drop_list

__author__ = 'adam'


class TestQuizStudentDataManagement( TestCase ):

    def test_load_student_work( self ):
        self.fail()

    def test_make_drop_list( self ):
        test = [ 'name', 'id', 'sis_id', '1.0', '1.0.1', '1.0.2' ]
        self.assertEqual( make_drop_list( test ), [ '1.0', '1.0.1', '1.0.2' ] )
