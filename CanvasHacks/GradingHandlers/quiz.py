"""
Created by adam on 5/6/19
"""
from CanvasHacks.Errors.grading import NonStringInContentField
from CanvasHacks.GradingHandlers.base import IGrader
from CanvasHacks.GradingMethods.base import IGradingMethod
from CanvasHacks.GradingCorrections.penalities import get_penalty, IPenalizer
from CanvasHacks.Repositories.interfaces import ISubmissionRepo
from CanvasHacks.Repositories.quizzes import QuizRepository

__author__ = 'adam'

import pandas as pd

if __name__ == '__main__':
    pass


class QuizGrader( IGrader ):

    grade_method: IGradingMethod
    penalizer: IPenalizer

    def __init__( self, work_repo: QuizRepository, submission_repo: ISubmissionRepo, **kwargs ):
        """

        :param work_repo:
        :param submission_repo:
        :param kwargs:
        """
        self.work_repo = work_repo
        self.submission_repo = submission_repo
        super().__init__( **kwargs )

        self.penalizer = self.activity.penalizer
        self.grade_method = self.activity.grade_method

        self.graded = [ ]

    def grade( self, **kwargs):
        """
        Grades all rows in work_repo.data
        todo: Add logging of details of how grade assigned
        :return: List of objects ready for upload
        """

        for i, row in self.work_repo.data.iterrows():
            try:
                self.graded.append( self._grade_row( row, **kwargs ) )
            except NonStringInContentField as e:
                print(e, row)

        # Print or log any penalties applied.
        # The penalizer object leaves this task up to us
        self.report_late_penalties()

        return self.graded

    def report_late_penalties( self ):
        # Report late penalties
        if len( self.penalizer.penalized_records ) > 0:
            for penalty_dict in self.penalizer.penalized_records:
                self._penalty_message(penalty_dict['penalty'], penalty_dict['record'])

    def _get_score( self, content, on_empty=None ):
        """
        Calls the grading method which calculates the points received for
        a given question.
        Abstracted out so that can give a custom response value when
        the grade method returns None
        :param content:
        :return: integer points, None, or on_empty
        """
        g = self.grade_method.grade(content)
        if g:
            # if pd.isnull( row[ column_name ] ):
            return self.work_repo.points_per_question
        elif on_empty is not None:
            return on_empty

    def _make_graded_row_output( self, row, question_score_dict, fudge_points ):
        out = {
            'student_id': int( row[ 'student_id' ] ),
            'attempt': int( row[ 'attempt' ] ),
            'submission_id': int( row[ 'submission_id' ] ),
            'course_id': int( row[ 'course_id' ] ),
            'quiz_id': int( row[ 'quiz_id' ] ),
            'data': { }
        }

        out[ 'data' ][ "quiz_submissions" ] = [
            {
                "attempt": int( row[ 'attempt' ] ),
                "fudge_points": fudge_points,
                "questions": question_score_dict
            }
        ]

        return out

    def _grade_row( self, row , **kwargs):
        """Grades a row

        NB, requires that the non-graded attempts be
        filtered out before passing in

        todo test whether the problem with non-graded people getting zeros is caused here

        :param row: pd.DataFrame row
        :param kwargs:
        :return: Dictionary formatted for uploading
        """
        # used for computing penalty
        total_score = 0
        questions = { }

        # Grade on emptiness
        for qid, column_name in self.work_repo.question_columns:
            content = row[ column_name ]
            pts = self._get_score( content, **kwargs )
            # Quiz type things require the scores to be uploaded
            # for each question.
            # Thus we grade each question and then penalize the
            # overall score with fudge points if necessary
            questions[ qid ] = { 'score': pts }
            total_score += pts

            # Compute penalty if needed
            # Will be 0 if not docking for lateness
            # Records of penalty will be stored on self.penalizer.penalized_records
            fudge_points = self.penalizer.get_fudge_points(row['submitted'], total_score, row)

        out = self._make_graded_row_output(row, questions, fudge_points)

        return out

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





# ============================= OLD


def grade( frame, quiz_data_obj, grace_period=None ):
    """
    OLD
    This handles the actual grading

    quiz_data_obj will have the payload format:
        "quiz_submissions": [{
        "attempt": int(attempt),
        "fudge_points": total_score
      },
          "questions": {
      "QUESTION_ID": {
        "score": null, // null for no change, or an unsigned decimal
        "comment": null // null for no change, '' for no comment, or a string
      }
    """
    results = [ ]
    #     questions = detect_question_columns(frame.columns)

    for i, row in frame.iterrows():
        fudge_points = 0
        out = {
            'student_id': int( row[ 'student_id' ] ),
            'attempt': int( row[ 'attempt' ] ),
            'submission_id': int( row[ 'submission_id' ] ),
            'course_id': int( row[ 'course_id' ] ),
            'quiz_id': int( row[ 'quiz_id' ] ),
            'data': { }
        }
        # used for computing penalty
        total_score = 0
        questions = { }

        for qid, column_name in quiz_data_obj.question_columns:
            if pd.isnull( row[ column_name ] ):
                questions[ qid ] = { 'score': 0 }
            else:
                questions[ qid ] = { 'score': 1.0 }
                total_score += 1

        # compute penalty if needed
        penalty = get_penalty( row[ 'submitted' ], quiz_data_obj.due_date, quiz_data_obj.quarter_credit_date,
                               grace_period )
        # will be 0 if not docking
        fudge_points = total_score * -penalty
        if penalty > 0:
            print( 'Student #{}: Submitted on {}; was due {}. Penalized {}'.format( row[ 'student_id' ],
                                                                                    row[ 'submitted' ],
                                                                                    quiz_data_obj.due_date, penalty ) )

        out[ 'data' ][ "quiz_submissions" ] = [
            {
                "attempt": int( row[ 'attempt' ] ),
                "fudge_points": fudge_points,
                "questions": questions
            }
        ]

        results.append( out )
    return results
