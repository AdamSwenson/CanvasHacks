"""
Created by adam on 2/27/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass


class NonStringInContentField(Exception):
    """Raised when something other than a string
    appears in a field that we are assessing
    """
    pass