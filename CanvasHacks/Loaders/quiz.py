"""
Created by adam on 2/24/20
"""
import pandas as pd

from CanvasHacks.Loaders.ILoaders import IAllLoader, INewLoader
from CanvasHacks.Processors.quiz import process_work
from CanvasHacks.QuizReportFileTools import load_activity_data_from_files, retrieve_quiz_data, save_downloaded_report, \
    load_new

__author__ = 'adam'

if __name__ == '__main__':
    pass


class LoaderFactory:
    """Decides which loader to use"""

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


class AllQuizReportFileLoader( IAllLoader ):
    """Loads all records for quiz"""

    @staticmethod
    def load( activity, course=None, **kwargs ):
        # course = self.course if course is None else course
        # activity = self.activity if activity is None else activity
        # pass
        return load_activity_data_from_files( activity, course )


class AllQuizReportDownloader( INewLoader ):

    @staticmethod
    def load( activity, course, save=True, **kwargs ):
        quiz = AllQuizReportDownloader.get_quiz( course, activity )
        student_work_frame = retrieve_quiz_data( quiz )

        if save:
            # Want to have all the reports be formatted the same
            # regardless of whether we manually or programmatically
            # downloaded them. Thus we save before doing anything to them.
            save_downloaded_report( activity, student_work_frame )

        return student_work_frame


class NewQuizReportFileLoader( INewLoader ):
    """
    Loads latest data from files

    todo
    """

    @staticmethod
    def load( activity, course=None, **kwargs ):
        """
        Returns all new records
        :param course:
        :param activity:
        :return: DataFrame
        :raises: NoNewSubmissions
        """
        data = load_new( activity )
        NewQuizReportFileLoader._check_empty( data )
        return data


class NewQuizReportDownloadLoader( INewLoader ):
    """
    Downloads latest report and returns what's new without
    storing report

    todo
    """

    @staticmethod
    def load( activity, course=None, **kwargs ):
        """
        Returns all new records
        :param course:
        :param activity:
        :return: DataFrame
        :raises: NoNewSubmissions
        """
        data = load_new( activity )
        NewQuizReportDownloadLoader._check_empty( data )
        return data


def load_student_work( csv_filepath, submissions ):
    """Loads and processes a csv file containing all student work for the assignment
    submissions: DataFrame containing student submission objects
    NB, process_work has been refactored out in CAN-11 but load_student_work
    is still here for legacy uses
    """
    f = pd.read_csv( csv_filepath )
    return process_work( f, submissions )
    # # rename id so will be able to join
    # f.rename( { 'id': 'student_id' }, axis=1, inplace=True )
    # # merge it with matching rows from the submissions frame
    # f = pd.merge( f, submissions, how='left', on=[ 'student_id', 'attempt' ] )
    # f.set_index( 'name', inplace=True )
    # f.sort_index( inplace=True )
    # return f
