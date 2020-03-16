"""
Created by adam on 9/21/18
"""
__author__ = 'adam'

import string

import nltk
from nltk.corpus import stopwords

from CanvasHacks.Errors.grading import NonStringInContentField



class ITextProcessor:

    def process( self, content ):
        raise NotImplementedError


class WordbagMaker( ITextProcessor ):

    def __init__( self, count_stopwords=True, remove=[ ], **kwargs ):
        self._remove = remove
        self.count_stopwords = count_stopwords

    def process( self, content ):
        """
        Returns a list of words
        :param content:
        :return:
        """
        if not isinstance( content, str ):
            raise NonStringInContentField

        return [ word.lower() for sent in nltk.tokenize.sent_tokenize( content ) for word in
                 nltk.tokenize.word_tokenize( sent ) if word.lower() not in self.to_remove ]

    @property
    def to_remove( self ):
        """
        Strings that should be filtered out when tokenizing

        :return:
        """
        self._remove += [ '``', "''", "'s" ]
        self._remove += string.punctuation
        if not self.count_stopwords:
            self._remove += stopwords.words( 'english' )
        return set( self._remove )




# ------------ old

def make_wordbag( text, to_remove=[] ):
    if len(to_remove) == 0:
        to_remove = [ '``', "''", "'s" ]
        to_remove += string.punctuation
        to_remove += stopwords.words( 'english' )
        to_remove = set( to_remove )

    return [ word.lower() for sent in nltk.tokenize.sent_tokenize( text ) for word in
             nltk.tokenize.word_tokenize( sent ) if word.lower() not in to_remove ]

if __name__ == '__main__':
    pass
