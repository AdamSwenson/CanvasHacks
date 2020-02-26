"""
Created by adam on 2/24/20
"""
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions

__author__ = 'adam'

if __name__ == '__main__':
    pass

class ILoader:

    @staticmethod
    def get_quiz( course, activity ):
        """Returns the canvasapi.quiz.Quiz object associated
        with this repository.
        """
        return course.get_quiz( activity.quiz_id )

    @staticmethod
    def load( activity, course=None, **kwargs ):
        raise NotImplementedError


class INewLoader(ILoader):
    """Interface for any class which ingests data and returns
    what hasn't been acted upon yet
    """

    @staticmethod
    def _check_empty( data ):
        """
        Should be called on what's been loaded before returning
        it.
        :raises NoNewSubmissions
        """
        if len( data ) == 0:
            raise NoNewSubmissions


class IAllLoader(ILoader):
    """Interface for any class which loads all existing
    data for the quiz"""
    pass
    # @staticmethod
    # def load( activity, course=None, **kwargs ):
    #     raise NotImplementedError