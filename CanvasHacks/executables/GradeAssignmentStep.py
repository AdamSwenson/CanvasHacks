"""
Created by adam on 3/24/20
"""
__author__ = 'adam'


from CanvasHacks import environment
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Definitions.base import BlockableActivity
# todo Switch to assignment_new when ready
from CanvasHacks.GradingHandlers.factories import GradingHandlerFactory
from CanvasHacks.Models.model import StoreMixin
from CanvasHacks.Repositories.DataManagement import DataStoreNew
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository

from CanvasHacks.Repositories.submissions import SubmissionRepository, AssignmentSubmissionRepository


class GradeAssignment( StoreMixin ):
    """
    Executable which grades and uploads scores for all selected
    assignments

    Taken from the code in the assignment tools notebook which was created
    in CAN-44

    Created: CAN-44 / CAN-60
    """

    def __init__( self, activity=None, rest_timeout=5, no_late_penalty=True, upload_grades=True, **kwargs ):
        self.upload_grades = upload_grades
        self.wait = rest_timeout
        self.no_late_penalty = no_late_penalty
        if activity is None:
            # Use what's stored in environment
            selected_activities = environment.CONFIG.get_assignment_ids()
            # todo update to allow multiple selected activities
            activity_id = selected_activities[0]
            activity = environment.CONFIG.unit.get_activity_by_id(activity_id)

        self.activity = activity

        if self.no_late_penalty:
            self.activity.due_at = self.activity.lock_at

        self.graded = [ ]

        self.handle_kwargs( **kwargs )

    def _initialize( self ):
        """
        Handle instantiating and loading repositories
        :return:
        """
        self.workRepo = WorkRepositoryLoaderFactory.make( course=environment.CONFIG.course,
                                                          activity=self.activity,
                                                          rest_timeout=self.wait )


        self.assignment = environment.CONFIG.course.get_assignment( self.activity.id )

        self.subRepo = AssignmentSubmissionRepository( self.assignment )
        # shove the activity onto a sub repo so it will resemble
        # a quizrepo for the grader
        self.subRepo.activity = self.activity


        # Filter previously graded
        self.subRepo.data = [ s for s in self.subRepo.data if s.workflow_state != 'complete' ]
        self.workRepo.data = self.workRepo.data[ self.workRepo.data.workflow_state != 'complete' ].copy( deep=True )

        self.workRepo.data.reset_index( inplace=True )

        # We will need the association repo if the activity can be
        # blocked or graded by another student
        self.association_repo = None
        if isinstance( self.activity, BlockableActivity ):
            dao = SqliteDAO()
            self.association_repo = AssociationRepository( dao, self.activity )

    def run( self, **kwargs ):
        self.handle_kwargs( **kwargs )
        # Load data
        self._initialize()
        # Let the grader do its job
        grader = GradingHandlerFactory.make( activity=self.activity,
                                             work_repo=self.workRepo,
                                             submission_repo=self.subRepo,
                                             association_repo=self.association_repo )

        #     store.results = GT.new_determine_journal_credit(journal, subRepo)
        #     if GRADING_LATE:
        #         store.results = [j for j in store.results if j[0].grade != 'complete']

        # grader = assignmentGrader( work_repo=self.workRepo,
        #                      submission_repo=self.subRepo,
        #                      association_repo=self.association_repo )
        g = grader.grade( on_empty=0 )
        self.graded += g
        print( "Graded: ", len( self.graded ) )

        if self.upload_grades:
            self._upload_step()

    def get_submission_object( self, student_id, attempt ):
        """
        todo This really should be calling a method on the submission repo
        :param student_id:
        :param attempt:
        :return:
        """
        return [ d for d in self.subRepo.data if d.user_id == student_id and d.attempt == attempt ][0]

    def _upload_step( self ):
        self.uploaded = 0
        # Upload grades
        for g, pct_credit in self.graded:
            # call the put method on the returned canvas api submission
            score = "{}%".format(pct_credit)
            sub = self.get_submission_object( g[ 'student_id' ], g[ 'attempt' ] )
            sub.edit(submission={'posted_grade': score})
            self.uploaded += 1


if __name__ == '__main__':
    # todo parse command line args into environment

    step = GradeAssignment()
    # step.run()
