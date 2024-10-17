"""
Created by adam on 4/11/20
"""
__author__ = 'adam'

from unittest import TestCase

from CanvasHacks.Text.process import TokenFiltrationMixin
from TestingBase import TestingBase

if __name__ == '__main__':
    pass


class TestTokenFiltrationMixin(TestingBase):
    def setUp(self) -> None:
        self.config_for_test()
        self.obj = TokenFiltrationMixin()

    def test__remove_list_for_regex( self ):
        r = self.obj._remove_list_for_regex
        print(r)
        self.assertIsInstance(r, list, "returned list")

    def test_to_remove_inc_stops_regex( self ):
        rx = self.obj.to_remove_inc_stops_regex
        self.assertIsNotNone(rx.match('the'))

    def test_keep( self ):
        self.assertTrue(self.obj.keep('dog'))
        self.assertTrue(self.obj.keep('the', keep_stopwords=True))
        self.assertFalse(self.obj.keep('the', keep_stopwords=False))

        t = ['the', '1', '.', 'dog']
        a = [ w for w in t if self.obj.keep(w, keep_stopwords=False)]
        self.assertEqual(len(a), 1, "removed expected from list")

        b = [ w for w in t if self.obj.keep(w, keep_stopwords=True)]
        self.assertEqual(len(b), 2, "removed expected from list")



class TestWordbagMaker( TestingBase ):
    def test_process( self ):
        self.skipTest('todo')
