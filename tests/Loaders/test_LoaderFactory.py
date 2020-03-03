"""
Created by adam on 2/24/20
"""
# import CanvasHacks.globals
# CanvasHacks.globals.use_api = False
from unittest.mock import MagicMock

from CanvasHacks.Loaders.assignment import AssignmentDownloadLoader
from CanvasHacks.Loaders.discussion import DiscussionDownloadLoader, DiscussionFileLoader
from CanvasHacks.Loaders.factories import LoaderFactory, QuizLoaderFactory
from CanvasHacks.Loaders.quiz import AllQuizReportDownloader, AllQuizReportFileLoader, NewQuizReportDownloadLoader, \
    NewQuizReportFileLoader
from factories.PeerReviewedFactories import unit_factory
from tests.TestingBase import TestingBase

__author__ = 'adam'


class TestLoaderFactory( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.course = MagicMock()
        self.unit = unit_factory()

    def test_returns_discussion_download_loader( self ):
        r = LoaderFactory.make(is_discussion=True)
        self.assertEqual(r, DiscussionDownloadLoader)

    def test_returns_discussion_file_loader( self ):
        r = LoaderFactory.make(is_discussion=True, download=False)
        self.assertEqual(r, DiscussionFileLoader)

    def test_returns_assignment_loader( self ):
        r = LoaderFactory.make( is_quiz=False )
        self.assertEqual( r, AssignmentDownloadLoader )

    # Tests to make sure quiz loader passes correct loader up
    # to the main loader factory

    def test_make_download_new( self ):
        download = True
        only_new = True

        # call
        result = LoaderFactory.make( download, only_new )

        # check
        self.assertEqual( result, NewQuizReportDownloadLoader )

    def test_make_download_all( self ):
        download = True
        only_new = False

        # call
        result = LoaderFactory.make( download, only_new )

        # check
        self.assertEqual( result, AllQuizReportDownloader )

    def test_make_file_new( self ):
        download = False
        only_new = True

        # call
        result = LoaderFactory.make( download, only_new )

        # check
        self.assertEqual( result, NewQuizReportFileLoader )

    def test_make_file_all( self ):
        download = False
        only_new = False

        # call
        result = LoaderFactory.make( download, only_new )

        # check
        self.assertEqual( result, AllQuizReportFileLoader )


class TestAssignmentLoaderFactory( TestingBase ):

    def setUp( self ):
        self.config_for_test()

    def test_returns_assignment_loader( self ):
        r = LoaderFactory.make( is_quiz=False )
        self.assertEqual(r, AssignmentDownloadLoader, "Returns the AssignmentDownloadLoader")


class TestQuizLoaderFactory( TestingBase ):

    def setUp( self ):
        self.config_for_test()

    def test_make_download_new( self ):
        download = True
        only_new = True

        # call
        result = QuizLoaderFactory.make( download, only_new )

        # check
        self.assertEqual( result, NewQuizReportDownloadLoader )

    def test_make_download_all( self ):
        download = True
        only_new = False

        # call
        result = LoaderFactory.make( download, only_new )

        # check
        self.assertEqual( result, AllQuizReportDownloader )

    def test_make_file_new( self ):
        download = False
        only_new = True

        # call
        result = LoaderFactory.make( download, only_new )

        # check
        self.assertEqual( result, NewQuizReportFileLoader )

    def test_make_file_all( self ):
        download = False
        only_new = False

        # call
        result = LoaderFactory.make( download, only_new )

        # check
        self.assertEqual( result, AllQuizReportFileLoader )
