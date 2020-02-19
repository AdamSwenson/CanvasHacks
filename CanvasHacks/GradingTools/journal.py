"""
Created by adam on 2/18/20
"""
from CanvasHacks.GradingTools.penalities import get_penalty

__author__ = 'adam'

from CanvasHacks.GradingTools.base import IGrader

__author__ = 'adam'

from CanvasHacks.GradingTools.nonempty import receives_credit


class JournalGrader( IGrader ):
    """Handles grading weekly journals"""

    def __init__( self, work_repo, grade_func=None, **kwargs ):
        """
        :param grade_func: Function or method to use to determine grade
        """
        self.grade_func = grade_func
        self.work_repo = work_repo

        super().__init__( **kwargs )

    def grade( self ):
        """Assigns a provisional grade for the discussion assignment
        Will return as a list of tuples
        todo: Add logging of details of how grade assigned

       Determines how much credit potentially late credit/no credit
        assignments should recieve.
        Created in CAN-24"""
        self.graded = [ ]
        for submission in self.work_repo.data:
            if submission.body is not None:
                credit = receives_credit( submission.body )
                if credit:
                    score = 100
                # Now check whether need to penalize for lateness
                penalty = get_penalty( submission.submitted_at, self.activity.due_at, self.activity.lock_at, self.activity.grace_period )
                # penalty was set up for uploading where have to use fudge points.
                # so we need to interpret it a bit here.
                # It will have returned 0 for no penalty and .5 for half credit
                penalty = 100 * penalty
                score = score - penalty
                self.graded.append( (submission, int( score )) )
        return self.graded


if __name__ == '__main__':
    pass
