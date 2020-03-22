"""
Created by adam on 3/10/20
"""
__author__ = 'adam'

from CanvasHacks.GradingHandlers.base import IGrader
from CanvasHacks.GradingHandlers.quiz import QuizGrader
from CanvasHacks.Repositories.interfaces import ISubmissionRepo
from CanvasHacks.Repositories.quizzes import QuizRepository

if __name__ == '__main__':
    pass


class ReviewGrader(QuizGrader):
    """Handles grading review assignments
    These will be essentially quiz assignments but we may
    want to handle the multiple choice differently
    todo Currently this clones QuizGrader consider updating all of this in CAN-57
    """

    def __init__( self, work_repo: QuizRepository, submission_repo: ISubmissionRepo, **kwargs ):
        """
        :param work_repo: Content repository with review data
        :param kwargs:
        """
        self.work_repo = work_repo
        self.submission_repo = submission_repo

        # super().__init__( **kwargs )

        self.penalizer = self.activity.penalizer
        self.grade_method = self.activity.grade_method

        self.graded = [ ]

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
        fudge_points = self.penalizer.get_fudge_points(row['submitted'], total_score, row)

        out = self._make_graded_row_output(row, questions, fudge_points)

        return out