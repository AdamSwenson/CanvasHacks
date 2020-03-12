"""
Created by adam on 3/11/20
"""
__author__ = 'adam'

from unittest import TestCase

from CanvasHacks.Processors.cleaners import HtmlCleaner
from TestingBase import TestingBase

if __name__ == '__main__':
    pass

TEST_DATA = [
    { 'input': "<p>Tacos are nom</p>",
      'expect': "Tacos are nom"
      },

]


class TestHtmlCleaner( TestingBase ):

    def setUp(self) -> None:
        self.config_for_test()
        self.obj = HtmlCleaner()

    def test_clean( self ):
        for t in TEST_DATA:
            self.assertEqual(t['expect'], self.obj.clean(t['input']))
