"""
Created by adam on 2/1/19
"""
from unittest import TestCase
from assets.DownloadProcessingTools import *

__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestChooseHandler( TestCase ):
    def test_unknown( self ):
        result = chooseHandler('.parg')
        self.assertEqual(result.__name__, 'unknown_handler')

    def test_pdf( self ):
        result = chooseHandler('.pdf')
        self.assertEqual(result.__name__, 'pdf_handler')

