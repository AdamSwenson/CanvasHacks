"""
Created by adam on 3/16/20
"""
__author__ = 'adam'

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Definitions.base import BlockableActivity
from CanvasHacks.GradingHandlers.quiz import QuizGrader
from CanvasHacks.Models.model import StoreMixin
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from CanvasHacks.Repositories.submissions import QuizSubmissionRepository



from CanvasHacks import environment


class GradeQuiz(StoreMixin):
    """
    Executable which grades and uploads scores for all selected
    assignments

    Taken from the code in the Quiz tools notebook which was created
    in CAN-44

    Created: CAN-44 / CAN-60
    """

    def __init__( self, activity=None, rest_timeout=5, no_late_penalty=True, upload_grades=True, **kwargs ):
        self.upload_grades = upload_grades
        self.wait = rest_timeout
        self.no_late_penalty = no_late_penalty
        if activity is None:
            # programmatically get data
            activity = [ c for c in environment.CONFIG.unit.components if c.id == environment.CONFIG.assignments[ 0 ][ 0 ] ][
            0 ]
        self.activity = activity

        if self.no_late_penalty:
            self.activity.due_at = self.activity.lock_at

        self.graded = [ ]

        self.handle_kwargs(**kwargs)

    def _initialize( self ):
        """
        Handle instantiating and loading repositories
        :return:
        """
        self.workRepo = WorkRepositoryLoaderFactory.make( course=environment.CONFIG.course,
                                                          activity=self.activity,
                                                          rest_timeout=self.wait )

        self.quiz = environment.CONFIG.course.get_quiz( self.activity.quiz_id )
        self.subRepo = QuizSubmissionRepository( self.quiz )

        # If this is a quiz type assignment, we need to get the quiz submission objects
        # not the regular submission object so we can use them for uploading
        self.qsubs = [ s for s in self.quiz.get_submissions() ]

        # Filter previously graded
        self.subRepo.data = [ s for s in self.subRepo.data if s.workflow_state != 'complete' ]
        self.workRepo.data = self.workRepo.data[ self.workRepo.data.workflow_state != 'complete' ].copy( deep=True )

        self.workRepo.data.reset_index( inplace=True )

        # We will need the association repo if the activity can be
        # blocked or graded by another student
        self.association_repo = None
        if isinstance( self.activity, BlockableActivity ):
            dao = SqliteDAO()
            self.association_repo = AssociationRepository(dao, self.activity)


    def run( self, **kwargs ):
        self.handle_kwargs(**kwargs)
        # Load data
        self._initialize()
        # Let the grader do its job
        grader = QuizGrader( work_repo=self.workRepo,
                             submission_repo=self.subRepo,
                             association_repo=self.association_repo )
        g = grader.grade( on_empty=0 )
        self.graded += g
        print( "Graded: ", len( self.graded ) )

        if self.upload_grades:
            self._upload_step()


    def get_submission_object( self, student_id, attempt ):
        return [ d for d in self.qsubs if d.user_id == student_id and d.attempt == attempt ]

    def _upload_step( self ):
        # Upload grades
        for g in self.graded:
            sub = self.get_submission_object( g[ 'student_id' ], g[ 'attempt' ] )[ 0 ]
            sub.update_score_and_comments( quiz_submissions=g[ 'data' ][ 'quiz_submissions' ] )


if __name__ == '__main__':
    # todo parse command line args into environment

    step = GradeQuiz()
    # step.run()
