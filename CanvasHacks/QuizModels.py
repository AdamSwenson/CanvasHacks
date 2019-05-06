"""
Created by adam on 5/6/19
"""
__author__ = 'adam'

from CanvasHacks import environment as env
import pandas as pd

class QuizData(object):
    """Holds the relevant info for a quiz type assignment"""

    def __init__(self, **kwargs):
        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])
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
        return self.due_at

    @property
    def quarter_credit_date(self):
        return self._quarter_credit_date

    @quarter_credit_date.setter
    def quarter_credit_date(self, date):
        self._quarter_credit_date = pd.to_datetime(date)

    @property
    def folder_path(self):
        return "{}/{}".format(env.ARCHIVE_FOLDER, self.name)

    @property
    def lock_date(self):
        return self.lock_at

    @property
    def max_score(self):
        return self.points_possible

    @property
    def name(self):
        return self.title

    def set_question_columns(self, results_frame):
        """Finds the question columns in a results frame
        and stores them in a list of tuples
        with the form (question id, string column name)
        """
        questions = self._detect_question_columns(results_frame.columns)
        self.question_columns = [(q.split(':')[0], q) for q in questions ]

    def _detect_question_columns(self, columns):
        """Return a list of columns which contain a colon,
        those probably contain the question answers
        """
        return [c for c in columns if len(c.split(':')) > 1]



if __name__ == '__main__':
    pass