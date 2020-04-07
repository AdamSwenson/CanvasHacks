"""
Created by adam on 2/1/19
"""
from typing import List
# from AdamTools.Text.TextProcessingTools import WordFreq
from CanvasHacks.Text.stats import WordFreq

__author__ = 'adam'


class DataStoreNew(object):
    """All downloaded and score data gets stored in this object
    Methods using the data will expect an instance.
    New as of CAN-24
    """
    credit: List[ int ]

    def __init__(self, activity):
        self.activity = activity
        self.course_id = activity.course_id
        self.assignment_name = activity.name
        self.assignment_id = activity.id
        # New (can-24) thing to hold the scores
        # should contain tuples (submission, pct credit)
        self.results = []

    def assign_student_no_credit( self, student_id ):
        """
        Update a record to give the student no credit
        :param student_id:
        :return:
        """
        idx = [ idx for idx, v in enumerate( self.results ) if v[ 0 ].user_id == student_id ][ 0 ]
        old = self.results.pop( idx )
        new = (old[ 0 ], None)
        self.results.append(new)


    def assign_student_credit( self, student_id ):
        """
        Updates student to receive 100 credit. NB, will lose any penalty
        :param student_id:
        :return:
        """
        idx = [ idx for idx, v in enumerate( self.results ) if v[ 0 ].user_id == student_id ][ 0 ]
        old = self.results.pop( idx )
        new = (old[ 0 ], 100)
        self.results.append( new )

    @property
    def credit( self ):
        """Alias so can use interfaces for old version"""
        return [r.user_id for r, score in self.results if score is not None and score > 0]

    @property
    def submissions( self ):
        """Alias so can use interfaces for old version"""
        r = [s[0].attributes for s in self.results]
        for s in r:
            s['student_id'] = s['user_id']
        return r


    def print_counts( self ):
        m = "Tentatively assigning credit to {} submissions; no credit to {} submissions."
        print(m.format(len(self.credit), len(self.no_credit)))


class DataStore(object):
    """All downloaded and score data gets stored in this object
    Methods using the data will expect an instance.
    """
    credit: List[ int ]

    def __init__(self, assignment_id=None,  assignment_name=None, course_id=None):
        self.course_id = course_id
        self.assignment_name = assignment_name
        self.assignment_id = assignment_id
        # New (can-24) thing to hold the scores
        # should contain tuples (submission, pct credit)
        self.scores = []
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
    #     #     c = list(filter(lambda x: x['unit'] == assignment_id, self.credit))[0]
    #     #     return c['ids']
    #     return self.credit[0].ids


class BagStore(object):

    def __init__(self):
        # Preserves the distinct submissions from students
        self.assignment_bags = {}
        # Holds 1 bag per unit containing the contents of
        # all student bags
        self.assignment_words = {}

    @property
    def assignment_names(self):
        return [name for name in self.assignment_bags.keys()]

    @property
    def unique_words(self):
        return list(set(self.all_words))

    @property
    def all_bags(self):
        """Returns a list containing lists of words
        Each of the word list is a student's submission,
        but all the assignments are combined
        """
        return []

    @property
    def all_words(self):
        """Returns a list of all the words
        submitted on all the assignments."""
        a = []
        for name in self.assignment_bags.keys():
            for bag in self.assignment_bags[name]:
                a += bag
        return a

    def add_assignment_bags(self, name, bags):
        """bags is a list of lists. Each list should
        contain words from 1 student's submission on the unit"""
        self.assignment_bags[name] = bags
        self.assignment_words[name] = []
        for b in bags:
            self.assignment_words[name] += [w for w in b]

    def get_assignment_frequencies(self, name):
        return WordFreq(self.assignment_words[name])


if __name__ == '__main__':
    pass