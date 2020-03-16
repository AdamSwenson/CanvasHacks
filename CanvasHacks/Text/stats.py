"""
Created by adam on 3/15/20
"""
__author__ = 'adam'

import nltk

from CanvasHacks.Models.model import StoreMixin
from CanvasHacks.Text.process import WordbagMaker

if __name__ == '__main__':
    pass


class ITextStat:

    def analyze( self, content ):
        raise NotImplementedError


class WordCount(ITextStat):

    def __init__(self, **kwargs):
        """
        kwargs will often contain
            count_stopwords
        :param kwargs:
        """
        self.bagmaker = WordbagMaker(**kwargs)

    def analyze( self, content ):
        """
        Returns the total number of words in the content
        :param content:
        :return:
        """
        bag = self.bagmaker.process(content)
        return len( bag )


class WordFreq(object):
    """
    Tools for computing and plotting frequencies of word appearances using the nltk.FreqDist method
    """

    def __init__(self, word_list):
        """
        Args:
            word_list: list of words
        """
        self.data = word_list
        self.unique = sorted(set(self.data))

        assert(type(word_list) is list)
        self.freqDist = nltk.FreqDist(self.data)
        self.ranking = list(self.freqDist.keys())

    def topN(self, number_to_display):
        """
        Returns the N most common items in the dataset

        Args:
            number_to_display: The number to display
        """
        assert(type(number_to_display) is int)
        return self.ranking[0: number_to_display]

    def plot(self, number_to_display, **kwargs):
        """
        Displays a plot of the frequency distribution of item frequencies
        Args:
            number_to_display: The top n to display
        """
        assert(type(number_to_display) is int)
        self.freqDist.plot(number_to_display, cumulative=True, **kwargs)

    @property
    def word_freq_dicts( self ):
        """
        A list of dictionaries with the frequency of each word
        Returns:
            Dictionary with words as keys and 'word' and 'count'
        """
        # fd = nltk.FreqDist(self.data)
        # for word in self.data:
        #     fd.inc(word)
        # results = []
        return [{'word': w[0], 'count' : w[1]} for w in self.freqDist.items()]
        #     results.append()
        # return results