"""
Created by adam on 2/22/19
"""
from unittest import TestCase
from CanvasHacks.DataManagement import BagStore

__author__ = 'adam'

# test data
items_per_list = 2
num_students = 2

def make_student_bag(root, num_words):
    return ["{}{}".format(root, i) for i in range(0, num_words) ]

def make_assignment_bags(name, num_students=2, num_words=2):
    return [make_student_bag(name, num_words) for _ in range(0, num_students)]

def make_test_bags(assignments, num_students=2, num_words=2):
    """Makes a test data object. Like this for 'abc'
        {'a': [['a0', 'a1'], ['a0', 'a1']],
         'b': [['b0', 'b1'], ['b0', 'b1']],
         'c': [['c0', 'c1'], ['c0', 'c1']]}
     """
    return { a : make_assignment_bags(a, num_students, num_words) for a in assignments }

# test add_assignment_bags


class TestBagStore( TestCase ):
    def test_assignment_names( self ):
        self.fail()

    def test_unique_words( self ):
        test_data = make_test_bags('abc')
        store = BagStore()
        store.assignment_bags = test_data
        store.all_words
        self.assertEqual(len(store.all_words), 6)


    def test_all_bags( self ):
        self.fail()

    def test_all_words( self ):
        # test all words
        test_data = make_test_bags('abc')
        store = BagStore()
        store.assignment_bags = test_data
        store.all_words
        self.assertEqual(len(store.all_words), 12)


    def test_add_assignment_bags( self ):

        test_data = make_test_bags('abc')
        store = BagStore()
        for name in test_data.keys():
            store.add_assignment_bags(name, test_data[name])

        # make sure updated both stores
        self.assertEqual(len(store.assignment_bags.keys()),  3)
        self.assertEqual(len(store.assignment_words.keys()),  3)

        for name in test_data.keys():
            # check that bag was stored
            self.assertTrue(test_data[name] is store.assignment_bags[name])
            # check assignment words
            self.assertTrue(len(store.assignment_words[name]) is 4)


if __name__ == '__main__':
    pass
