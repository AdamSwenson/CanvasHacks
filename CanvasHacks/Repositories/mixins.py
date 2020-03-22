"""
Created by adam on 2/26/20
"""
__author__ = 'adam'

import pandas as pd
from canvasapi.quiz import QuizSubmission
from canvasapi.submission import Submission

if __name__ == '__main__':
    pass


class FrameStorageMixin:
    """
    Tools for use by repositories for which
    self.data is a dataframe of student records
    """

    def remove_student_records( self, student_ids ):
        student_ids = student_ids if isinstance( student_ids, list ) else [ student_ids ]
        if len( student_ids ) == 0:
            # bail if there were no students. That way we can run
            # this on first time
            return True

        is_index = False
        prelen = len( self.data )
        # figure out whether student_id is the index
        if 'student_id' not in self.data.columns:
            self.data.reset_index( inplace=True )
            is_index = True
        self.data = self.data[ ~self.data.student_id.isin( student_ids ) ].copy( deep=True )

        removed = prelen - len( self.data )
        if removed > 0:
            print( "Removed {} records".format( removed ) )

        if is_index:
            self.data.set_index( 'student_id', inplace=True )


class ObjectHandlerMixin:
    """Tools for dealing with
    input values which may represent students
    and other objects in a number of ways
    """

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

    def force_to_ids( self, list_of_students ):
        """We could receive a list of ids, Student
        objects or canvasapi User objects. This returns
        a list of ids"""
        out = [ ]

        for s in list_of_students:
            if isinstance( s, int ):
                out.append( s )
            else:
                # Both Student and User objects will have an id attribute
                # which contains the canvas id of the student
                out.append( s.id )
        return out


class TimeHandlerMixin:
    """Tools for classes which need to
    handle datetimes
    """

    def _force_timestamp( self, val ):
        """
        Forces the val to be a pandas timestamp
        :param val: string or timestamp
        :return: pd.Timestamp
        """
        if not isinstance( val, pd.Timestamp ):
            return pd.to_datetime( val )
        return val

    def _force_timedelta( self, val ):
        """
        Forces the provided value to be a timedelta
        :param val: string or pd.Timedelta
        :return: pd.Timedelta
        """
        if not isinstance( val, pd.Timedelta ):
            return pd.to_timedelta( val )


class StudentWorkMixin( ObjectHandlerMixin ):
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

