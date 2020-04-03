"""
Created by adam on 1/29/20
"""
from unittest import TestCase

from CanvasHacks.GradingMethods.nonempty import receives_credit, CreditForNonEmptyOLD

__author__ = 'adam'

from TestingBase import TestingBase

if __name__ == '__main__':
    pass


class TestCreditForNonEmpty(TestingBase):

    def setUp(self) -> None:
        self.config_for_test()
        self.obj = CreditForNonEmptyOLD()

    def test_grade_credit( self ):
        txt = "The fat wiffle hound wiffled loudly"
        self.assertEqual( 100, self.obj.grade( txt ), "Defaults -- greater than minimum word count" )

    def test_grade_no_credit( self ):
        txt = ""
        self.assertEqual( None, self.obj.grade( txt ), "Defaults -- no credit" )


class Test_receives_credit( TestCase ):
    def test_happy_path_w_defaults( self ):
        txt = "The fat wiffle hound wiffled loudly"
        self.assertTrue(receives_credit(txt), "Defaults -- greater than minimum word count")

        txt = "hello"
        self.assertFalse(receives_credit(txt), "Defaults -- Less than minimum word count")

    def test_excluding_stopwords( self ):
        txt = "The fat wiffle hound wiffled loudly"
        self.assertTrue(receives_credit(txt, count_stopwords=False), "Excluding stopwords; still above minimum")

        txt = "The a dog"
        self.assertFalse(receives_credit(txt, count_stopwords=False), "Excluding stopwords pushes below minimum")