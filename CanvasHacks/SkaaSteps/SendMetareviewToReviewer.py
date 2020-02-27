"""
Created by adam on 2/23/20
"""
from CanvasHacks.Logging.run_data import RunLogger
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep
from CanvasHacks.Messaging.Messengers import FeedbackFromMetareviewMessenger

__author__ = 'adam'



class SendMetareviewToReviewer(IStep):

    def __init__(self, course=None, unit=None, is_test=None, send=True, **kwargs):
        """
        :param course:
        :param unit:
        :param is_test:
        :param send: Whether to actually send the messages
        """
        super().__init__(course, unit, is_test, send, **kwargs)
        # The activity whose results we are going to be doing something with
        self.activity = unit.metareview

        # The activity which we are telling the student about
        self.activity_notifying_about = unit.metareview

        # The activity_inviting_to_complete whose id is used to store review pairings for the whole SKAA
        self.activity_for_review_pairings = unit.initial_work

        self._initialize()

    def run(self, only_new=True, rest_timeout=5):
        # Get work
        self.work_repo = WorkRepositoryLoaderFactory.make( self.activity, self.course, only_new, rest_timeout=rest_timeout )

        # Filter out students who have already been notified.
        # (NB, a step like this wasn't necessary in SendInitialWorkToReviewer
        # since we could filter by who doesn't have a review partner
        self.work_repo.remove_student_records( self.notificationStatusRepo.previously_sent_results )

        # Filter the review pairs to just those in the work repo.
        self.associations = [ ]
        for student_id in self.work_repo.submitter_ids:
            # Work repo contains submitted meta reviews. Thus we look up
            # review pairings where a student submitting the metareview assignment
            # is the assessee
            records = self.associationRepo.get_assessee_object( self.activity_for_review_pairings, student_id )
            self.associations.append( records )
        print( "Going to send metareview results for {} students".format( len( self.associations ) ) )

        # Send
        self.messenger = FeedbackFromMetareviewMessenger(self.unit, self.studentRepo, self.work_repo, self.notificationStatusRepo.record_sent_results )
        self.messenger.notify(self.associationRepo.data, self.send)

        # Log the run
        msg = "Sent {} metareview results \n {}".format( len( self.associations ), self.associations )
        # Note we are distributing the material for the metareview, that's
        # why we're using that activity_inviting_to_complete.
        RunLogger.log_metareview_feedback_distributed( self.unit.metareview, msg )


if __name__ == '__main__':
    pass