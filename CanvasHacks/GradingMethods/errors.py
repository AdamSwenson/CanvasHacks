"""
Created by adam on 3/15/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass


class InvalidGradingValuesError(Exception):
    """
    Raised when expecting a list of dictionaries of the
    format:
     { count : int,
            pct_credit : float
            }
    But got something bad
    """
    pass