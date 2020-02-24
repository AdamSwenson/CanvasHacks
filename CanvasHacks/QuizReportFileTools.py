"""
Created by adam on 2/10/20
"""
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions
from CanvasHacks.Repositories.quizzes import WorkRepositoryFactory, \
    drop_columns_from_frame, WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.submissions import QuizSubmissionRepository
from CanvasHacks.TimeTools import getDateForMakingFileName

__author__ = 'adam'

import json
import time

import pandas as pd

from CanvasHacks.FileTools import makeDataFileIterator, create_folder
from CanvasHacks.RequestTools import *


# -------------------------- Getting the report file from server
def report_url_gen( starting_report_url ):
    """
    Returns the original url followed by copies with the report id incremented by 1
    starting_report_url: 'https://canvas.csun.edu/api/v1/courses/85210/quizzes/165098/reports/92640'
    """
    r = starting_report_url.split( '/' )
    url_stub = "/".join( r[ :-1 ] )
    rid = int( r[ -1: ][ 0 ] )

    while True:
        yield "{}/{}?include[]=progress&include[]=file".format( url_stub, rid )
        rid += 1


def parse_download_url( response ):
    """Takess a requests.response from get_report_download_url
    and tries to parse out the file download url.
    todo: set this up to poll for progress
    """
    c = json.loads( response.content )

    try:
        download_url = c[ 'file' ][ 'url' ]
        print( download_url )
        return download_url

    except KeyError:
        # todo Poll the progress url until have download url
        #         progress_url = c['progress_url']
        print( "Error: No download url provided \n", c )


def get_report_download_url( report_url ):
    """Uses the report url to get the url from which the csv file can be downloaded"""
    #     data = {"include": ["progress", "file"]}
    #     data = {"include": "file"}
    url = "{}?include[]=progress&include[]=file".format( report_url )
    data = { }

    try:
        # Make the request
        # We can't use the usual function since we don't want response.json()
        response = requests.get( report_url, headers=make_request_header() )

        print( 'response was ', response.status_code )
        response.raise_for_status()
        # todo or put check the progress url until workflow_state="completed"
        #         if response.progress.workflow_state != 'completed':

        # Continuing on since was successful
        return parse_download_url( response )

    except HTTPError as http_err:
        print( f'HTTP error occurred: {http_err}' )  # Python 3.6

    except Exception as err:
        print( f'Other error occurred: {err}' )  # Python 3.6


def download_report( download_url, save_file_path=None ):
    """Once we have the url to download the csv file, this
    will handle the download and load the data into a pandas
    dataframe
    """
    # Request the results file for assignment
    # Open it with pandas
    frame = pd.read_csv( download_url )

    if save_file_path:
        # Temporary location to store the downloaded file
        frame.to_csv( save_file_path )

    return frame


def retrieve_quiz_data( quiz, rest_timeout=60, max_id_attempts=20 ):
    """Returns a dataframe of the student report
    ACTUALLY WORKING VERSION!
    WILL ONLY WORK IF THE GENERATE REPORT BUTTON HAS BEEN MANUALLY CLICKED FIRST
    Returns:
        DataFrame

    """
    # This should request that the reports be generated
    reports = quiz.get_all_quiz_reports()

    print( "Resting for {} seconds while waiting for canvas to generate report".format( rest_timeout ) )
    time.sleep( rest_timeout )

    # The first report should be the student_analysis report. However,
    # for some reason, canvas will not return the file info with the
    # report we just created. However, it seems that the creation process
    # also created a report with a different id, which will contain the file info
    # At least in testing, this report id was 2 more than the student report
    # (the item_analysis report id was the student_analysis id + 1)
    # But will use a generator to cover more possibilities
    url_gen = report_url_gen( reports[ 0 ].url )

    for _ in range( 0, max_id_attempts ):
        # first value out of generator will be the original url
        url = next( url_gen )
        print( "trying: ", url )
        # We request the hidden report object which will have the url for downloading
        # and parse out the url
        download_url = get_report_download_url( url )
        # We load the url and parse into a dataframe
        if download_url:
            return download_report( download_url )


def save_downloaded_report( activity, frame ):
    """If we've downloaded the report programmatically, this
    saves it to the expected location
    """
    # save to file
    create_folder( activity.folder_path )
    try:
        # if there's a particular section
        fp = "{}/{}-student-work.csv".format( activity.folder_path, SECTION )
    except NameError:
        fp = "{}/{}-{}-student-work.csv".format( activity.folder_path, getDateForMakingFileName(), activity.safe_name )

    try:
        frame.to_csv( fp )
    except Exception as e:
        print( "Error saving student work to file ", e )


# -------------------------- Handle stuff stored in a file on disk
def get_newest_data( activity ):
    # get data from newest file
    fiter = makeDataFileIterator( activity.folder_path )
    report_frames = [ ]
    try:
        while True:
            f = next( fiter )
            # print( "loading: ", f )
            frame = pd.read_csv( f )
            frame.submitted = pd.to_datetime( frame.submitted )
            if 'student_id' not in frame.index:
                frame.rename( { 'id': 'student_id' }, axis=1, inplace=True )
            # this makes it freak out for some reason
            #         frame.set_index('student_id', inplace=True)
            report_frames.append( frame )
    except StopIteration:
        return sort_frames_by_age( report_frames )[ 0 ]


def sort_frames_by_age( quiz_report_frames ):
    """Sorts the list of frames so that the newest
    is first, the oldest is last"""
    # assumes submitted is a datetime
    quiz_report_frames.sort( key=lambda x: x.submitted.max(), reverse=True )
    return quiz_report_frames


def get_whats_new( quiz_report_frames ):
    """Given a list of quiz report dataframes, returns a dataframe
    of the things that are new since the last time the data was checked
    """
    if len( quiz_report_frames ) == 1:
        return quiz_report_frames[ 0 ]
    sort_frames_by_age( quiz_report_frames )
    latest = quiz_report_frames[ 0 ]
    previous = quiz_report_frames[ 1 ]
    # Anything which happened after the last check of the data
    return latest[ latest.submitted > previous.submitted.max() ]


def load_new( activity ):
    """Returns a dataframe containing everything that is new in the most
    recent file since the next most recent file.

    NB, this is not equivalent to all the records which have not been
    acted upon since it is possible that no action was taken on the
    records in the next most recent file."""
    fiter = makeDataFileIterator( activity.folder_path )
    report_frames = [ ]
    try:
        while True:
            f = next( fiter )
            print( "loading: ", f )
            frame = pd.read_csv( f )
            frame.submitted = pd.to_datetime( frame.submitted )
            if 'student_id' not in frame.index:
                frame.rename( { 'id': 'student_id' }, axis=1, inplace=True )
            # this makes it freak out for some reason
            #         frame.set_index('student_id', inplace=True)
            report_frames.append( frame )
    except StopIteration:
        newstuff = get_whats_new( report_frames )
        print( "{} new records since previous file".format( len( newstuff ) ) )
        if len( newstuff ) == 0:
            raise NoNewSubmissions

        return newstuff


def make_quiz_repo( course, activity, save=True ):
    """Gets all student work data for the activity that's part of the assignment
    loads it into a QuizRepository or ReviewRepository and
    returns the repository.
    This is the main method called to get data
    """
    # Get quiz submission objects
    repo = WorkRepositoryFactory.make( activity, course )
    # if isinstance(activity, Review):
    #     repo = ReviewRepository(activity, course)
    # else:
    #     repo = QuizRepository(activity, course)

    # Download student work
    # This will work if the 'Create Report' button has been manually clicked
    student_work_frame = retrieve_quiz_data( repo.quiz )

    if save:
        # Want to have all the reports be formatted the same
        # regardless of whether we manually or programmatically
        # downloaded them. Thus we save before doing anything to them.
        save_downloaded_report( activity, student_work_frame )

    # Download submissions
    subRepo = QuizSubmissionRepository( repo.quiz )

    # Doing the combination with submissions after saving to avoid
    # mismatches of new and old data
    repo._process( student_work_frame, subRepo.frame )

    return repo


def load_activity_data_from_files( activity, course ):
    """Get complete set of data for activity from a bunch of
    potentially inconsistent files.
    Created in CAN-41
    Loads the data into a repository object of the appropriate type
    """
    fiter = makeDataFileIterator( activity.folder_path )
    frames = [ ]
    try:
        while True:
            f = next( fiter )
            print( "loading: ", f )
            f = pd.read_csv( f )
            if 'student_id' not in f.columns:
                f.rename( { 'id': 'student_id' }, axis=1, inplace=True )
            frames.append( f )
    except StopIteration:
        print( "Loaded data from {} files".format( len( frames ) ) )

        data = pd.concat( frames, sort=True )
        print( "Loaded {} rows from all files in folder".format( len( f ) ) )

        if 'score_x' in data.columns:
            # this shouldn't be necessary in future.
            # Only when were saving sheet plus submissions
            def fix_score( row ):
                return row[ [ 'score', 'score_x', 'score_y' ] ].mean()

            data.score = data.apply( lambda x: fix_score( x ), axis=1 )
            data.drop( [ 'score_x', 'score_y' ], axis=1, inplace=True )

        repo = WorkRepositoryFactory.make( activity, course )
        repo.set_question_columns( data )
        drop_columns_from_frame( data )

        data.drop_duplicates( inplace=True )
        repo.data = data
        print( "{} rows loaded to repo.data after processing".format( len( repo.data ) ) )
        return repo


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

    # def __init__( self, course, activity ):
    #     self.course = course
    #     self.activity = activity

    @staticmethod
    def load( activity, course=None, **kwargs ):
        # course = self.course if course is None else course
        # activity = self.activity if activity is None else activity

        return load_activity_data_from_files( activity, course )


class AllQuizReportDownloader( INewLoader ):

    @staticmethod
    def load( activity, course=None, save=True, **kwargs ):
        student_work_frame = retrieve_quiz_data( activity )

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

    # def __init__( self, course, activity ):
    #     self.course = course
    #     self.activity = activity

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

    # def __init__( self, course, activity ):
    #     self.course = course
    #     self.activity = activity

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


if __name__ == '__main__':
    pass
