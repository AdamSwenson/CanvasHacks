"""
Created by adam on 5/6/19
"""
__author__ = 'adam'

from CanvasHacks import environment as env
import pandas as pd
from CanvasHacks.Models.model import Model

class StoredDataFileMixin:
    """Standard methods for accessing data stored in files"""

    @property
    def safe_name( self ):
        """Returns a name that won't f up the file path"""
        return "".join([n for n in self.name if n != ':'])

    @property
    def folder_path(self):
        # ssafename = "".join([n for n in self.name if n != ':'])
        return "{}/{}-{}".format(env.ARCHIVE_FOLDER, self.course_id, self.safe_name)


class QuizDataMixin:
    """ Methods for handling data downloaded for quiz type assignments """
    #
    # @property
    # def safe_name( self ):
    #     """Returns a name that won't f up the file path"""
    #     return "".join([n for n in self.name if n != ':'])
    #
    # @property
    # def folder_path(self):
    #     # ssafename = "".join([n for n in self.name if n != ':'])
    #     return "{}/{}-{}".format(env.ARCHIVE_FOLDER, self.course_id, self.safe_name)

    def set_question_columns(self, results_frame):
        """Finds the question columns in a results frame
        and stores them in a list of tuples
        with the form (question id, string column name)
        """
        questions = self._detect_question_columns(results_frame.columns)
        self.question_columns = [(q.split(':')[0], q) for q in questions]
        # weird stuff we need to filter
        bad = ['Unnamed']
        self.question_columns = [(a[0], a[1] ) for a in self.question_columns if a[0].strip() not in bad ]

    def _detect_question_columns(self, columns):
        """Return a list of columns which contain a colon,
        those probably contain the question answers
        """
        return [c for c in columns if len(c.split(':')) > 1]

    @staticmethod
    def _check_date( date ):
        """Checks that a value is a pd.Timestamp
        if not, it tries to make it into one"""
        return date if isinstance( date, pd.Timestamp ) else pd.to_datetime( date )

    @property
    def keep_columns( self ):
        """Returns a list of report column names which
        should not be dropped from the frame"""
        cols = [c[1] for c in self.question_columns]
        cols += env.REPORT_KEEP_COLUMNS
        return cols


class QuizData(Model, QuizDataMixin):
    """Holds the data which defines the properties of a
    canvas quiz type unit
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.handle_kwargs(kwargs)
        # for k in kwargs.keys():
        #     self.__setattr__(k, kwargs[k])
        self.question_columns = []

    @property
    def course_id(self):
        for a in self.html_url.split('/'):
            try:
                return int(a)
            except:
                pass

    @property
    def due_date(self):
        return type( self )._check_date(self.due_at)

    @property
    def open_date( self ):
        return type( self )._check_date(self.open_at)

    @property
    def quarter_credit_date(self):
        return self._quarter_credit_date

    @quarter_credit_date.setter
    def quarter_credit_date(self, date):
        self._quarter_credit_date = pd.to_datetime(date)
    #
    # @property
    # def folder_path(self):
    #     return "{}/{}-{}".format(env.ARCHIVE_FOLDER, self.course_id, self.name)

    @property
    def lock_date(self):
        return type( self )._check_date(self.lock_at)

    @property
    def max_score(self):
        return self.points_possible

    @property
    def name(self):
        return self.title

    # def set_question_columns(self, results_frame):
    #     """Finds the question columns in a results frame
    #     and stores them in a list of tuples
    #     with the form (question id, string column name)
    #     """
    #     questions = self._detect_question_columns(results_frame.columns)
    #     self.question_columns = [(q.split(':')[0], q) for q in questions ]
    #
    # def _detect_question_columns(self, columns):
    #     """Return a list of columns which contain a colon,
    #     those probably contain the question answers
    #     """
    #     return [c for c in columns if len(c.split(':')) > 1]
    #
    # @staticmethod
    # def _check_date( date ):
    #     """Checks that a value is a pd.Timestamp
    #     if not, it tries to make it into one"""
    #     return date if isinstance( date, pd.Timestamp ) else pd.to_datetime( date )



if __name__ == '__main__':
    pass