"""
Created by adam on 2/1/19
"""
from typing import List, Any
from CanvasHacks.TextProcessing import WordFreq
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


class BagStore(object):

    def __init__(self):
        # Preserves the distinct submissions from students
        self.assignment_bags = {}
        # Holds 1 bag per assignment containing the contents of
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
        contain words from 1 student's submission on the assignment"""
        self.assignment_bags[name] = bags
        self.assignment_words[name] = []
        for b in bags:
            self.assignment_words[name] += [w for w in b]

    def get_assignment_frequencies(self, name):
        return WordFreq(self.assignment_words[name])


if __name__ == '__main__':
    pass