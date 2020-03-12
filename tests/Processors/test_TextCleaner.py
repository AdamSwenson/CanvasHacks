"""
Created by adam on 3/11/20
"""
__author__ = 'adam'

from unittest import TestCase

from CanvasHacks.Processors.cleaners import TextCleaner
from TestingBase import TestingBase

if __name__ == '__main__':
    pass


class TestTextCleaner( TestingBase ):


    def setUp(self) -> None:
        self.config_for_test()
        self.obj = TextCleaner()


    def test_clean( self ):
        self.fail()
