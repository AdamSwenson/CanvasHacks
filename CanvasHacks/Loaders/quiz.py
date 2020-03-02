"""
Created by adam on 2/24/20
"""
import pandas as pd

from CanvasHacks.Loaders.interfaces import IAllLoader, INewLoader
from CanvasHacks.Processors.quiz import process_work
from CanvasHacks.QuizReportFileTools import load_activity_data_from_files, retrieve_quiz_data, save_downloaded_report, \
    load_new

__author__ = 'adam'

if __name__ == '__main__':
    pass


class AllQuizReportFileLoader( IAllLoader ):
    """Loads all records for quiz"""

    @staticmethod
    def load( activity, course, **kwargs ):
        # course = self.course if course is None else course
        # activity_inviting_to_complete = self.activity_inviting_to_complete if activity_inviting_to_complete is None else activity_inviting_to_complete
        # pass
        return load_activity_data_from_files( activity, course )


class AllQuizReportDownloader( INewLoader ):

    @staticmethod
    def load( activity, course, save=True, **kwargs ):
        quiz = AllQuizReportDownloader.get_quiz( course, activity )
        student_work_frame = retrieve_quiz_data( quiz, **kwargs )

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
    def load( activity, course, **kwargs ):
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
        # quiz = AllQuizReportDownloader.get_quiz( course, activity_inviting_to_complete )
        # student_work_frame = retrieve_quiz_data( quiz )

        data = load_new( activity )
        NewQuizReportDownloadLoader._check_empty( data )
        return data


def load_student_work( csv_filepath, submissions ):
    """Loads and processes a csv file containing all student work for the unit
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
