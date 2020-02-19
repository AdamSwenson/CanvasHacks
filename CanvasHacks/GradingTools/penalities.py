"""
Created by adam on 2/17/20
"""
import pandas as pd

from CanvasHacks.UtilityDecorators import ensure_timestamps

__author__ = 'adam'

if __name__ == '__main__':
    pass


@ensure_timestamps
def get_penalty( submitted_date, due_date, last_half_credit_date, grace_period=None ):
    """
    last_half_credit_date: Last moment they could receive half credit. If the assignment hasn't closed, submissions after this will be given 0.25 credit. This can just be set to the lock date if there's no need to give quarter credit
    grace_period: Should be a pd.Timedelta object, e.g., pd.Timedelta('1 day').
    """
    assert (isinstance( submitted_date, pd.Timestamp ))

    if grace_period is not None:
        assert (isinstance( grace_period, pd.Timedelta ))
        due_date += grace_period
        last_half_credit_date += grace_period
    # Check if full credit
    if submitted_date <= due_date:
        return 0
    # if it was submitted after due date but before the quarter credit date
    # i.e, the first exam, it gets half
    if submitted_date <= last_half_credit_date:
        return .5
    # if it was after the half credit date, it gets quarter credit
    return .25
