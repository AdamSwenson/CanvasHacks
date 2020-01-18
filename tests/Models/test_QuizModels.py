"""
Created by adam on 5/6/19
"""
from unittest import TestCase

from CanvasHacks.Models.QuizModels import QuizData

__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestQuizData( TestCase ):
    def test_course_id( self ):
        self.fail()

    def test_due_date( self ):
        self.fail()

    def test_quarter_credit_date( self ):
        self.fail()

    def test_quarter_credit_date( self ):
        self.fail()

    def test_lock_date( self ):
        self.fail()

    def test_name( self ):
        self.fail()

    def test_set_question_columns( self ):
        self.fail()

    def test__detect_question_columns( self ):
        test = [ 'submitted', 'attempt', "1785114: \nWhat is an example of persuasive advertising?", '1.0' ]
        qd = QuizData()
        self.assertEqual( qd._detect_question_columns( test ),
                          [ "1785114: \nWhat is an example of persuasive advertising?" ] )
