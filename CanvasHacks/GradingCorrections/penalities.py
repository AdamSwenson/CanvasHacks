"""
Created by adam on 2/17/20
"""
from abc import ABC

import pandas as pd

from CanvasHacks.Repositories.mixins import TimeHandlerMixin
from CanvasHacks.TimeTools import check_is_date
from CanvasHacks.UtilityDecorators import ensure_timestamps

__author__ = 'adam'

if __name__ == '__main__':
    pass


class IPenalizer(ABC):


    def analyze( self, *args, **kwargs ):
        """
        THIS IS THE LATEST VERSION CAN-60
        Returns a signed float of the percentage
        the contribution the evaluated item makes to the
        overall score should be lowered.

        :param work:
        :return: signed float
        """
        raise NotImplementedError


    def get_penalty( self, submitted_date ):
        """

        Returns the percentage that the assignment
        should be penalized.
        Not used on its own. get_fudge_points and
        get_penalized_score properly apply the output of this
        method for the particular grading use.

        :type submitted_date: pd.Datetime
        """
        raise NotImplementedError

    def get_fudge_points( self, submitted_date, total_score, row=None ):
        """
        For assignment types where we have to submit the
        grade via fudge points, this calculates the amount for
        canvas to subtract or add to the total score.

        If row is provided, will save record to self.penalized_records

        :param submitted_date: The date the student work was submitted
        :param total_score: The score that we will apply penalty to
        :param row: None or pd.DataFrame row. If not None, will save record
        :return: float
        """
        raise NotImplementedError

    @property
    def penalty_messages( self ):
        """
        Returns a list of penalty messages
        :return: list
        """
        out = []

        if len( self.penalized_records ) > 0:
            for penalty_dict in self.penalized_records:
                due_at = None
                try:
                    due_at = self.due_date
                except AttributeError:
                    # Some penalizers may not have a due date
                    pass
                msg = self._make_penalty_message( penalty_dict[ 'penalty' ], penalty_dict[ 'record' ], due_at=None )
                out.append(msg)
        return out


    def _make_penalty_message( self, penalty, row, due_at=None ):
            """
            Handles printing or logging of penalties applied

            # todo enable logging

            :param penalty:
            :param row:
            :return:
            """
            stem = 'Student #{}: Submitted on {}; was due {}. Penalized {}'
            return stem.format( row[ 'student_id' ], row[ 'submitted' ], due_at, penalty )


class NoLatePenalty( IPenalizer ):
    """
    All graders will need a penalizer object
    so this can be used if there is no penalty for
    late submissions
    """

    def __init__( self, *args, **kwargs ):
        self.penalized_records = [ ]

    def get_penalty( self, submitted_date, **kwargs ):
        return 0

    def get_penalized_score( self, submitted_date, original_score, **kwargs ):
        return original_score

    def get_fudge_points( self, submitted_date, total_score, row=None, **kwargs ):
        """
        For assignment types where we have to submit the
        grade via fudge points, this calculates the amount for
        canvas to subtract or add to the total score.

        If row is provided, will save record to self.penalized_records

        :param submitted_date: The date the student work was submitted
        :param total_score: The score that we will apply penalty to
        :param row: None or pd.DataFrame row. If not None, will save record
        :return: float
        """
        return 0


class HalfLate( IPenalizer, TimeHandlerMixin ):
    """Late assignments receive half credit"""

    def __init__( self, due_date, grace_period=None ):
        due_date = self._force_timestamp( due_date )
        assert (isinstance( due_date, pd.Timestamp ))
        self.due_date = due_date

        if grace_period is not None:
            assert (isinstance( grace_period, pd.Timedelta ))
            self.due_date += grace_period

        # Record of applied penalties
        self.penalized_records = [
            # List of dicts with format
            # 'record': row,
            # 'penalty': penalty,
            # optional (for methods which used fudge points)
            # 'fudge_points': fudge_points
        ]

    def get_penalty( self, submitted_at ):
        """
        Returns the percentage that the assignment
        should be penalized.
        Not used on its own. get_fudge_points and
        get_penalized_score properly apply the output of this
        method for the particular grading use.

        Will return 0.0 for an on-time assignment
        :param submitted_at:
        :return:
        """
        submitted_at = self._force_timestamp( submitted_at )
        assert (isinstance( submitted_at, pd.Timestamp ))
        # Check if full credit
        if submitted_at <= self.due_date:
            return 0
        return 0.50

    def get_penalized_score( self, submitted_date, original_score, record=None ):
        """
        Returns the score reduced by the appropriate penalty.
        If record is not none, the penalty etc will be saved to
        penalized_records
        :param submitted_date:
        :param original_score:
        :param record:
        :return: float
        """
        penalty = self.get_penalty( submitted_date )
        # penalty was set up for uploading where have to use fudge points.
        # so we need to interpret it a bit here.
        # It will have returned 0 for no penalty and .5 for half credit
        if penalty == 0:
            return original_score
        elif penalty > 0 and record is not None:
            self.penalized_records.append(
                { 'record': record,
                  'penalty': penalty
                  } )
        return original_score * penalty


    def get_point_reduction_pct( self, submitted_date, **kwargs ):
        return 1 - self.get_penalty(submitted_date)

    def get_fudge_points( self, submitted_date, total_score, row=None ):
        """
        For assignment types where we have to submit the
        grade via fudge points, this calculates the amount for
        canvas to subtract or add to the total score.

        If row is provided, will save record to self.penalized_records

        :param submitted_date: The date the student work was submitted
        :param total_score: The score that we will apply penalty to
        :param row: None or pd.DataFrame row. If not None, will save record
        :return: float
        """
        # compute penalty if needed
        penalty = self.get_penalty( submitted_date )

        # will be 0 if not docking for lateness
        fudge_points = total_score * -penalty

        if penalty > 0 and row is not None:
            # Save record so calling class can handle
            self.penalized_records.append( {
                'record': row,
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
        self.penalized_records = [
            # List of dicts with format
            # 'record': row,
            # 'penalty': penalty,
            # optional if use fudge points
            # 'fudge_points': fudge_points
        ]


    def get_point_reduction_pct( self, submitted_date ):
        return 1 - self.get_penalty(submitted_date)

    def get_penalty( self, submitted_date ):
        """
        Computes the penalty as a percentage to be combined with
        the original score by another method.
        Not used on its own. get_fudge_points and
        get_penalized_score properly interpret the output of this
        method for the particular grading use.
        :param submitted_date:
        :return: float
        """
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

        If row is provided, will save record to self.penalized_records

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
            self.penalized_records.append( {
                'record': row,
                'penalty': penalty,
                'fudge_points': fudge_points
            } )

        return fudge_points


# ================================= OLD


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
