"""
Created by adam on 2/26/20
"""
__author__ = 'adam'

import pandas as pd

if __name__ == '__main__':
    pass


class StudentWorkMixin:
    """Parent class for any repository which holds
    student data and can provide a formatted version
    for sending via email etc
    """
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

    def _handle_id( self, object_or_int ):
        """
        Takes either a object or the int value of their id
        and returns the id
        :param object_or_int:
        :return: int
        """
        try:
            return int( object_or_int )
        except TypeError:
            try:
                # in case we have a student object w id stored like this
                return object_or_int.student_id
            except AttributeError:
                return object_or_int.id

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