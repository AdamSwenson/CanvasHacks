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



class InvalidReviewPointValue(Exception):
    """Raised when the points assigned by a reviewer are out
    of range"""
    pass


class UngradableActivity(Exception):
    """Raised when something prevents the assignment
    from being graded"""
    message = "Something unspecified has prevented the assignment from being graded"


class WaitingForReviewerToSubmit(UngradableActivity):
    """Called when the reviewer has not yet done
    their job thus blocking the ability to grade"""
    message = "Reviewer has not submitted review thus cannot complete grading"


class NoReviewerAssigned(UngradableActivity):
    """Raised when the author has not yet been
    assigned a reviewer"""
    pass