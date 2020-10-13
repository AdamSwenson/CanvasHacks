"""
Created by adam on 3/10/20
"""
__author__ = 'adam'

from CanvasHacks.Definitions.skaa import MetaReview
from CanvasHacks.Errors.grading import NonStringInContentField
from CanvasHacks.GradingHandlers.errors import NoGradingMethodDefined
from CanvasHacks.GradingHandlers.quiz import QuizGrader
from CanvasHacks.GradingHandlers.records import PointsRecord
from CanvasHacks.GradingMethods.errors import UngradableActivity
from CanvasHacks.GradingMethods.nonempty import CreditForNonEmptyPoints
from CanvasHacks.GradingMethods.review import ReviewBasedPoints
from CanvasHacks.Repositories.interfaces import ISubmissionRepo
from CanvasHacks.Repositories.quizzes import QuizRepository

if __name__ == '__main__':
    pass


class ReviewGrader( QuizGrader ):
    """Handles grading review assignments
    These will be essentially quiz assignments but we may
    want to handle the multiple choice differently
    todo Currently this clones QuizGrader consider updating all of this in CAN-57
    """

    def __init__( self, work_repo: QuizRepository, submission_repo: ISubmissionRepo, metareview: MetaReview = None,
                  metareview_points: int = None, **kwargs ):
        """
        :param work_repo: Content repository with review data
        :param metareview: A MetaReview object where points for this review are
        assigned
        :param metareview_points: The number of points assigned by the reviewer

        :param kwargs:
        """
        self.work_repo = work_repo
        self.submission_repo = submission_repo

        self.metareview = metareview
        self.metareview_points = metareview_points

        # super().__init__( **kwargs )

        self.penalizer = self.activity.penalizer
        self.grade_method = self.activity.grade_method

        self.graded = [ ]
        self.grade_records = [ ]


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

    def _grade_row( self, row, **kwargs ):
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
        # todo CAN-57 Consider implementing separate graders for text and multiple choice columns. That will allow to require more words in the text columns without hosing the 1-2 word multiple choice answers
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
        fudge_points = self.penalizer.get_fudge_points( row[ 'submitted' ], total_score, row )

        out = self._make_graded_row_output( row, questions, fudge_points )

        return out

    def grade( self, **kwargs ):
        """
        Grades all rows in work_repo.data
        todo: Add logging of details of how grade assigned
        :return: List of objects ready for upload
        """

        for i, row in self.work_repo.data.iterrows():
            try:
                self.graded.append( self._grade_row( row, **kwargs ) )
            except NonStringInContentField as e:
                print( e, row )

        # Print or log any penalties applied.
        # The penalizer object leaves this task up to us
        self.report_late_penalties()

        # todo Add recording of grade records
        return self.graded, self.grade_records




class ReviewGraderNew( QuizGrader ):
    """Handles grading review assignments
    These will be essentially quiz assignments but we may
    want to handle the multiple choice differently
    todo Currently this clones QuizGrader consider updating all of this in CAN-57
    """

    def __init__( self, work_repo: QuizRepository, submission_repo: ISubmissionRepo, metareview: MetaReview = None,
                  metareview_points: int = None, **kwargs ):
        """
        :param work_repo: Content repository with review data
        :param metareview: A MetaReview object where points for this review are
        assigned
        :param metareview_points: The number of points assigned by the reviewer

        :param kwargs:
        """
        self.work_repo = work_repo
        self.submission_repo = submission_repo

        self.metareview = metareview
        self.metareview_points = metareview_points

        # super().__init__( **kwargs )

        self.penalizers = self.activity.penalizers
        self.grade_methods = self.activity.grade_methods

        self.corrections = self.activity.corrections

        self.graded = [ ]
        self.grade_records = [ ]


    # def _get_score( self, content, on_empty=None ):
    #     """
    #     Calls the grading method which calculates the points received for
    #     a given question.
    #     Abstracted out so that can give a custom response value when
    #     the grade method returns None
    #     :param content:
    #     :return: integer points, None, or on_empty
    #     """
    #     g = self.grade_method.grade(content)
    #     if g:
    #         # if pd.isnull( row[ column_name ] ):
    #         return self.work_repo.points_per_question
    #     elif on_empty is not None:
    #         return on_empty

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
    #     # used for computing penalty
    #     total_score = 0
    #     questions = { }
    #
    #     # Grade on emptiness
    #     # todo CAN-57 Consider implementing separate graders for text and multiple choice columns. That will allow to require more words in the text columns without hosing the 1-2 word multiple choice answers
    #     for qid, column_name in self.work_repo.question_columns:
    #         content = row[ column_name ]
    #         pts = self._get_score( content, **kwargs )
    #         # Quiz type things require the scores to be uploaded
    #         # for each question.
    #         # Thus we grade each question and then penalize the
    #         # overall score with fudge points if necessary
    #         questions[ qid ] = { 'score': pts }
    #         total_score += pts
    #
    #
    #     out = self._make_graded_row_output( row, questions, fudge_points )
    #
    #     return out


    def grade( self, **kwargs ):
        """
        Grades all rows in work_repo.data
        todo: Add logging of details of how grade assigned
        :return: Tuple where ( [ ( submission, score) ...], [PointsRecord, ....]) where
        the former is ready to be used in uploading
        """

        for i, row in self.work_repo.data.iterrows():
            record = PointsRecord()
            record.student_id = row.student_id

            try:
                self._compute_score( record=record, row=row )

                # Since we are using the canvas quiz type assignments
                # the reviewer's scores and any penalties will need to be
                # uploaded separately as fudge points

                # todo reenable penalizer and corrections w correct checks
                # self._compute_penalty(record=record, content=row)
                # self._compute_correction(record=record, content=row)

                # Push the record into the store
                self.graded_records.append( record )

                # Create an object for uploading
                out = self.prepare_object_for_upload(record, row)
                self.graded.append( out )

            except (UngradableActivity, NonStringInContentField) as e:
                # Only store the legit records not the ones which
                # were skipped because, e.g., the reviewer didn't submit yet
                # todo Should probably use this in logging
                record.add_general_message(e)

        return self.graded, self.grade_records

    def prepare_object_for_upload( self, record, row ):
        """Returns an object ready to be uploaded to canvas"""
        # Add the score for uploading
        questions_dict = { column_name: record[ column_name ] for qid, column_name in
                           self.work_repo.question_columns }

        fudge_points = record.total_fudge_points

        return self._make_graded_row_output( row, questions_dict, fudge_points )


    def _compute_score( self, record: PointsRecord, row, **kwargs ):
        """
        Calls the grading method(s) which calculate the points received for
        all question columns.
        :param row: A data frame row containing the student's responses
        :return: PointsRecord with the grade methods and scores filled in
        """

        # used for computing penalty
        # total_score = 0
        # questions = { }

        if isinstance(self.grade_methods[0], CreditForNonEmptyPoints):
            # Grade on emptiness
            # todo CAN-57 Consider implementing separate graders for text and multiple choice columns. That will allow to require more words in the text columns without hosing the 1-2 word multiple choice answers
            for qid, column_name in self.work_repo.question_columns:
                content = row[ column_name ]
                pts = self.grade_methods[0].grade(content)
                # pts = self._get_score( content, **kwargs )
                # Quiz type things require the scores to be uploaded
                # for each question.
                # Thus we grade each question and then penalize the
                # overall score with fudge points if necessary
                record.add_question_points( column_name, pts )

        else:
            raise NoGradingMethodDefined
            # questions[ qid ] = { 'score': pts }
            # total_score += pts

        if len(self.grade_methods) > 1:
            # todo Expand to allow other methods
            raise NoGradingMethodDefined

    def _compute_penalty( self, record: PointsRecord, row, **kwargs ):
        """
        Adds the number of points that should be
        subtracted from the score to the point record
        :param row:
        :param kwargs:
        :return:
        """
        # get a negative float representing the points  the total score
        # should be adjusted down
        for penalizer in self.penalizers:
            # points = penalizer.analyze( **row.to_dict(), **kwargs )
            # record.add_grade( penalizer, points )

            # Compute penalty if needed
            # todo this should be made less specific
            # Will be 0 if not docking for lateness
            # Records of penalty will be stored on self.penalizer.penalized_records
            fudge_points = penalizer.get_fudge_points( row[ 'submitted' ], record.total_points, row )

            record.add_fudge_points(penalizer, fudge_points)

    def _compute_correction( self, record: PointsRecord, row, **kwargs ):
        """
        Returns a positive float representing the pct the total score
        should be adjusted up.

        For reviews where part of the grade is determined by metareview assigned
        points, this adds in the reviewer score

        :param row:
        :param kwargs:
        :return:
        """
        try:
            for method in self.corrections:

                if isinstance( method, ReviewBasedPoints ):
                    # we use a grading method here to get the reviewer up
                    # response.
                    # This method is under corrections here, since quizzes
                    # require uploading via via fudge points
                    points = method.grade( record.student_id )
                    record.add_fudge_points( method, points )

                else:
                    # todo should verify that instance of IGradeCorrectionPoints
                    # Other correction objects will be used via the analyze method
                    points = method.analyze( **row.to_dict(), **kwargs )
                    record.add_fudge_points( method, points )

                # This will determine if there is a message stored on the method
                # If so, it will be added to the record.
                record.add_log_message( method )

        except KeyError as e:
            # Likely raised because reviewer hasn't turned in their assignment
            record.add_general_message( e )
            print( e )

