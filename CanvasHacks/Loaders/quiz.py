"""
Created by adam on 2/24/20
"""
import pandas as pd

from CanvasHacks.Errors.data_ingestion import NoNewSubmissions, NoStudentWorkDataLoaded, NoWorkDownloaded
from CanvasHacks.Files.FileTools import create_folder
from CanvasHacks.Loaders.interfaces import IAllLoader, INewLoader
from CanvasHacks.Processors.quiz import process_work
from CanvasHacks.Files.QuizReportFileTools import load_activity_data_from_files, load_activity_from_newest_file, load_new,\
    retrieve_quiz_data, save_downloaded_report

__author__ = 'adam'

if __name__ == '__main__':
    pass


# =================================== file

class AllQuizReportFileLoader( IAllLoader ):
    """Loads all records for quiz"""
    failure_message = "Could not load data from file"

    @staticmethod
    def load( activity, course, **kwargs ):
        # course = self.course if course is None else course
        # activity_inviting_to_complete = self.activity_inviting_to_complete if activity_inviting_to_complete is None else activity_inviting_to_complete
        # pass
        student_work_frame = load_activity_data_from_files( activity, course )
        AllQuizReportFileLoader._check_empty( student_work_frame )
        return student_work_frame


class QuizReportFileLoader( IAllLoader ):
    """
    New standard fileloader
    """

    @staticmethod
    def load( activity, course, **kwargs ):
        student_work_frame = load_activity_from_newest_file( activity )
        QuizReportFileLoader._check_empty( student_work_frame )
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


# ========================= download
class AllQuizReportDownloader( INewLoader ):
    failure_message = "Could not download data."

    @staticmethod
    def load( activity, course, save=True, **kwargs ):
        quiz = AllQuizReportDownloader.get_quiz( course, activity )
        # This will return none if never able to download from a url
        student_work_frame = retrieve_quiz_data( quiz, **kwargs )

        if student_work_frame is None:
            print( 'uhoh' )
            raise NoWorkDownloaded

        if save:
            # Want to have all the reports be formatted the same
            # regardless of whether we manually or programmatically
            # downloaded them. Thus we save before doing anything to them.
            save_downloaded_report( activity, student_work_frame )

        return student_work_frame


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


class QuizComboLoader( IAllLoader ):
    """
    Attempts to load first by downloading and then falls
    back to loading from a file.
    """

    @staticmethod
    def load( activity, course, save=True, **kwargs ):
        loaders = (AllQuizReportDownloader, QuizReportFileLoader) # AllQuizReportFileLoader)
        for loader in loaders:
            try:
                # The loader should raise the error or return the
                # desired value
                return loader.load( activity, course, save=save, **kwargs )
            except NoWorkDownloaded as e:
                # We ignore so next object will try
                print( e.message )

                # We attempt to create the folder that the file loader will
                # look in because, otherwise, we won't have a handy location
                # to put the downloaded file in the future. (Before, it accidentally happened
                # when we tried to save None instead of a dataframe. That was fixed
                # so now we need to do it explicitly).
                create_folder( activity.folder_path )

            except NoNewSubmissions:
                # We're done, but this may have special handling
                # so we re-raise it
                raise NoNewSubmissions

        # if we made it all the way here, all attempts at loading have failed
        # so we raise this to tell the program to move on
        raise NoStudentWorkDataLoaded


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
