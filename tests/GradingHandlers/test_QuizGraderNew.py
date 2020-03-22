"""
Created by adam on 3/9/20
"""
__author__ = 'adam'

from unittest.mock import MagicMock, create_autospec, patch

from CanvasHacks.Definitions.base import BlockableActivity
from CanvasHacks.Errors.grading import StudentUnableToComplete
from CanvasHacks.GradingCorrections.base import IGradeCorrection
from CanvasHacks.GradingHandlers.quiz_new import QuizGrader
from CanvasHacks.GradingMethods.base import IGradingMethod
from CanvasHacks.Repositories.interfaces import ISubmissionRepo
from TestingBase import TestingBase
from factories.RepositoryMocks import ContentRepositoryMock

if __name__ == '__main__':
    pass


class TestQuizGraderUnitTests( TestingBase ):

    def setUp( self ):
        self.num = 3
        self.config_for_test()
        self.points_per_question = self.fake.random.randint( 1, 100 )

        self.create_new_and_preexisting_students()
        sp = { 'analyze.return_value': 0.5 }
        self.penalizers = [ ]
        for _ in range( 0, self.num ):
            m = MagicMock( **sp )
            # m.analyze = MagicMock( return_value=0.5 )
            self.penalizers.append( m )
        self.grade_methods = [ create_autospec( IGradingMethod ) for _ in range( 0, self.num ) ]
        self.corrections = [ create_autospec( IGradeCorrection ) for _ in range( 0, self.num ) ]
        self.activity = MagicMock( grade_methods=self.grade_methods, penalizers=self.penalizers,
                                   corrections=self.corrections )

        self.work_repo = ContentRepositoryMock( activity=self.activity, points_per_question=self.points_per_question )
        self.work_repo.create_quiz_repo_data( self.student_ids, submitted_at=self.fake.date_time_this_century(),
                                              make_dataframe=True )

        self.submission_repo = create_autospec( ISubmissionRepo )

        self.obj = QuizGrader( self.work_repo, self.submission_repo )

    def test__compute_initial_total( self ):
        for i, row in self.work_repo.data.iterrows():
            # call
            results = self.obj._compute_initial_total( row )
            # check
            for gm in self.grade_methods:
                gm.grade.assert_called()
                # gm.grade.assert_called_with(content)
                for qid, column_name in self.work_repo.question_columns:
                    gm.grade.assert_any_call( row[ column_name ] )

            # print(results)

    def test__compute_correction_pct( self ):
        for i, row in self.work_repo.data.iterrows():
            # call
            results = self.obj._compute_correction_pct( row )
            # check
            for gm in self.corrections:
                gm.analyze.assert_called()
                # gm.grade.assert_called_with(content)
                # for qid, column_name in self.work_repo.question_columns:
                # check called with row
                gm.analyze.assert_any_call( **row.to_dict() )

    def test__compute_penalty_pct( self ):
        """
        Since the penalizer will mostly handle penalties based
        on times, we check that particular use case.
        :return:
        """
        for i, row in self.work_repo.data.iterrows():
            # call
            results = self.obj._compute_penalty_pct( row )
            # check
            for gm in self.penalizers:
                gm.analyze.assert_called()
                gm.analyze.assert_called_with( **row.to_dict() )

    def test__compute_penalty_pct_specific_to_times( self ):
        """
        Since the penalizer will mostly handle penalties based
        on times, we check that particular use case.
        :return:
        """
        for i, row in self.work_repo.data.iterrows():
            # call
            results = self.obj._compute_penalty_pct( row )
            # check
            for gm in self.penalizers:
                gm.analyze.assert_called()
                call_args = gm.analyze.call_args
                s = call_args[ 1 ][ 'submitted_at' ]
                self.assertEqual( row[ 'submitted_at' ], s )

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
    #     self.assertEqual(on_empty, result, "returns custom value when empty")
    #     self.grade_method.grade.assert_called()
    #     self.grade_method.grade.assert_called_with( content )


class TestQuizGraderFunctionalTests( TestingBase ):

    def setUp( self ):
        # each grade method needs to return .25
        self.num = 4
        self.config_for_test()
        self.points_per_question = self.fake.random.randint( 1, 100 )

        self.create_new_and_preexisting_students()
        # sp = { 'analyze.return_value': 0.5 }
        self.penalizers = [ ]
        # for _ in range( 0, self.num ):
        #     m = MagicMock( **sp )
        #     self.penalizers.append( m )
        self.grade_methods = []
        gp = { 'grade.return_value': 0.25 }
        for _ in range( 0, self.num ):
            self.grade_methods.append( MagicMock( **gp ) )

        # self.grade_methods = [ create_autospec( IGradingMethod ) for _ in range( 0, self.num ) ]
        sp = { 'analyze.return_value': 0 }
        self.corrections = [ MagicMock(**sp) for _ in range( 0, self.num ) ]

        self.activity = MagicMock( grade_methods=self.grade_methods,
                                   penalizers=self.penalizers,
                                   corrections=self.corrections )

        self.work_repo = ContentRepositoryMock( activity=self.activity, points_per_question=self.points_per_question )
        self.work_repo.create_quiz_repo_data( self.student_ids, submitted_at=self.fake.date_time_this_century(),
                                              make_dataframe=True )

        self.submission_repo = create_autospec( ISubmissionRepo )

        self.obj = QuizGrader( self.work_repo, self.submission_repo )


    def test__grade_row_no_penalty( self ):
        sp = { 'analyze.return_value': 0 }
        for _ in range( 0, self.num ):
            m = MagicMock( **sp )
            self.penalizers.append( m )

        # fudge_points = 0
        # self.penalizer.get_fudge_points = MagicMock( return_value=fudge_points )

        row = self.work_repo.data.iloc[ 0 ]

        # call
        result = self.obj._grade_row( row )

        # check things called with expected values
        for gm in self.grade_methods:
            gm.grade.assert_called()
            for qid, column_name in self.work_repo.question_columns:
                # grade method called on each question field in row
                gm.grade.assert_any_call( row[ column_name ] )

        # check fudge points
        result_fudge_points = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'fudge_points' ]
        self.assertEqual( result_fudge_points, 0, "zero fudge points returned" )

        # check question scores
        result_question_dict = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'questions' ]
        for qid, cname in self.work_repo.question_columns:
            self.assertIn( qid, result_question_dict, "expected dictionary key" )
            self.assertIn( 'score',
                           result_question_dict[ qid ],
                           "expected internal dict key" )
            self.assertEqual( result_question_dict[ qid ][ 'score' ],
                              self.points_per_question,
                              "expected question score" )

    def test_grade_row_penalty( self ):
        total_possible = self.points_per_question * len(self.work_repo.question_columns)

        fudge_points = total_possible * -0.5

        sp = { 'analyze.return_value': -0.25 }
        for _ in range( 0, 2):
            self.penalizers.append( MagicMock( **sp ) )

        row = self.work_repo.data.iloc[ 0 ]

        # call
        result = self.obj._grade_row( row )

        # check things called with expected values
        for gm in self.grade_methods:
            gm.grade.assert_called()
            for qid, column_name in self.work_repo.question_columns:
                # grade method called on each question field in row
                gm.grade.assert_any_call( row[ column_name ] )

        # check fudge points
        result_fudge_points = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'fudge_points' ]
        self.assertEqual( result_fudge_points, fudge_points, "expected fudge points returned" )

        # check question scores
        result_question_dict = result[ 'data' ][ "quiz_submissions" ][ 0 ][ 'questions' ]
        for qid, cname in self.work_repo.question_columns:
            self.assertIn( qid, result_question_dict, "expected dictionary key" )
            self.assertIn( 'score',
                           result_question_dict[ qid ],
                           "expected internal dict key" )
            self.assertEqual( result_question_dict[ qid ][ 'score' ],
                              self.points_per_question,
                              "expected question score" )

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

    @patch('CanvasHacks.GradingHandlers.quiz_new.BlockedByOtherStudent')
    def test_grade_row_student_blocked( self , checkerMock):
        def a():
            raise StudentUnableToComplete
        checkerMock.analyze = MagicMock(side_effect=a)

        # Only care about being blocked if total score is 0
        [gm.pop() for gm in self.grade_methods]

        gp = { 'grade.return_value': 0 }
        for _ in range( 0, self.num ):
            self.grade_methods.append( MagicMock( **gp ) )


        # total_possible = self.points_per_question * len( self.work_repo.question_columns )
        #
        # fudge_points = total_possible * -0.5
        #
        # sp = { 'analyze.return_value': -0.25 }
        # for _ in range( 0, 2 ):
        #     self.penalizers.append( MagicMock( **sp ) )
        self.activity = create_autospec(BlockableActivity, grade_methods=self.grade_methods,
                                   penalizers=self.penalizers,
                                   corrections=self.corrections )

        self.assocRepo = MagicMock()

        self.obj = QuizGrader( self.work_repo, self.submission_repo, association_repo=self.assocRepo )

        row = self.work_repo.data.iloc[ 0 ]

        # call
        with self.assertRaises(StudentUnableToComplete):
            result = self.obj._grade_row( row )



    def test_grade( self ):
        self.skipTest( 'todo' )
        # todo Mixed credit and no credit students
        # todo Different total scores
        # todo Different attempts
