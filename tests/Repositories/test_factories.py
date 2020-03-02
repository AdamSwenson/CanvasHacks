"""
Created by adam on 2/26/20
"""
__author__ = 'adam'

import unittest
from unittest.mock import MagicMock, patch
from tests.TestingBase import TestingBase

from faker import Faker

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Models.status_record import StatusRecord
from CanvasHacks.PeerReviewed.Definitions import Unit
from CanvasHacks.Repositories.status import ComplexStatusRepository, StatusRepository
from tests.factories.ModelFactories import student_factory
from tests.factories.PeerReviewedFactories import activity_data_factory, unit_factory
fake = Faker()

from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory, WorkRepositoryFactory
import pandas as pd

class TestWorkRepositoryLoaderFactory( TestingBase ):

    def setUp(self):
        self.config_for_test()

    def test_make( self ):
        self.skipTest('todo')

    def test__for_assignment_type_activity( self ):

        self.skipTest('todo')
    #
    # @patch('CanvasHacks.Repositories.factories.WorkRepositoryLoaderFactory.QuizSubmissionRepository')
    def test__for_quiz_type_activity( self ):
        self.skipTest( 'todo' )

        # loader = MagicMock(return_value=pd.DataFrame())
        # WorkRepositoryLoaderFactory
        # subRepoMock.frame = pd.DataFrame()
        #
        # # check
        # subRepoMock.frame.assert_called()



class TestWorkRepositoryFactory( TestingBase ):

    def setUp( self ):
        self.config_for_test()

    def test_make( self ):
        self.skipTest('todo')


if __name__ == '__main__':
    pass