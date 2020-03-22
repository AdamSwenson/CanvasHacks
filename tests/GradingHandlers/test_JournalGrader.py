"""
Created by adam on 3/9/20
"""
__author__ = 'adam'

from CanvasHacks.GradingHandlers.journal import JournalGrader
from TestingBase import TestingBase

from unittest.mock import MagicMock


from unittest import TestCase


if __name__ == '__main__':
    pass


class TestJournalGrader( TestingBase ):

    def make_journal_submission( self, is_empty=False ):
        txt = "" if is_empty else self.fake.paragraph()
        return MagicMock(body=txt,
                         submitted_at=self.fake.date_time_this_century())

    def setUp( self ):
        self.config_for_test()
        self.create_new_and_preexisting_students()

        self.full_credit_score = 100

        self.penalizer = MagicMock()
        self.grade_method = MagicMock()
        self.grade_method.grade = MagicMock(return_value=self.full_credit_score)
        self.activity = MagicMock(grade_method=self.grade_method, penalizer=self.penalizer)

    def test_grade( self ):
        data = [self.make_journal_submission() for _ in self.students]
        self.penalizer.get_penalized_score = MagicMock(return_value=self.full_credit_score)
        work_repo = MagicMock( activity=self.activity, data=data )
        obj = JournalGrader(work_repo)

        # call
        obj.grade()

        # check
        self.assertEqual(len(self.students), len(obj.graded), "Expected number in output")

        for d in data:
            # Check that grade method received expected value
            self.grade_method.grade.assert_any_call(d.body)
            # Check that penalizer method received expected value
            # self.penalizer.get_penalized_score.assert_any_call((d.submitted_at, self.full_credit_score))

        for g in obj.graded:
            # Check put in output
            self.assertEqual(self.full_credit_score, g[1], "Correct score added")

    def test_grade_penalty( self ):
        data = [self.make_journal_submission() for _ in self.students]
        penalized_score = 21
        self.penalizer.get_penalized_score = MagicMock(return_value=penalized_score)
        work_repo = MagicMock( activity=self.activity, data=data )
        obj = JournalGrader(work_repo)

        # call
        obj.grade()

        # check
        self.assertEqual(len(self.students), len(obj.graded), "Expected number in output")

        for d in data:
            # Check that grade method received expected value
            self.grade_method.grade.assert_any_call(d.body)
            # Check that penalizer method received expected value
            # self.penalizer.get_penalized_score.assert_any_call((d.submitted_at, self.full_credit_score))

        for g in obj.graded:
            # Check put in output
            self.assertEqual(penalized_score, g[1], "Correct penalized score added")



