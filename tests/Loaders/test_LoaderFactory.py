"""
Created by adam on 2/24/20
"""
# import CanvasHacks.globals
# CanvasHacks.globals.use_api = False

from CanvasHacks.Loaders.quiz import NewQuizReportDownloadLoader, LoaderFactory, NewQuizReportFileLoader, AllQuizReportFileLoader, AllQuizReportDownloader
from tests.TestingBase import TestingBase
from unittest import TestCase

__author__ = 'adam'


class TestLoaderFactory( TestingBase):

    def setUp(self):
        self.config_for_test()

    def test_make_download_new( self ):
        download = True
        only_new = True

        # call
        result = LoaderFactory.make(download, only_new)

        # check
        self.assertEqual(result, NewQuizReportDownloadLoader)

    def test_make_download_all( self ):
        download = True
        only_new = False

        # call
        result = LoaderFactory.make(download, only_new)

        # check
        self.assertEqual(result, AllQuizReportDownloader)

    def test_make_file_new( self ):
        download = False
        only_new = True

        # call
        result = LoaderFactory.make(download, only_new)

        # check
        self.assertEqual(result, NewQuizReportFileLoader)

    def test_make_file_all( self ):
        download = False
        only_new = False

        # call
        result = LoaderFactory.make(download, only_new)

        # check
        self.assertEqual(result, AllQuizReportFileLoader)
