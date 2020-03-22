"""
Created by adam on 2/26/20
"""
__author__ = 'adam'

from tests.TestingBase import TestingBase

from faker import Faker

fake = Faker()


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