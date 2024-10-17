"""
Created by adam on 3/10/20
"""
__author__ = 'adam'

from unittest.mock import MagicMock, create_autospec
from CanvasHacks import environment
from CanvasHacks.GradingCorrections.base import IGradeCorrectionPoints
from CanvasHacks.GradingCorrections.penalities import IPenalizer
from CanvasHacks.GradingHandlers.records import PointsRecord
from CanvasHacks.GradingHandlers.review import ReviewGrader, ReviewGraderNew
from CanvasHacks.GradingMethods.base import IGradingMethod
from CanvasHacks.GradingMethods.nonempty import CreditForNonEmptyPoints
from CanvasHacks.GradingMethods.review import ReviewBasedPoints
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


class TestReviewGraderWithMetareviewDeterminedPoints( TestingBase ):
    """
    Tests for cases where the review grade is partially determined by points
    assigned by another student through the metareview.
    """

    def setUp( self ):
        self.config_for_test()
        self.points_per_question = self.fake.random.randint( 1, 100 )

        self.points_assigned_in_metareview = self.fake.random.randint( 1, 50 )

        self.create_new_and_preexisting_students()

        self.penalizer = create_autospec( IPenalizer )
        self.grade_method = create_autospec( IGradingMethod )

        self.activity = MagicMock( grade_method=self.grade_method, penalizer=self.penalizer )

        self.work_repo = ContentRepositoryMock( activity=self.activity, points_per_question=self.points_per_question )
        self.work_repo.create_quiz_repo_data( self.student_ids, submitted_at=self.fake.date_time_this_century(),
                                              make_dataframe=True )

        self.submission_repo = create_autospec( ISubmissionRepo )

        self.obj = ReviewGraderNew( self.work_repo, self.submission_repo )

    def test__compute_score( self ):
        points = self.fake.random.randint(1,100)
        att = { 'grade.return_value' : points}
        grader = create_autospec( CreditForNonEmptyPoints, **att )
        grader.configure_mock(**att)
        self.obj.grade_methods = [grader]
        record = create_autospec(PointsRecord)

        content = self.fake.paragraph()

        # call
        self.obj._compute_score( record, self.work_repo.data.loc[0] )

        # check
        self.obj.grade_methods[0].grade.assert_called()
        record.add_question_points.assert_called()

        for qid, column_name in self.work_repo.question_columns:
            record.add_question_points.assert_any_call(column_name, points)

    # def test__get_score_custom_on_empty( self ):
    #     # Custom on empty case
    #     self.grade_method.grade = MagicMock( return_value=None )
    #     content = self.fake.paragraph()
    #     on_empty = 'taco'
    #
    #     # call
    #     result = self.obj._get_score( content, on_empty=on_empty )
    #
    #     # check
    #     self.assertEqual( on_empty, result, "returns custom value when empty" )
    #     self.grade_method.grade.assert_called()
    #     self.grade_method.grade.assert_called_with( content )

    # def test__grade_row_no_penalty( self ):
    #     fudge_points = 0
    #     self.penalizer.get_fudge_points = MagicMock( return_value=fudge_points )
    #     self.grade_method.grade = MagicMock( return_value=self.points_per_question )
    #     row = self.work_repo.data.iloc[ 0 ]
    #
    #     # call
    #     result = self.obj._grade_row( row )
    #
    #     # check things called with expected values
    #     self.grade_method.grade.assert_called()
    #     for qid, column_name in self.work_repo.question_columns:
    #         # grade method called on each question field in row
    #         self.grade_method.grade.assert_any_call( row[ column_name ] )
    #
    #     # check fudge points
    #     result_fudge_points = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'fudge_points' ]
    #     self.assertEqual( result_fudge_points, 0, "zero fudge points returned" )
    #
    #     # check question scores
    #     result_question_dict = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'questions' ]
    #     for qid, cname in self.work_repo.question_columns:
    #         self.assertIn( qid, result_question_dict, "expected dictionary key" )
    #         self.assertIn( 'score', result_question_dict[ qid ], "expected internal dict key" )
    #         self.assertEqual( result_question_dict[ qid ][ 'score' ], self.points_per_question,
    #                           "expected question score" )

    def test__compute_penalty( self ):
        fudge_points = -50
        att = {'name' : self.fake.text(), 'get_fudge_points.return_value' : fudge_points}
        # self.penalizer.get_fudge_points = MagicMock( return_value=fudge_points )
        self.penalizer.configure_mock(**att)
        self.obj.penalizers = [self.penalizer]

        # self.grade_method.grade = MagicMock( return_value=self.points_per_question )
        row = self.work_repo.data.iloc[ 0 ]
        record = create_autospec(PointsRecord)

        # call
        result = self.obj._compute_penalty( record, row )

        # check things called with expected values
        self.obj.penalizers[ 0 ].get_fudge_points.assert_called()
        record.add_fudge_points.assert_called()

        # check fudge points were added to record
        record.add_fudge_points.assert_any_call(att['name'], fudge_points)

        # result_fudge_points = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'fudge_points' ]
        # self.assertEqual( result_fudge_points, fudge_points, "expected fudge points returned" )
        #
        # # check question scores
        # result_question_dict = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'questions' ]
        # for qid, cname in self.work_repo.question_columns:
        #     self.assertIn( qid, result_question_dict, "expected dictionary key" )
        #     self.assertIn( 'score', result_question_dict[ qid ], "expected internal dict key" )
        #     self.assertEqual( result_question_dict[ qid ][ 'score' ], self.points_per_question,
        #                       "expected question score" )

    def test__penalty_message( self ):
        self.skipTest( 'todo' )


    def test__compute_corrections_other_points( self ):
        fudge_points = 50
        att = { 'analyze.return_value' : fudge_points}
        correction = create_autospec(IGradeCorrectionPoints)
        correction.configure_mock(**att)

        self.obj.corrections = [correction]

        row = self.work_repo.data.iloc[ 0 ]
        record = create_autospec(PointsRecord)

        # call
        self.obj._compute_correction( record, row )

        # check things called with expected values
        # Analyze method (not grade) was called
        self.obj.corrections[ 0 ].analyze.assert_called()

        # check fudge points were added to record
        record.add_fudge_points.assert_called()
        record.add_fudge_points.assert_any_call(correction, fudge_points)


    def test__compute_corrections_review_based( self ):
        fudge_points = 50
        att = { 'grade.return_value' : fudge_points}
        correction = create_autospec(ReviewBasedPoints)
        correction.configure_mock(**att)

        self.obj.corrections = [correction]

        # self.grade_method.grade = MagicMock( return_value=self.points_per_question )
        row = self.work_repo.data.iloc[ 0 ]
        record = create_autospec(PointsRecord)
        record.configure_mock(**{'student_id' : 9})

        # call
        self.obj._compute_correction( record, row )

        # check
        # Grade method (not analyze) was called
        self.obj.corrections[ 0 ].grade.assert_called()

        # check fudge points were added to record
        record.add_fudge_points.assert_called()
        record.add_fudge_points.assert_any_call(correction, fudge_points)



class TestReviewGraderFunctionalTests( TestingBase ):

    def test_grade( self ):
        self.skipTest( 'todo' )
        # todo Mixed credit and no credit students
        # todo Different total scores
        # todo Different attempts
