"""
Created by adam on 2/17/20
"""

import pandas as pd

from CanvasHacks.Repositories.mixins import TimeHandlerMixin
from CanvasHacks.TimeTools import check_is_date
from CanvasHacks.UtilityDecorators import ensure_timestamps

__author__ = 'adam'

if __name__ == '__main__':
    pass


class IPenalizer:

    def get_penalty( self, submitted_date ):
        """
        :type submitted_date: object
        """
        raise NotImplementedError

    def get_fudge_points( self, submitted_date, total_score, row=None ):
        """
        For assignment types where we have to submit the
        grade via fudge points, this calculates the amount for
        canvas to subtract or add to the total score.

        If row is provided, will save record to self.penalized_rows

        :param submitted_date: The date the student work was submitted
        :param total_score: The score that we will apply penalty to
        :param row: None or pd.DataFrame row. If not None, will save record
        :return: float
        """
        raise NotImplementedError


class NoLatePenalty( IPenalizer ):
    """
    All graders will need a penalizer object
    so this can be used if there is no penalty for
    late submissions
    """

    def __init__( self, *args, **kwargs  ):
        self.penalized_rows = []

    def get_penalty( self, submitted_date ):
        return 0

    def get_penalized_score( self, submitted_date, original_score ):
        return original_score

    def get_fudge_points( self, submitted_date, total_score, row=None ):
        """
        For assignment types where we have to submit the
        grade via fudge points, this calculates the amount for
        canvas to subtract or add to the total score.

        If row is provided, will save record to self.penalized_rows

        :param submitted_date: The date the student work was submitted
        :param total_score: The score that we will apply penalty to
        :param row: None or pd.DataFrame row. If not None, will save record
        :return: float
        """
        return 0


class HalfLate( IPenalizer, TimeHandlerMixin ):
    """Late assignments receive half credit"""

    def __init__( self, due_date, grace_period=None ):
        due_date = check_is_date( due_date )
        assert (isinstance( due_date, pd.Timestamp ))
        self.due_date = due_date

        if grace_period is not None:
            assert (isinstance( grace_period, pd.Timedelta ))
            self.due_date += grace_period

        # Record of applied penalties
        self.penalized_rows = [
            # List of dicts with format
            # 'row': row,
            # 'penalty': penalty,
            # 'fudge_points': fudge_points
        ]

    def get_penalty( self, submitted_date ):
        """
        Returns the percentage that the assignment
        should be penalized.
        Will return 0.0 for an on-time assignment
        :param submitted_date:
        :return:
        """
        submitted_date = check_is_date( submitted_date )
        assert (isinstance( submitted_date, pd.Timestamp ))
        # Check if full credit
        if submitted_date <= self.due_date:
            return 0
        return 0.50

    def get_penalized_score( self, submitted_date, original_score ):
        penalty = self.get_penalty( submitted_date )
        # penalty was set up for uploading where have to use fudge points.
        # so we need to interpret it a bit here.
        # It will have returned 0 for no penalty and .5 for half credit
        if penalty == 0:
            return original_score
        return original_score * penalty
        # penalty = 100 * penalty
        # score = original_score - penalty
        # return score

    def get_fudge_points( self, submitted_date, total_score, row=None ):
        """
        For assignment types where we have to submit the
        grade via fudge points, this calculates the amount for
        canvas to subtract or add to the total score.

        If row is provided, will save record to self.penalized_rows

        :param submitted_date: The date the student work was submitted
        :param total_score: The score that we will apply penalty to
        :param row: None or pd.DataFrame row. If not None, will save record
        :return: float
        """
        # compute penalty if needed
        penalty = self.get_penalty( submitted_date )

        # penalty = self.penalizer.get_penalty(row['submitted'])
        # penalty = get_penalty( row[ 'submitted' ], self.activity.due_at, self.activity.last_half_credit_date, self.activity.grace_period )

        # will be 0 if not docking for lateness
        fudge_points = total_score * -penalty

        if penalty > 0 and row is not None:
            # Save record so calling class can handle
            self.penalized_rows.append( {
                'row': row,
                'penalty': penalty,
                'fudge_points': fudge_points
            } )

        return fudge_points


class QuarterLate( IPenalizer, TimeHandlerMixin ):
    """
    Gives half credit for submissions between
    due date and last half credit date.
    Gives quarter credit thereafter
    """

    def __init__( self, due_date, last_half_credit_date, grace_period=None ):
        # assert (isinstance( due_date, pd.Timestamp ))
        # assert (isinstance( last_half_credit_date, pd.Timestamp ))
        self.last_half_credit_date = self._force_timestamp( last_half_credit_date )
        self.due_date = self._force_timestamp( due_date )

        if grace_period is not None:
            assert (isinstance( grace_period, pd.Timedelta ))
            self.due_date += grace_period
            self.last_half_credit_date += grace_period

        # Record of applied penalties
        self.penalized_rows = [
            # List of dicts with format
            # 'row': row,
            # 'penalty': penalty,
            # 'fudge_points': fudge_points
        ]

    # @ensure_timestamps
    def get_penalty( self, submitted_date ):
        submitted_date = self._force_timestamp( submitted_date )
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

    def get_fudge_points( self, submitted_date, total_score, row=None ):
        """
        For assignment types where we have to submit the
        grade via fudge points, this calculates the amount for
        canvas to subtract or add to the total score.

        If row is provided, will save record to self.penalized_rows

        :param submitted_date: The date the student work was submitted
        :param total_score: The score that we will apply penalty to
        :param row: None or pd.DataFrame row. If not None, will save record
        :return: float
        """
        # compute penalty if needed
        penalty = self.get_penalty( submitted_date )

        # penalty = self.penalizer.get_penalty(row['submitted'])
        # penalty = get_penalty( row[ 'submitted' ], self.activity.due_at, self.activity.last_half_credit_date, self.activity.grace_period )

        # will be 0 if not docking for lateness
        fudge_points = total_score * -penalty

        if penalty > 0 and row is not None:
            # Save record so calling class can handle
            self.penalized_rows.append( {
                'row': row,
                'penalty': penalty,
                'fudge_points': fudge_points
            } )

        return fudge_points


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
