"""
Created by adam on 10/1/19
"""
__author__ = 'adam'

from CanvasHacks.Models.model import StoreMixin


class IRepo( StoreMixin ):
    """Parent class for all repositories.
    All will store data in the data attribute,
    but this does not constrain how the data is stored.
    Some use a dataframe, others use a dictionary
    """
    pass


class IDownloadingRepo:
    """Repositories which download stuff"""

    def download( self ):
        raise NotImplementedError


class IContentRepository( IRepo ):
    """Defines methods of repositories which
    return the content of student work
    """


    def get_formatted_work_by( self, student_id ):
        raise NotImplementedError


class ISubmissionRepo( IRepo, IDownloadingRepo ):

    def download( self ):
        raise NotImplementedError

    @property
    def frame( self ):
        raise NotImplementedError

    def get_by_student_id( self, student_id ):
        raise NotImplementedError


if __name__ == '__main__':
    pass