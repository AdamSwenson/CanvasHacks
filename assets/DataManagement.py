"""
Created by adam on 2/1/19
"""
from typing import List, Any

__author__ = 'adam'


class DataStore(object):
    """All downloaded and score data gets stored in this object
    Methods using the data will expect an instance.
    """
    credit: List[ int ]

    def __init__(self, assignment_id=None,  assignment_name=None, course_id=None):
        self.course_id = course_id
        self.assignment_name = assignment_name
        self.assignment_id = assignment_id
        # List of ids from students receiving credit
        self.credit = []
        self.no_credit = []
        self.submissions = []

    def print_counts( self ):
        m = "Tentatively assigning credit to {} submissions; no credit to {} submissions."
        print(m.format(len(self.credit), len(self.no_credit)))

    # @property
    # def ids_receiving_credit( self):
    #     # if assignment_id is not None:
    #     #     c = list(filter(lambda x: x['assignment'] == assignment_id, self.credit))[0]
    #     #     return c['ids']
    #     return self.credit[0].ids


if __name__ == '__main__':
    pass