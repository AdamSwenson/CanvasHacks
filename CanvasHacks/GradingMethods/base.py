"""
Created by adam on 3/15/20
"""
__author__ = 'adam'

from abc import ABC

from CanvasHacks.Errors.grading import NonStringInContentField

if __name__ == '__main__':
    pass


class IGradingMethod( ABC ):
    """
    GradingMethods are in charge of taking whatever we are
    grading and determining the initial score based on the content.

    The grade method will return a float which the calling
    method should multiply against the available points.

    When multiple GradingMethods will be used to compute the
    initial score, each should be initialized with
    the pct_of_score containing a float such that the pct_of_score
    for all used GradingMethods add to 1

    Parent for those classes which return a
    positive float to indicate how much of the total
    possible credit a student should receive.

    Normally applied to questions
    """

    def grade( self, *args, **kwargs ):
        raise NotImplementedError
