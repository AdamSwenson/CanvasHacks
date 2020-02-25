"""
Created by adam on 2/24/20
"""
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions

__author__ = 'adam'

if __name__ == '__main__':
    pass


class INewLoader:
    """Interface for any class which ingests data and returns
    what hasn't been acted upon yet
    """

    @staticmethod
    def load( activity, course=None, **kwargs ):
        raise NotImplementedError

    @staticmethod
    def _check_empty( data ):
        """
        Should be called on what's been loaded before returning
        it.
        :raises NoNewSubmissions
        """
        if len( data ) == 0:
            raise NoNewSubmissions


class IAllLoader:
    """Interface for any class which loads all existing
    data for the quiz"""

    @staticmethod
    def load( activity, course=None, **kwargs ):
        raise NotImplementedError