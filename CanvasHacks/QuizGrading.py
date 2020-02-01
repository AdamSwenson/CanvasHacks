"""
Created by adam on 5/6/19
"""
from CanvasHacks.UtilityDecorators import ensure_timestamps

__author__ = 'adam'

import pandas as pd


@ensure_timestamps
def get_penalty(submitted_date, due_date, quarter_credit_date, grace_period=None):
    """
    grace_period: Should be a pd.Timedelta object, e.g., pd.Timedelta('1 day')
    """
    assert(isinstance(submitted_date, pd.Timestamp))

    if grace_period is not None:
        due_date += grace_period
    # Check if full credit
    if submitted_date <= due_date:
        return 0
    # if it was submitted after due date but before the quarter credit date
    # i.e, the first exam, it gets half
    if submitted_date <= quarter_credit_date:
        return .5
    # if it was after the half credit date, it gets quarter credit
    return .25

#
# test_cases = [
#     {
#         # full credit case
#         'submitted': '2019-02-22 07:59:00',
#         'due': '2019-02-23 07:59:00',
#         'half': '2019-03-01 07:59:00',
#         'expect': 0
#     },
#     {
#         # half credit case
#         'submitted': '2019-02-24 07:59:00',
#         'due': '2019-02-23 07:59:00',
#         'half': '2019-03-01 07:59:00',
#         'expect': .5
#     },
#     {
#         # quarter credit case
#         'submitted': '2019-03-02 07:59:00',
#         'due': '2019-02-23 07:59:00',
#         'half': '2019-03-01 07:59:00',
#         'expect': .25
#     },
# ]
#
# for t in test_cases:
#     assert (get_penalty(t['submitted'], t['due'], t['half']) == t['expect'])

if __name__ == '__main__':
    pass