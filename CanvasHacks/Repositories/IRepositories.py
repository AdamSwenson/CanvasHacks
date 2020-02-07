"""
Created by adam on 10/1/19
"""
__author__ = 'adam'

import pandas as pd
class IRepo(object):

    def download(self):
        raise NotImplementedError

    @property
    def student_ids( self ):
        if isinstance(self.data, dict):
            uids = [k for k in self.data.keys()]
        if isinstance(self.data, list):
            uids = [ k['student_id'] for k in self.data ]
        if isinstance(self.data, pd.DataFrame):
            try:
                uids = self.data.student_id.tolist()
            except KeyError:
                uids = self.data.reset_index()['student_id'].tolist()
        uids = list(set(uids))
        uids.sort()
        return uids


class StudentWorkRepo(object):
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


if __name__ == '__main__':
    pass