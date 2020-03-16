"""
Created by adam on 3/15/20
"""
__author__ = 'adam'

from unittest import TestCase

from CanvasHacks.Text.process import WordbagMaker
from CanvasHacks.Text.stats import WordCount
from TestingBase import TestingBase

if __name__ == '__main__':
    pass


class TestWordCount( TestingBase ):
    def setUp(self) -> None:
        self.config_for_test()

    def test_initialized_correctly( self ):
        obj = WordCount(count_stopwords=False)
        self.assertIsInstance(obj.bagmaker, WordbagMaker, "instantiated correct helper")
        self.assertFalse(obj.bagmaker.count_stopwords, 'param set on bagmaker')


    def test_analyze( self ):
        obj = WordCount(count_stopwords=True)

        expected = self.fake.random.randint(1, 1000)
        content = " ".join([ self.fake.word() for _ in range(0, expected)])

        result = obj.analyze(content)

        self.assertEqual(expected, result, 'expected count returned')

