"""
Created by adam on 10/1/19
"""
__author__ = 'adam'

import pandas as pd

from CanvasHacks.Models.model import StoreMixin


class IRepo( StoreMixin ):
    """Parent class for all repositories.
    All will store data in the data attribute,
    but this does not constrain how the data is stored.
    Some use a dataframe, others use a dictionary
    """

    def download( self ):
        raise NotImplementedError

    @property
    def student_ids( self ):
        if isinstance( self.data, dict ):
            uids = [ k for k in self.data.keys() ]
        if isinstance( self.data, list ):
            uids = [ k[ 'student_id' ] for k in self.data ]
        if isinstance( self.data, pd.DataFrame ):
            try:
                uids = self.data.student_id.tolist()
            except KeyError:
                uids = self.data.reset_index()[ 'student_id' ].tolist()
        uids = list( set( uids ) )
        uids.sort()
        return uids


class StudentWorkRepo( IRepo ):
    """Parent class for any repository which holds
    student data and can provide a formatted version
    for sending via email etc
    """

    def get_formatted_work( self, student_id ):
        raise NotImplementedError

    def _check_empty( self, work ):
        """Checks whether the work is empty and
        returns the appropriate text to use
        """
        # Handle empty
        if work is None:
            return "THIS STUDENT SUBMISSION WAS BLANK. PLEASE GRADE ACCORDINGLY"
        return work

    # def store_results( self, results_list ):
    #     raise NotImplementedError


class ContentRepository:
    """Defines methods of repositories which
    return the content of student work
    """

    def get_formatted_work_by( self, student_id ):
        raise NotImplementedError


if __name__ == '__main__':
    pass


class SelectableMixin:
    """Allows to store a list of column names
    that have been specially designated by the user
    """

    def _init_selected( self ):
        try:
            if len( self.selected ) > 0:
                pass
        except Exception as e:
            print( e )
            self.selected = [ ]

    def select( self, identifier, name=None ):
        self._init_selected()
        self.selected.append( identifier )

    def deselect( self, identifier ):
        self.selected.pop( self.selected.index( identifier ) )

    def get_selections( self ):
        self._init_selected()
        return self.selected

    def reset_selections( self ):
        self.selected = [ ]