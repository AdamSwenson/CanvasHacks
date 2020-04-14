"""
Created by adam on 9/21/18
"""
__author__ = 'adam'

import re
import string

import nltk
from nltk.corpus import stopwords

from CanvasHacks.Errors.grading import NonStringInContentField
from CanvasHacks.Files.JournalsFileTools import load_words_to_ignore


class ITextProcessor:

    def process( self, content ):
        raise NotImplementedError


class TokenFiltrationMixin:
    """
    Anything which will remove some tokens from a wordbag
    should inherit this.
    Can also be used standalone
    """

    @property
    def to_remove( self ):
        """
        OLD

        Strings that should be filtered out when tokenizing

        :return:
        """
        self._remove += [ '``', "''", "'s" ]
        self._remove += [ "%s" % i for i in range( 0, 100 ) ]
        self._remove += [ 'none', '305' ]
        self._remove += string.punctuation
        if not self.count_stopwords:
            self._remove += stopwords.words( 'english' )
        return set( self._remove )

    @property
    def to_remove_inc_stops_regex( self ):
        """
        Returns compiled regex including stopwords
        :return:
        """
        stop_list = [ '\\b{}\\b'.format( w ) for w in stopwords.words( 'english' )]
        remove = self._remove_list_for_regex + stop_list
        remove = "|".join(remove)
        return re.compile( r"{}".format( remove ) )

    @property
    def _remove_list_for_regex( self ):
        """
        Makes a list of components that will be disjoined into
        a regular expression by something else
        :return:
        """
        # Any freestanding numbers or number containing
        remove = [ "\d+" ]

        # punctuation
        remove += ["[{}]".format( "".join( string.punctuation ))]

        # Single letters except for 'i'
        remove += [ '\\b{}\\b'.format( c ) for c in string.ascii_lowercase if c not in [ 'i' ] ]

        # words from file
        remove += [ '\\b{}\\b'.format( w ) for w in load_words_to_ignore()]

        # Return list without formatting or compiling to regex
        return remove

    @property
    def to_remove_regex( self ):
        """
        Returns a compiled regular expression of things to remove
        :return:
        """
        # # Any freestanding numbers or number containing
        # remove = [ "\d+" ]
        #
        # # punctuation
        # remove += ["[{}]".format( "".join( string.punctuation ))]
        #
        # # Single letters except for 'i'
        # remove += [ '\\b{}\\b'.format( c ) for c in string.ascii_lowercase if c not in [ 'i' ] ]
        #
        # # words from file
        # remove += [ '\\b{}\\b'.format( w ) for w in load_words_to_ignore()]
        #
        # # Make into regex
        # remove = '|'.join( remove )

        remove = self._remove_list_for_regex
        remove = "|".join(remove)
        return re.compile( r"{}".format( remove ) )

    def keep( self, token, keep_stopwords=False ):
        """
        For a given token, returns true if it should be kept in the bag
        or false if it should be removed
        :param token:
        :param keep_stopwords:
        :return:
        """
        if keep_stopwords:
            rx = self.to_remove_regex
        else:
            rx = self.to_remove_inc_stops_regex

        return rx.match(token) is None

# def filter_on_regex( word, rx=rx ):
#     if rx.match( word ) is None:
#         return word


class WordbagMaker( ITextProcessor, TokenFiltrationMixin ):

    def __init__( self, keep_stopwords=True, remove=[ ], **kwargs ):
        if len( remove ) == 0:
            self._remove = load_words_to_ignore()
        else:
            self._remove = remove
        self.keep_stopwords = keep_stopwords

    def process( self, content ):
        """
        Returns a list of words
        :param content:
        :return:
        """
        if not isinstance( content, str ):
            raise NonStringInContentField

        return [ word.lower() for sent in nltk.tokenize.sent_tokenize( content ) for word in
                 nltk.tokenize.word_tokenize( sent ) if self.keep(word.lower(), keep_stopwords=self.keep_stopwords) ]

        # return [ word.lower() for sent in nltk.tokenize.sent_tokenize( content ) for word in
        #          nltk.tokenize.word_tokenize( sent ) if word.lower() not in self.to_remove ]

    # @property
    # def to_remove( self ):
    #     """
    #     Strings that should be filtered out when tokenizing
    #
    #     :return:
    #     """
    #     self._remove += [ '``', "''", "'s" ]
    #     self._remove += [ "%s" % i for i in range( 0, 100 ) ]
    #     self._remove += [ 'none', '305' ]
    #     self._remove += string.punctuation
    #     if not self.keep_stopwords:
    #         self._remove += stopwords.words( 'english' )
    #     return set( self._remove )



# s = "".join(string.punctuation)
# single_letters = ['\\b{}\\b'.format(c) for c in string.ascii_lowercase if c not in ['i']]
#
# remove = ["\d+", "[{}]".format(s)]
# remove += single_letters
# # remove += string.punctuation
# remove = '|'.join(remove)
# rx = re.compile(r"{}".format(remove))

def filter_on_regex(word, rx):
    if rx.match(word) is None:
        return word

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
