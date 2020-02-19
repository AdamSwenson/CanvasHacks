"""
Created by adam on 5/6/19
"""
from CanvasHacks.GradingTools.nonempty import grade_credit_no_credit
from CanvasHacks.GradingTools.penalities import get_penalty
from CanvasHacks.Repositories.quizzes import QuizRepository

__author__ = 'adam'

import pandas as pd


if __name__ == '__main__':
    pass


class QuizGrader:

    def __init__( self, work_repo: QuizRepository, submission_repo, grade_func=None ):
        """
        :param grade_func: Function or method to use to determine grade
        """
        self.grade_func = grade_func
        self.work_repo = work_repo
        self.submission_repo = submission_repo

    @property
    def activity( self ):
        return self.work_repo.activity

    def grade( self ):
        self.graded = [ ]
        for i, row in self.work_repo.data.iterrows():
            self.graded.append(self._grade_row(row))
        return self.graded

    def _get_score( self, content, on_empty=None ):
        """
        The method which calculates the points received for
        a given question
        :param content:
        :return:
        """
        if grade_credit_no_credit(content):
            # if pd.isnull( row[ column_name ] ):
            return self.work_repo.points_per_question
        elif on_empty is not None:
            return on_empty

    def _get_fudge_points( self,  row, total_score ):
        """Calculates the amount for canvas to subtract or add to the total score"""
        # compute penalty if needed
        penalty = get_penalty( row[ 'submitted' ], self.activity.due_at, self.activity.last_half_credit_date, self.activity.grace_period )

        if penalty > 0:
            print(self._penalty_message( penalty, row ))

        # will be 0 if not docking for lateness
        fudge_points = total_score * -penalty
        return fudge_points

    def _grade_row(self, row):
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

        # Grade on emptiness
        # todo This should use credit_no_credit from GradingTools.nonempty
        for qid, column_name in self.work_repo.question_columns:
            content = row[ column_name ]
            pts = self._get_score(content)
            questions[ qid ] = { 'score': pts }
            total_score += pts
            # if grade_credit_no_credit(content):
            #     # if pd.isnull( row[ column_name ] ):
            #     pts = self.work_repo.points_per_question
            #     questions[ qid ] = { 'score': pts }
            #     total_score += pts
            # else:
            #     # todo test whether I need this and if this causes the problem w people getting 0s
            #     # questions[ qid ] = { 'score': 0 }
            #     pass
            #     # questions[ qid ] = { 'score': 4.0 }
            #     # total_score += 4

        # compute penalty if needed
        # will be 0 if not docking for lateness
        fudge_points = self._get_fudge_points(row, total_score)


        # # compute penalty if needed
        # penalty = get_penalty( row[ 'submitted' ], self.activity.due_at, self.activity.last_half_credit_date, self.activity.grace_period )
        #
        # # fudge_points = total_score * -penalty
        #
        # if penalty > 0:
        #     print(self._penalty_message( penalty, row ))

        out[ 'data' ][ "quiz_submissions" ] = [
            {
                "attempt": int( row[ 'attempt' ] ),
                "fudge_points": fudge_points,
                "questions": questions
            }
        ]
        return out

    def _penalty_message( self, penalty, row ):
        stem = 'Student #{}: Submitted on {}; was due {}. Penalized {}'
        return stem.format( row[ 'student_id' ], row[ 'submitted' ], self.activity.due_at, penalty )




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