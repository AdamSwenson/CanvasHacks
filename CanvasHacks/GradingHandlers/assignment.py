"""
Created by adam on 3/24/20
"""

from CanvasHacks.Definitions.base import BlockableActivity
from CanvasHacks.Errors.grading import NonStringInContentField
from CanvasHacks.GradingAnalyzers.blocked import BlockedByOtherStudent
from CanvasHacks.GradingHandlers.base import IGrader
from CanvasHacks.Logging.penalties import PenaltyLogger
from CanvasHacks.Repositories.assignments import AssignmentRepository
from CanvasHacks.Repositories.interfaces import ISubmissionRepo

__author__ = 'adam'

if __name__ == '__main__':
    pass


class AssignmentGrader( IGrader ):
    # grade_method: IGradingMethod
    # penalizer: IPenalizer

    def __init__( self, work_repo: AssignmentRepository, submission_repo: ISubmissionRepo, association_repo=None,
                  **kwargs ):
        """

        :param work_repo:
        :param submission_repo:
        :param association_repo: Only needed if grading an assignment which can be blocked
        :param kwargs:
        """
        self.association_repo = association_repo
        self.blocked_checker = None
        self.work_repo = work_repo
        self.submission_repo = submission_repo
        super().__init__( **kwargs )

        self.corrections = self.activity.corrections

        self.penalizers = self.activity.penalizers

        self.grade_methods = self.activity.grade_methods
        # Todo Check that output of grading methods sums to 1?

        self.graded = [ ]

        if isinstance( self.work_repo.activity, BlockableActivity ) and self.association_repo is not None:
            # association repo better have been set
            # todo
            self.blocked_checker = BlockedByOtherStudent( self.submission_repo, self.association_repo )

    def _compute_score( self, content, **kwargs ):
        """
        Calls the grading method which calculates the points received for
        a given question.s
        :param content:
        :return: integer points, None, or on_empty
        """
        pct_possible = 0
        for method in self.grade_methods:
            # each method should return a float pct
            # all of which sum to 1
            pct_possible += method.grade( content )
        # pct_possible = self.grade_method.grade( content )

        # return pct_possible
        return self.work_repo.points_per_question * pct_possible

    def _compute_penalty_pct( self, row, **kwargs ):
        down = 0
        # get a negative float representing the pct the total score
        # should be adjusted down
        for penalizer in self.penalizers:
            down += penalizer.analyze( **row.to_dict(), **kwargs )
        return down

    def _compute_correction_pct( self, row, **kwargs ):
        up = 0
        for correction in self.corrections:
            # get a positive float representing the pct the total score
            # should be adjusted up
            up += correction.analyze( **row.to_dict(), **kwargs )
        return up

    def _compute_initial_total( self, row, **kwargs ):
        """
        Returns the questions dict to be sent and the total
        score
        :param row:
        :param kwargs:
        :return:
        """
        content = row[ 'body' ]
        return self._compute_question_score( content, **kwargs )

    # def _grade_row( self, row, **kwargs ):
    #     """Grades a row
    #
    #     NB, requires that the non-graded attempts be
    #     filtered out before passing in
    #
    #     todo test whether the problem with non-graded people getting zeros is caused here
    #
    #     :param row: pd.DataFrame row
    #     :param kwargs:
    #     :return: Dictionary formatted for uploading
    #     """
    #
    #     # for student
    #     total_score = 0
    #
    #     # compute the initial total score of the activity
    #     # this is the job of the GradingMethod
    #     total_score = self._compute_initial_total( row, **kwargs )
    #
    #     try:
    #         if total_score == 0 and self.blocked_checker is not None:
    #             # This will raise an exception if they are blocked
    #             # and we won't return anything
    #             self.blocked_checker.analyze( row[ 'student_id' ] )
    #
    #         # Compute penalty if needed
    #         # Will be 0 if not docking for lateness
    #         # Records of penalty will be stored on self.penalizer.penalized_records
    #         down = self._compute_penalty_pct( row, **kwargs )
    #
    #         # Calculate things which could increase the score
    #         # this also may raise an exception if the student was
    #         # unable to complete it
    #         up = self._compute_correction_pct( row, **kwargs )
    #
    #         adj = up + down
    #
    #         fudge_points = total_score * adj
    #
    #         out = self._make_graded_row_output( row, questions, fudge_points )
    #
    #         return out
    #
    #     except StudentUnableToComplete as e:
    #         # handle situation where they were blocked by e.g. a reviewer not turning
    #         # in their part
    #
    #         # NB this is going to be tricky once relax deadlines
    #         # Should initially just log everything. But there will need to
    #         # be a switch for when they get full credit
    #         print( e )
    #         if CanvasHacks.testglobals.TEST:
    #             # Reraise so can see what happened for tests
    #             raise e

    # def _make_graded_row_output( self, row, question_score_dict, fudge_points ):
    #     out = {
    #         'student_id': int( row[ 'student_id' ] ),
    #         'attempt': int( row[ 'attempt' ] ),
    #         'submission_id': int( row[ 'submission_id' ] ),
    #         'course_id': int( row[ 'course_id' ] ),
    #         'assignment_id': int( row[ 'assignment_id' ] ),
    #         'data': { }
    #     }
    #
    #     out[ 'data' ][ "assignment_submissions" ] = [
    #         {
    #             "attempt": int( row[ 'attempt' ] ),
    #             "fudge_points": fudge_points,
    #             "questions": question_score_dict
    #         }
    #     ]
    #
    #     return out
    #
    #     # if self.using_percentage:
    #     #     pct = 100 * adj
    #     #
    #     # # using total points
    #     # score = total_score * adj
    #
    #     #
    #     # # Grade on emptiness
    #     # for qid, column_name in self.work_repo.question_columns:
    #     #     content = row[ column_name ]
    #     #     pts = self._compute_question_score( content, **kwargs )
    #     #     # assignment type things require the scores to be uploaded
    #     #     # for each question.
    #     #     # Thus we grade each question and then penalize the
    #     #     # overall score with fudge points if necessary
    #     #     questions[ qid ] = { 'score': pts }
    #     #     total_score += pts
    #     #
    #     #     # Compute penalty if needed
    #     #     # Will be 0 if not docking for lateness
    #     #     # Records of penalty will be stored on self.penalizer.penalized_records
    #     #     fudge_points = self.penalizer.get_fudge_points(row['submitted'], total_score, row)
    #     #
    #     # out = self._make_graded_row_output(row, questions, fudge_points)
    #     #
    #     # return out

    def grade( self, **kwargs ):
        """
        Grades all rows in work_repo.data
        todo: Add logging of details of how grade assigned
        :return: List of objects ready for upload
        """
        # todo Add some sort of type check here
        for i, submission in self.work_repo.data.iterrows():
            # for submission in self.work_repo.data:
            if submission.body is not None:
                score = self._compute_score( submission.body )
                if score:
                    # todo reenable penalizer w correct checks
                    # down = self._compute_penalty_pct()
                    # score = self.penalizer.get_penalized_score( submission.submitted_at, score, record=submission )
                    score = int( score )
                    score = score if score <= 100 else 100
                    self.graded.append( (submission, score ) )

        # self.report_late_penalties()

        return self.graded

    def report_late_penalties( self ):
        # Report late penalties
        if len( self.penalizer.penalized_records ) > 0:
            for penalty_dict in self.penalizer.penalized_records:
                self._penalty_message( penalty_dict[ 'penalty' ], penalty_dict[ 'record' ] )

    def _penalty_message( self, penalty, record ):
        """
        Handles printing or logging of penalties applied

        # todo enable logging

        :param penalty:
        :param row: A Submission object
        :return:
        """
        stem = 'Student #{}: Submitted on {}; was due {}. Penalized {}'
        try:
            return stem.format( record.student_id, record.submitted, self.activity.due_at, penalty )
        except (TypeError, AttributeError):
            # Will hit this if a Submission object
            return stem.format( record.user_id, record.submitted_at, self.activity.due_at, penalty )

        for i, row in self.work_repo.data.iterrows():
            try:
                self.graded.append( self._grade_row( row, **kwargs ) )
            except NonStringInContentField as e:
                print( e, row )

        # Print or log any penalties applied.
        # The penalizer object leaves this task up to us
        PenaltyLogger.log( self.penalizer )

        return self.graded

    # def _penalty_message( self, penalty, row ):
    #     """
    #     Handles printing or logging of penalties applied
    #
    #     # todo enable logging
    #
    #     :param penalty:
    #     :param row:
    #     :return:
    #     """
    #     stem = 'Student #{}: Submitted on {}; was due {}. Penalized {}'
    #     return stem.format( row[ 'student_id' ], row[ 'submitted' ], self.activity.due_at, penalty )
    #

    # def report_late_penalties( self ):
    #     # Report late penalties
    #     if len( self.penalizer.penalized_records ) > 0:
    #         for penalty_dict in self.penalizer.penalized_records:
    #             self._penalty_message( penalty_dict[ 'penalty' ], penalty_dict[ 'record' ] )
