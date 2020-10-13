"""
Created by adam on 9/23/20
"""
__author__ = 'adam'

from CanvasHacks.GradingMethods.base import IGradingMethodPoints
from CanvasHacks.Models.model import StoreMixin


class PointsRecord( StoreMixin ):
    """
    A record of all the points assigned (including negative points
    for penalties) and the method which assigned them for one student
    """

    GENERAL_MESSAGE_KEY = 'general'

    FUDGE_POINTS_PREFIX = 'fp-'
    """String added to the name of a fudge points field """

    def __init__( self, **kwargs ):

        self.student_id = None

        self.grade_dict = { }
        """Keys will be names of the grading / penalty / correction method which 
        assigned the number of points or, for quizzes, the name of the question which
        receives that number of points. Values will be integer or float point amounts"""

        self.log_messages = { }
        """Keys will be names of the grading / penalty / correction method which 
        generated the message"""

        self.handle_kwargs( **kwargs )

    @property
    def total_points( self ):
        """
        Returns sum of all points in the grade_dict.

        :return:
        """
        return sum( [ p for p in self.grade_dict.values() ] )

    @property
    def total_fudge_points( self ):
        """
        Returns the sum of all fudge points
        :return:
        """
        fields = [ f for f in self.grade_dict.keys() if f[ : len(self.FUDGE_POINTS_PREFIX)] == self.FUDGE_POINTS_PREFIX]
        return sum( [ p for k, p in self.grade_dict.items() if k in fields])

    def add_grade( self, grade_method: IGradingMethodPoints, points: float ):
        """
        Stores an amount of assigned points in grade_dict with the name of the method
        providing the points as key
        :param grade_method: The object which assigned the number of points
        :param points: The number of points (positive or negative) assigned
        by the grading method
        :return:
        """
        # if not isinstance(grade_method, IGradingMethodPoints):

        # self.grade_dict[ grade_method.__class__.__name__ ] = points
        self.grade_dict[ grade_method.name ] = points

    def add_question_points( self, question_name: str, points: float ):
        """
        When grading quizzes, we need to record points for each question so
        that we can upload accordingly. This stores the question name as key and
        points received as value in the grade_dict

        :param question_name:
        :param points:
        :return:
        """
        self.grade_dict[ question_name ] = points

    def add_fudge_points( self, method_or_name, points ):
        """
        When grading quizzes things like late penalties and reviewer assigned
        points will have to be uploaded as fudge points. This adds such items
        to the grade_dict with a prefix identifying them as such
        :param method_or_name: Either a method with a name attribute or a string name for the thing giving the fudge points
        :param points:
        :return:
        """
        name = method_or_name if isinstance(method_or_name, str) else method_or_name.name
        k = f"{self.FUDGE_POINTS_PREFIX}{name}"
        self.grade_dict[k] = points

    def add_log_message( self, grade_method: IGradingMethodPoints ):
        """
        Stores any log message housed on the grade_method.messages to the record with the name of the method
        providing the points as key
        :param grade_method: The object which assigned the number of points
        :return:
        """
        if hasattr( grade_method, 'message' ) and len( grade_method.message ) > 0:
            self.log_messages[ grade_method.name ] = grade_method.message

    @property
    def general_message_keys( self ):
        """Returns a list of keys which cover general messages"""
        return [ m for m in self.log_messages.keys() if
                 m[ : len( self.GENERAL_MESSAGE_KEY ) ] == self.GENERAL_MESSAGE_KEY ]

    def add_general_message( self, message ):
        k = f"{self.GENERAL_MESSAGE_KEY} {len( self.general_message_keys ) + 1}"

        self.log_messages[ k ] = message

    @property
    def data_for_log_entry( self ):
        """
        Returns the expected dictionary of data for the logger's use
        :return:
        """
        d = { 'student_id': self.student_id }

        for k, v in self.grade_dict.items():
            # Add the points to the dictionary
            d[ k ] = v

            # check for any messages and include them after the score
            if k in self.log_messages.keys():
                m = self.log_messages[ k ]
                # format the column header
                h = "{} message".format( k )
                d[ h ] = m

        # include any general messages
        for gmk in self.general_message_keys:
            d[ gmk ] = self.log_messages[ gmk ]

        return d


if __name__ == '__main__':
    pass
