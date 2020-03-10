"""
Created by adam on 2/18/20
"""

__author__ = 'adam'

from CanvasHacks.GradingTools.base import IGrader

__author__ = 'adam'

from CanvasHacks.GradingTools.nonempty import IGradingMethod
from CanvasHacks.GradingTools.penalities import IPenalizer


class JournalGrader( IGrader ):
    """Handles grading weekly journals"""
    grade_method: IGradingMethod
    penalizer: IPenalizer

    def __init__( self, work_repo, **kwargs ):
        """
        :param work_repo: Content repository with journal data
        :param kwargs:
        """
        self.work_repo = work_repo
        super().__init__( **kwargs )
        self.penalizer = self.activity.penalizer
        self.grade_method = self.activity.grade_method
        self.graded = [ ]

    def grade( self ):
        """Assigns a provisional grade for the journal
        Will return as a list of tuples
        todo: Add logging of details of how grade assigned

       Determines how much credit potentially late credit/no credit
        assignments should receive.
        Created in CAN-24
        """
        for submission in self.work_repo.data:
            if submission.body is not None:
                score = self.grade_method.grade( submission.body )
                if score:
                    score = self.penalizer.get_penalized_score( submission.submitted_at, score, record=submission )
                    self.graded.append( (submission, int( score )) )

        self.report_late_penalties()

        return self.graded

    def report_late_penalties( self ):
        # Report late penalties
        if len( self.penalizer.penalized_rows ) > 0:
            for penalty_dict in self.penalizer.penalized_records:
                self._penalty_message(penalty_dict['penalty'], penalty_dict['record'])


    def _penalty_message( self, penalty, row ):
        """
        Handles printing or logging of penalties applied

        # todo enable logging

        :param penalty:
        :param row:
        :return:
        """
        stem = 'Student #{}: Submitted on {}; was due {}. Penalized {}'
        return stem.format( row[ 'student_id' ], row[ 'submitted' ], self.activity.due_at, penalty )

if __name__ == '__main__':
    pass
