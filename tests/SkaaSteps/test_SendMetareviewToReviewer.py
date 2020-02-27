"""
Tests that the correct content will get
sent to the reviewer after the metareview is complete
Created by adam on 2/22/20
"""
__author__ = 'adam'
import unittest
from unittest.mock import MagicMock, patch
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import unit_factory
import CanvasHacks.testglobals
CanvasHacks.testglobals.use_api = False

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from tests.TestingBase import TestingBase

from CanvasHacks.SkaaSteps.SendMetareviewToReviewer import SendMetareviewToReviewer


# Make sure correct students involved (have more than the 2 in db)
# Make sure correct text is sent
# Make sure addressing params are correct


class TestCallsAllExpected( TestingBase ):
    """Makes sure that everything gets called with expected values.
      Not super diagnostic since many of the mocked calls are
      where we'd actually expect failure. Still, useful for catching
      problems when update code etc"""

    def setUp( self ):
        self.config_for_test()
        self.dao = SqliteDAO()

        self.course = MagicMock()
        self.unit = unit_factory()

    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.StudentRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.FeedbackFromMetareviewMessenger' )
    @patch( 'CanvasHacks.SkaaSteps.ISkaaSteps.AssociationRepository' )
    @patch( 'CanvasHacks.SkaaSteps.SendMetareviewToReviewer.WorkRepositoryLoaderFactory' )
    def test_run( self, workLoaderMock, assocRepoMock, messengerMock, studentRepoMock ):
        """Check that each student receives the expected message
        containing the correct student's submission
        """
        students = [ student_factory(), student_factory() ]
        submitter_ids = [ s.student_id for s in students ]
        workRepo = MagicMock()
        workRepo.submitter_ids = submitter_ids
        workLoaderMock.make = MagicMock( return_value=workRepo )

        studentRepoMock.download = MagicMock( return_value=students )
        send = True
        obj = SendMetareviewToReviewer( course=self.course, unit=self.unit, is_test=True, send=True )

        # call
        obj.run()

        # check
        workLoaderMock.make.assert_called()
        workLoaderMock.make.assert_called_with( self.unit.initial_work, self.course, True )

        obj.studentRepo.download.assert_called()

        obj.messenger.notify.assert_called()
        obj.messenger.notify.assert_called_with( obj.associationRepo.data, send )


class TestOnTimeSubmissions( TestingBase ):
    """Checks that works properly on first run after
    deadline on work that has been submitted
    """

    def test_run( self ):
        """todo
        """
        self.skipTest( "not written" )

    def test_assignments_stored_correctly( self ):
        """Check that the students who have submitted the assignment
        (and none of the non-submitteers) have been paired up
        in the expected manner, and that the pairings have been stored
        """
        self.skipTest( "not written" )


class TestLateSubmissions( unittest.TestCase ):
    """Checks that works properly on subsequent runs after the
    initial assignments have been sent out

    """

    def test_run( self ):
        """Check that each student receives the expected message
        containing the correct student's submission
        todo
        """
        self.skipTest( "not written" )
