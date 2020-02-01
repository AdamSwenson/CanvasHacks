"""
Various utilities for project

Created by adam on 1/19/20
"""
from functools import wraps

import pandas as pd

__author__ = 'adam'





if __name__ == '__main__':
    pass


def ensure_timestamps(f):
    """Makes sure that everything passed into the function
    is either a pd.Timestamp or pd.Timedelta
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        args = list(args)
        i=0
        for a in args:
            if not isinstance(a, pd.Timestamp) and not isinstance(a, pd.Timedelta):
                args[i] = pd.to_datetime(a)
            i+=1

        for k in kwargs.keys():
            if not isinstance(kwargs[k], pd.Timestamp) and not isinstance(a, pd.Timedelta):
                kwargs[k] = pd.to_datetime(kwargs[k])
        return f(*args, **kwargs)

    return decorated