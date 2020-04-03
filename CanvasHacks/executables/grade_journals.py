"""
Created by adam on 3/29/20
"""
__author__ = 'adam'

from CanvasHacks import environment
from CanvasHacks.Definitions.journal import Journal
from CanvasHacks.Models.model import StoreMixin


# todo dev

class GradeJournalStep(StoreMixin):
    """
    Executes the entire grading process for journals
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

    def run( self, **kwargs ):

        from CanvasHacks.Repositories.submissions import SubmissionRepository
        results = [ ]

        for a in environment.CONFIG.assignments:
            # canvas api object
            assignment = self.course.get_assignment( int( a[ 0 ] ) )
            # activity object to define the features
            journal = Journal( **assignment.attributes )
            # Download submissions
            subRepo = SubmissionRepository( assignment )
            # parse out already graded submissions
            subRepo.data = [ j for j in subRepo.data if j.grade != 'complete' ]

            # shove the activity onto a sub repo so it will resemble
            # a quizrepo for the grader
            subRepo.activity = journal
            # Initialize the package for results
            store = DataStoreNew( journal )
            # provisionally determine credit
            grader = JournalGrader( subRepo )
            store.results = grader.grade()
            #     store.results = GT.new_determine_journal_credit(journal, subRepo)
            #     if GRADING_LATE:
            #         store.results = [j for j in store.results if j[0].grade != 'complete']

            results.append( store )

    def _upload_step( self ):

        self._log_uploaded()

    def _log_uploaded( self ):
        """
        Prints or writes to file what happened during upload
        :return:
        """
        stem = "Grades uploaded for {} students "
        print( stem.format( self.uploaded ) )


if __name__ == '__main__':
    pass