"""
Created by adam on 3/24/20
"""
__author__ = 'adam'


from CanvasHacks import environment
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Definitions.base import BlockableActivity
# todo Switch to assignment_new when ready
from CanvasHacks.GradingHandlers.assignment import AssignmentGraderPoints
from CanvasHacks.GradingHandlers.factories import GradingHandlerFactory
from CanvasHacks.Logging.grade_composition import log_points
from CanvasHacks.Models.model import StoreMixin
from CanvasHacks.Repositories.DataManagement import DataStoreNew
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from CanvasHacks.Repositories.students import StudentRepository

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
        """

        :param activity:
        :param rest_timeout:
        :param no_late_penalty:
        :param upload_grades: If false, does a dry run without uploading or otherwise
        recording scores. If true, uploads to canvas.
        :param kwargs:
        """
        self.upload_grades = upload_grades
        self.rest_timeout = rest_timeout
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
        """Holds submission, score tuples for use in uploading"""

        self.grade_records = []
        """List of PointsRecord objects. Each holds details of a student's points and the methods which assigned them. [Added CAN-72]"""


        self.handle_kwargs( **kwargs )

    def _initialize( self ):
        """
        Handle instantiating and loading repositories
        :return:
        """
        self.workRepo = WorkRepositoryLoaderFactory.make( course=environment.CONFIG.course,
                                                          activity=self.activity,
                                                          rest_timeout=self.rest_timeout )


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

        # Create a student repository that will mainly be used for logging
        # and perhaps messaging
        self.studentRepo = StudentRepository( environment.CONFIG.course )
        self.studentRepo.download()


    def run( self, **kwargs ):
        self.handle_kwargs( **kwargs )
        # Load data
        self._initialize()
        # Let the grader do its job
        grader = GradingHandlerFactory.make( activity=self.activity,
                                             work_repo=self.workRepo,
                                             submission_repo=self.subRepo,
                                             association_repo=self.association_repo,
                                             no_late_penalty=self.no_late_penalty)

        # Grader returns tuple of lists ( [(submission, points/pct credit)], [PointsRecord]
        # If the grader is non-points-based, it will return an empty list for grade_records
        g, grade_records = grader.grade( on_empty=0 )
        self.graded += g
        self.grade_records += grade_records

        print(f"Graded {len( self.graded )} assignments"  )


        if self.upload_grades:

            # Write the details of how each score total was arrived at to log file
            self.log_point_bases( is_dry_run=False )

            if isinstance(grader, AssignmentGraderPoints):
                self._upload_step_points()
            else:
                self._upload_step_percentage()

            print(f"Uploaded {self.uploaded} grades")

        else:
            print("This was a dry run. No scores uploaded")
            self.log_point_bases( is_dry_run=True )

    def get_submission_object( self, student_id, attempt ):
        """
        todo This really should be calling a method on the submission repo
        :param student_id:
        :param attempt:
        :return:
        """
        return [ d for d in self.subRepo.data if d.user_id == student_id and d.attempt == attempt ][0]

    def _upload_step_percentage( self ):
        """
        Handles uploading where the score will be sent as
        a percentage of the total possible points
        :return:
        """
        print("Uploading scores as percentage of total possible points")

        self.uploaded = 0
        # Upload grades
        for g, pct_credit in self.graded:
            # call the put method on the returned canvas api submission
            score = "{}%".format(pct_credit)
            sub = self.get_submission_object( g[ 'student_id' ], g[ 'attempt' ] )
            sub.edit(submission={'posted_grade': score})
            self.uploaded += 1

    def _upload_step_points( self ):
        """
        Handles uploading where the score will be sent as a float of
        total points
        :return:
        """
        print("Uploading scores as points")

        self.uploaded = 0
        # Upload grades
        for g, score in self.graded:
            # call the put method on the returned canvas api submission
            # score = "{}%".format(pct_credit)
            sub = self.get_submission_object( g[ 'student_id' ], g[ 'attempt' ] )
            sub.edit(submission={'posted_grade': score})
            self.uploaded += 1


    def log_point_bases( self, is_dry_run):
        """Writes the details of how points were determined to
        the logfile.
        NB, this happens before uploading (and still happens when uploading is turned
        off)
        """
        # Add student names to the records before logging
        for g in self.grade_records:
            g.student_name = self.studentRepo.get_student_name(g.student_id)

            # todo Add email too if the log will be used in messaging. Points record is set up to handle this by setting g.student_email


        log_points(self.activity, self.grade_records, is_dry_run=is_dry_run)


if __name__ == '__main__':
    # todo parse command line args into environment

    step = GradeAssignment()
    # step.run()
