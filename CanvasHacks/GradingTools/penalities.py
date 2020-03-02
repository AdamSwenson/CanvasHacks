"""
Created by adam on 2/17/20
"""
import pandas as pd

from CanvasHacks.UtilityDecorators import ensure_timestamps
from CanvasHacks.TimeTools import check_is_date

__author__ = 'adam'

if __name__ == '__main__':
    pass


class IPenalizer:

    def get_penalty( self, submitted_date ):
        """
        :type submitted_date: object
        """
        raise NotImplementedError


class HalfLate( IPenalizer ):
    """Late assignments receive half credit"""

    def __init__( self, due_date, grace_period=None ):
        due_date = check_is_date(due_date)
        assert (isinstance( due_date, pd.Timestamp ))
        self.due_date = due_date

        if grace_period is not None:
            assert (isinstance( grace_period, pd.Timedelta ))
            self.due_date += grace_period

    def get_penalty( self, submitted_date ):
        submitted_date = check_is_date(submitted_date)
        assert (isinstance( submitted_date, pd.Timestamp ))
        # Check if full credit
        if submitted_date <= self.due_date:
            return 0
        return 0.50

    def get_penalized_score( self, submitted_date, original_score ):
        penalty = self.get_penalty(submitted_date)
        # penalty was set up for uploading where have to use fudge points.
        # so we need to interpret it a bit here.
        # It will have returned 0 for no penalty and .5 for half credit
        penalty = 100 * penalty
        score = original_score - penalty
        return score


class QuarterLate( IPenalizer ):

    def __init__( self, due_date, last_half_credit_date, grace_period=None ):
        assert (isinstance( due_date, pd.Timestamp ))
        assert (isinstance( last_half_credit_date, pd.Timestamp ))
        self.last_half_credit_date = last_half_credit_date
        self.due_date = due_date

        if grace_period is not None:
            assert (isinstance( grace_period, pd.Timedelta ))
            self.due_date += grace_period
            self.last_half_credit_date += grace_period

    @ensure_timestamps
    def get_penalty( self, submitted_date ):
        assert (isinstance( submitted_date, pd.Timestamp ))
        # Check if full credit
        if submitted_date <= self.due_date:
            return 0
        # if it was submitted after due date but before the quarter credit date
        # i.e, the first exam, it gets half
        if submitted_date <= self.last_half_credit_date:
            return 0.5
        # if it was after the half credit date, it gets quarter credit
        return 0.25


@ensure_timestamps
def get_penalty( submitted_date, due_date, last_half_credit_date, grace_period=None ):
    """
    OLD

    last_half_credit_date: Last moment they could receive half credit. If the unit hasn't closed, submissions after this will be given 0.25 credit. This can just be set to the lock date if there's no need to give quarter credit
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
