"""
Assigns a randomly selected reviewer and sends them the work

"""
import unittest

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from tests.TestingBase import TestingBase

from CanvasHacks.SkaaSteps.SendInitialWorkToReviewer import SendInitialWorkToReviewer


class TestOnTimeSubmissions(TestingBase ):
    """Checks that works properly on first run after
    deadline on work that has been submitted
    """

    def setUp(self):
        self.config_for_test()
        self.dao = SqliteDAO()

    def test_sends_correctly( self ):
        """Check that each student receives the expected message
        containing the correct student's submission
        """
        # Load initial content assignment data

        # create review assignments

        # send


        self.fail()


    def test_assignments_stored_correctly( self ):
        """Check that the students who have submitted the assignment
        (and none of the non-submitteers) have been paired up
        in the expected manner, and that the pairings have been stored
        """
        self.fail()


class TestLateSubmissions( TestingBase ):
    """Checks that works properly on subsequent runs after the
    initial assignments have been sent out

    """

    def test_sends_correctly( self ):
        """Check that each student receives the expected message
        containing the correct student's submission
        """
        self.fail()

    def test_review_pairings_made_correctly( self ):
        """Check that the students who have submitted the assignment
        (and none of the non-submitteers) have been paired up
        in the expected manner, and that the pairings have been stored
        """
        self.fail()

    def test_original_review_pairings_are_unaffected( self ):
        """Check that the review assignments which were created
        on the earlier run(s) have not been altered when the
        new review assignments were made
        """
        self.fail()


if __name__ == '__main__':
    unittest.main()
