import unittest
from unittest.mock import create_autospec, MagicMock

from CanvasHacks.Processors.filters import SubmissionReadinessFilter, FrameRowReadinessFilter, ReadinessFilterFactory,\
    QuizSubmissionReadinessFilter, UncheckableDataProvidedError
from canvasapi.quiz import QuizSubmission
from canvasapi.submission import Submission
import pandas as pd

from unittest import TestCase

from TestingBase import TestingBase
if __name__ == '__main__':
    pass


class TestSubmissionReadinessFilter(TestingBase):

    def setUp(self):
        self.config_for_test()
        self.obj = SubmissionReadinessFilter()

    def test_is_ready( self ):
        t = MagicMock(grade='complete')
        self.assertFalse(self.obj.is_ready(t), "returns false when grade is complete")

        t = MagicMock(workflow_state='complete')
        self.assertFalse(self.obj.is_ready(t), "returns false when workflow state is unsubmitted")

        t = MagicMock(workflow_state='pending_review')
        self.assertTrue(self.obj.is_ready(t), "returns true when workflow state is pending_review")

    def test_make_raises_on_unknown( self ):
        with self.assertRaises(UncheckableDataProvidedError):
            t = create_autospec( Submission )
            self.obj.is_ready(t)



class TestFrameRowReadinessFilter( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.obj = FrameRowReadinessFilter()

    def test_is_ready( self ):
        self.skipTest( 'todo' )



class TestQuizSubmissionReadinessFilter( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        self.obj = QuizSubmissionReadinessFilter()

    def test_is_ready( self ):
        t = create_autospec(QuizSubmission)
        self.skipTest( 'todo' )


class TestReadinessFilterFactory( TestingBase ):

    def setUp( self ):
        self.config_for_test()
        ReadinessFilterFactory()

    def test_make( self ):
        i = pd.Series()
        f = ReadinessFilterFactory.make(i)
        self.assertIsInstance(f, FrameRowReadinessFilter, "works for FrameRowReadinessFilter")

        i = create_autospec(Submission)
        f = ReadinessFilterFactory.make(i)
        self.assertIsInstance(f, SubmissionReadinessFilter, "works for SubmissionReadinessFilter")

        i = create_autospec(QuizSubmission)
        f = ReadinessFilterFactory.make( i )
        self.assertIsInstance( f, QuizSubmissionReadinessFilter, "works for QuizSubmissionReadinessFilter" )

    def test_make_raises_on_unknown( self ):
        with self.assertRaises(UncheckableDataProvidedError): #,  "raises when given string" ):
            f = ReadinessFilterFactory.make( "taco" )


if __name__ == '__main__':
    unittest.main()
