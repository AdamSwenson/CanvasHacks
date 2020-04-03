"""
Created by adam on 2/18/20
"""
from CanvasHacks.Models.model import StoreMixin

__author__ = 'adam'


class IGrader(StoreMixin):
    """Parent which defines common methods for any
    class in charge of grading student work

    todo Calling classes should be keeping a record of details of how grade assigned
    """
    def __init__(self, **kwargs):
        self.graded = [ ]
        self.handle_kwargs(**kwargs)

    def grade( self ):
        """Carry out grading on internally stored data
        from the repos it holds"""
        raise NotImplementedError

    # def log( self ):
    #     """
    #     :return:
    #     """
    #     raise NotImplementedError

    @property
    def activity( self ):
        return self.work_repo.activity

#
# class WorkingGrader(IGrader):
#
#     def grade( self ):
#         # for student
#         total_score = 0
#
#         # compute the initial total score of the activity
#         # this is the job of the GradingMethod
#
#         down = 0
#         # get a negative float representing the pct the total score
#         # should be adjusted down
#         for penalizer in self.penalizers:
#             down += penalizer.get_penalty()
#
#         up = 0
#         for correction in self.corrections:
#             # get a positive float representing the pct the total score
#             # should be adjusted up
#             up += correction.analyze()
#
#         adj = up + down
#
#         #todo careful about adj = 0
#
#         if self.using_fudge_points:
#             fudge_points = total_score * adj
#
#         if self.using_percentage:
#             pct = 100 * adj
#
#         # using total points
#         score = total_score * adj
#

class AllQuestionsEmpty(Exception):
    """
    Raised when a student's submission has all values empty.
    This can be caught and a check performed to see whether the
    activity depends on another student doing their part
    """
    pass


if __name__ == '__main__':
    pass