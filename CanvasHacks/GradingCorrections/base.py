"""
Base for all tools which add to or reduce
a total score based on some criteria

Created by adam on 3/16/20
"""
__author__ = 'adam'

from abc import ABC

from CanvasHacks.GradingHandlers.records import PointsRecord

if __name__ == '__main__':
    pass


class IGradeCorrection(ABC):
    """
    GradeCorrections return a percentage that the
    initial total score should be raised.

    # todo Decide whether there is value in distinguishing between penalizers and corrections since they just return a different signed percentage

    """

    def analyze( self, *args, **kwargs ):
        """
        Returns a signed float of the percentage
        the contribution the evaluated item makes to the
        overall score should be raised or lowered.

        if overall score = 4, comprising
            A = 2
            B = 1
            C = 1
        and this correction applies to A, the result 0.5
        means their overall score should be 3

        :param work:
        :return: signed float
        """
        raise NotImplementedError

    @property
    def name( self ):
        """Returns the class name of the grading method. Often used in
        storing method name as a key"""
        return self.__class__.__name__



class IGradeCorrectionPoints(ABC):
    """
    GradeCorrections return a float that the
    initial total score should be raised.

    # todo Decide whether there is value in distinguishing between penalizers and corrections since they just return a different signed percentage

    """

    def analyze( self, *args, **kwargs ):
        """
        Returns a signed float of the points
        the contribution the evaluated item makes to the
        overall score should be raised or lowered.

        if overall score = 4, comprising
            A = 2
            B = 1
            C = 1
        and this correction applies to A, the result 0.5
        means their overall score should be 3

        """
        raise NotImplementedError

    @property
    def name( self ):
        """Returns the class name of the grading method. Often used in
        storing method name as a key"""
        return self.__class__.__name__

