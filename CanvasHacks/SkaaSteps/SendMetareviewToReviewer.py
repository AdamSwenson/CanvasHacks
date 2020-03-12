"""
Created by adam on 2/23/20
"""
from CanvasHacks.Errors.review_pairings import NoReviewPairingsLoaded
from CanvasHacks.Logging.run_data import RunLogger
from CanvasHacks.Messaging.skaa import FeedbackFromMetareviewMessenger
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.status import FeedbackStatusRepository, InvitationStatusRepository
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep

__author__ = 'adam'


class SendMetareviewToReviewer( IStep ):

    def __init__( self, course=None, unit=None, is_test=None, send=True, **kwargs ):
        """
        :param course:
        :param unit:
        :param is_test:
        :param send: Whether to actually send the messages
        """
        super().__init__( course, unit, is_test, send, **kwargs )
        # The activity whose results we are going to be doing something with
        self.activity = unit.metareview

        # The activity which we are telling the student about
        # self.activity_notifying_about = unit.metareview

        # In sending the metareview results to the reviewer we are
        # telling the about the feedback on the review
        self.activity_feedback_on = unit.review

        # The activity_inviting_to_complete whose id is used to store review pairings for the whole SKAA
        self.activity_for_review_pairings = unit.initial_work

        self._initialize()

        self.feedback_status_repo = FeedbackStatusRepository(self.dao, self.activity_feedback_on, self.activity_for_review_pairings)

        self.statusRepos = [self.feedback_status_repo]

        self.associations = [ ]

    def run( self, **kwargs ):
        """
        Send feedback from the metareview to the person
        who completed the peer review
        :param only_new: Probably won't be used
        :param rest_timeout: Number of seconds to wait for canvas to generate report
        :return:
        """
        self._load_step( **kwargs )

        self._assign_step()

        self._message_step()

    def _message_step( self ):
        # Send
        self.messenger = FeedbackFromMetareviewMessenger( self.unit,
                                                          self.studentRepo,
                                                          self.work_repo,
                                                          self.statusRepos )
        self.messenger.notify( self.associations, self.send )
        # Log the run
        msg = "Sent {} metareview results \n {}".format( len( self.associations ), self.associations )
        # Note we are distributing the material for the metareview, that's
        # why we're using that activity_inviting_to_complete.
        RunLogger.log_metareview_feedback_distributed( self.unit.metareview, msg )

    def _assign_step( self ):
        # Filter out students who have already been notified.
        # NB, a step like this wasn't necessary in SendInitialWorkToReviewer
        # since we could filter by who doesn't have a review partner
        self._filter_notified()

        # Filter the review pairs to just those in the work repo.
        for student_id in self.work_repo.submitter_ids:
            # Work repo contains submitted meta reviews. Thus we look up
            # review pairings where a student submitting the metareview unit
            # is the assessee
            record = self.associationRepo.get_by_assessee( self.activity_for_review_pairings, student_id )
            if record is not None:
                self.associations.append( record )
        print( "Going to send metareview results for {} students".format( len( self.associations ) ) )
        if len( self.associations ) == 0:
            raise NoReviewPairingsLoaded

    def _load_step( self, **kwargs ):
        # Get work
        self.work_repo = WorkRepositoryLoaderFactory.make( self.activity, self.course, **kwargs )
        self.display_manager.initially_loaded = self.work_repo.data



    def _filter_notified( self ):
        """
        The downloaded store of student work contains reviews completed
        by every reviewer who has turned in the assignment.
        We need to remove reviewers who have already had their work sent to
        the original poster.
        That's the job of this method.
        :return:
        """
        records = self.feedback_status_repo.reviewers_with_authors_sent_feedback
        # We can remove those from the repo
        self.work_repo.remove_student_records( records )
        self.display_manager.post_filter = self.work_repo.data


if __name__ == '__main__':
    pass
