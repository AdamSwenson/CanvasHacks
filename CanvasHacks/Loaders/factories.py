"""
Created by adam on 2/26/20
"""
__author__ = 'adam'

from CanvasHacks.Loaders.assignment import AssignmentDownloadLoader
from CanvasHacks.Loaders.interfaces import ILoaderFactory
from CanvasHacks.Loaders.quiz import AllQuizReportDownloader, AllQuizReportFileLoader, NewQuizReportDownloadLoader, \
    NewQuizReportFileLoader

if __name__ == '__main__':
    pass


class LoaderFactory( ILoaderFactory ):
    """Decides which loader to use
    Makes the initial determination on whether is_non_quiz is set
    as an arg
    """

    @staticmethod
    def make( *args, **kwargs ):
        """
        Should use kwarg is_non_quiz=True if want
        an AssignmentLoader (for non-quizzes)
        :param args:
        :param kwargs:
        :return:
        """
        try:
            if kwargs[ 'is_quiz' ]:
                return QuizLoaderFactory.make( *args, **kwargs )
            # If key is set and false
            return AssignmentLoaderFactory.make( *args, **kwargs )

        except KeyError:
            # This is the default since most things use quizzes
            return QuizLoaderFactory.make( *args, **kwargs )


class AssignmentLoaderFactory( ILoaderFactory ):
    """Decides which loader to use for a non-quiz unit"""

    @staticmethod
    def make( **kwargs ):
        return AssignmentDownloadLoader


class QuizLoaderFactory( ILoaderFactory ):
    """
    Decides which form of quiz loader to use
    """

    @staticmethod
    def make( download=True, only_new=False, **kwargs ):
        if download and only_new:
            return NewQuizReportDownloadLoader

        if download:
            return AllQuizReportDownloader

        # We're just to load from file
        if only_new and only_new:
            return NewQuizReportFileLoader

        return AllQuizReportFileLoader
