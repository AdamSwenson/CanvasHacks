"""
Created by adam on 5/6/19
"""
from CanvasHacks.UtilityDecorators import ensure_timestamps

__author__ = 'adam'

import pandas as pd


@ensure_timestamps
def get_penalty( submitted_date, due_date, last_half_credit_date, grace_period=None ):
    """
    last_half_credit_date: Last moment they could receive half credit. If the assignment hasn't closed, submissions after this will be given 0.25 credit.
    grace_period: Should be a pd.Timedelta object, e.g., pd.Timedelta('1 day').
    """
    assert(isinstance(submitted_date, pd.Timestamp))

    if grace_period is not None:
        assert(isinstance(grace_period, pd.Timedelta))
        due_date += grace_period
        last_half_credit_date += grace_period
    # Check if full credit
    if submitted_date <= due_date:
        return 0
    # if it was submitted after due date but before the quarter credit date
    # i.e, the first exam, it gets half
    if submitted_date <= last_half_credit_date:
        return .5
    # if it was after the half credit date, it gets quarter credit
    return .25

#
# test_cases = [
#     {
#         # full credit case
#         'submitted': '2019-02-22 07:59:00',
#         'due': '2019-02-23 07:59:00',
#         'half': '2019-03-01 07:59:00',
#         'expect': 0
#     },
#     {
#         # half credit case
#         'submitted': '2019-02-24 07:59:00',
#         'due': '2019-02-23 07:59:00',
#         'half': '2019-03-01 07:59:00',
#         'expect': .5
#     },
#     {
#         # quarter credit case
#         'submitted': '2019-03-02 07:59:00',
#         'due': '2019-02-23 07:59:00',
#         'half': '2019-03-01 07:59:00',
#         'expect': .25
#     },
# ]
#
# for t in test_cases:
#     assert (get_penalty(t['submitted'], t['due'], t['half']) == t['expect'])

if __name__ == '__main__':
    pass


class QuizGrader:

    def __init__( self, work_repo, submission_repo, grade_func=None):
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
            if pd.isnull( row[ column_name ] ):
                questions[ qid ] = { 'score': 0 }
            else:
                questions[ qid ] = { 'score': 1.0 }
                total_score += 1
                # questions[ qid ] = { 'score': 4.0 }
                # total_score += 4

        # compute penalty if needed
        penalty = get_penalty( row[ 'submitted' ], self.activity.due_at, self.activity.last_half_credit_date, self.activity.grace_period )

        # will be 0 if not docking for lateness
        fudge_points = total_score * -penalty

        if penalty > 0:
            print(self._penalty_message( penalty, row ))

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