"""
Created by adam on 1/29/20
"""
from unittest import TestCase

from CanvasHacks.GradingTools.nonempty import receives_credit

__author__ = 'adam'

if __name__ == '__main__':
    pass


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