"""
Created by adam on 3/10/20
"""
__author__ = 'adam'

from unittest.mock import create_autospec, MagicMock

from CanvasHacks.GradingMethods.base import IGradingMethod
from CanvasHacks.GradingCorrections.penalities import IPenalizer
from CanvasHacks.GradingHandlers.review import ReviewGrader
from CanvasHacks.Repositories.interfaces import ISubmissionRepo
from TestingBase import TestingBase
from factories.RepositoryMocks import ContentRepositoryMock

if __name__ == '__main__':
    pass


class TestReviewGrader( TestingBase ):
    def setUp( self ):
        self.config_for_test()
        self.points_per_question = self.fake.random.randint( 1, 100 )

        self.create_new_and_preexisting_students()

        self.penalizer = create_autospec( IPenalizer )
        self.grade_method = create_autospec( IGradingMethod )

        self.activity = MagicMock( grade_method=self.grade_method, penalizer=self.penalizer )

        self.work_repo = ContentRepositoryMock( activity=self.activity, points_per_question=self.points_per_question )
        self.work_repo.create_quiz_repo_data( self.student_ids,
                                            submitted_at=self.fake.date_time_this_century(),
                                              make_dataframe=True )

        self.submission_repo = create_autospec( ISubmissionRepo )

        self.obj = ReviewGrader( self.work_repo, self.submission_repo )

    def test__get_score( self ):
        content = self.fake.paragraph()
        # call
        self.obj._get_score( content )
        # check
        self.grade_method.grade.assert_called()
        self.grade_method.grade.assert_called_with( content )

    def test__get_score_custom_on_empty( self ):
        # Custom on empty case
        self.grade_method.grade = MagicMock( return_value=None )
        content = self.fake.paragraph()
        on_empty = 'taco'

        # call
        result = self.obj._get_score( content, on_empty=on_empty )

        # check
        self.assertEqual( on_empty, result, "returns custom value when empty" )
        self.grade_method.grade.assert_called()
        self.grade_method.grade.assert_called_with( content )

    def test__grade_row_no_penalty( self ):
        fudge_points = 0
        self.penalizer.get_fudge_points = MagicMock( return_value=fudge_points )
        self.grade_method.grade = MagicMock( return_value=self.points_per_question )
        row = self.work_repo.data.iloc[ 0 ]

        # call
        result = self.obj._grade_row( row )

        # check things called with expected values
        self.grade_method.grade.assert_called()
        for qid, column_name in self.work_repo.question_columns:
            # grade method called on each question field in row
            self.grade_method.grade.assert_any_call( row[ column_name ] )

        # check fudge points
        result_fudge_points = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'fudge_points' ]
        self.assertEqual( result_fudge_points, 0, "zero fudge points returned" )

        # check question scores
        result_question_dict = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'questions' ]
        for qid, cname in self.work_repo.question_columns:
            self.assertIn( qid, result_question_dict, "expected dictionary key" )
            self.assertIn( 'score', result_question_dict[ qid ], "expected internal dict key" )
            self.assertEqual( result_question_dict[ qid ][ 'score' ], self.points_per_question,
                              "expected question score" )

    def test_grade_row_penalty( self ):
        fudge_points = -50
        self.penalizer.get_fudge_points = MagicMock( return_value=fudge_points )
        self.grade_method.grade = MagicMock( return_value=self.points_per_question )
        row = self.work_repo.data.iloc[ 0 ]

        # call
        result = self.obj._grade_row( row )

        # check things called with expected values
        self.grade_method.grade.assert_called()
        for qid, column_name in self.work_repo.question_columns:
            # grade method called on each question field in row
            self.grade_method.grade.assert_any_call( row[ column_name ] )

        # check fudge points
        result_fudge_points = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'fudge_points' ]
        self.assertEqual( result_fudge_points, fudge_points, "expected fudge points returned" )

        # check question scores
        result_question_dict = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'questions' ]
        for qid, cname in self.work_repo.question_columns:
            self.assertIn( qid, result_question_dict, "expected dictionary key" )
            self.assertIn( 'score', result_question_dict[ qid ], "expected internal dict key" )
            self.assertEqual( result_question_dict[ qid ][ 'score' ], self.points_per_question,
                              "expected question score" )

    def test__penalty_message( self ):
        self.skipTest( 'todo' )


class TestReviewGraderFunctionalTests( TestingBase ):

    def test_grade( self ):
        self.skipTest( 'todo' )
        # todo Mixed credit and no credit students
        # todo Different total scores
        # todo Different attempts
