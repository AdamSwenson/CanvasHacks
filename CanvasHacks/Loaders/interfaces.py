"""
Created by adam on 2/24/20
"""
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions

__author__ = 'adam'

if __name__ == '__main__':
    pass


class ILoaderFactory:

    @staticmethod
    def make( **kwargs ):
        raise NotImplementedError


class ILoader:
    """
    Defines interfaces for objects which load student
    data and return it as a dataframe.

    These shouldn't modify the data. That's the job of a
    repository.
    """

    @staticmethod
    def get_quiz( course, activity ):
        """Returns the canvasapi.quiz.Quiz object associated
        with this repository.
        """
        return course.get_quiz( activity.quiz_id )

    @staticmethod
    def get_assignment(course, activity):
        """If doesn't use quiz report, we need the activity_inviting_to_complete"""
        return course.get_assignment(activity.id)

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

    @staticmethod
    def _check_empty( data ):
        """
        Should be called on what's been loaded before returning
        it.
        :raises NoNewSubmissions
        """
        if len( data ) == 0:
            raise NoNewSubmissions

    # @staticmethod
    # def load( activity_inviting_to_complete, course=None, **kwargs ):
    #     raise NotImplementedError