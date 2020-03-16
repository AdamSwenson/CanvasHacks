"""
Created by adam on 3/15/20
"""
__author__ = 'adam'

from CanvasHacks.Errors.grading import NonStringInContentField

if __name__ == '__main__':
    pass

from CanvasHacks.Text.process import make_wordbag
from nltk.corpus import stopwords
import string


class IGradingMethod:

    def grade( self, content ):
        raise NotImplementedError
