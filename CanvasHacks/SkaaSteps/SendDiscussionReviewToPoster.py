"""
Created by adam on 3/2/20
"""
__author__ = 'adam'


from CanvasHacks.Errors.review_pairings import NoReviewPairingFound
from CanvasHacks.Messaging.discussions import FeedbackFromDiscussionReviewMessenger
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.status import StatusRepository
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep
from CanvasHacks.Messaging.skaa import MetareviewInvitationMessenger
from CanvasHacks.Logging.run_data import RunLogger
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions

__author__ = 'adam'


class SendDiscussionReviewToPoster(IStep):
    """Handles loading the submitted reviews and routing them to the authors
    """

    def __init__(self, course=None, unit=None, is_test=None, send=True, **kwargs):
        """
        :param course:
        :param unit:
        :param is_test:
        :param send: Whether to actually send the messages
        """
        super().__init__(course, unit, is_test, send, **kwargs)
        # The activity whose results we are going to be doing something with
        self.activity = unit.discussion_review

        # The activity_inviting_to_complete which we are inviting the receiving student to complete
        self.activity_notifying_about = unit.discussion_review

        # The activity_inviting_to_complete whose id is used to store review pairings for the whole SKAA
        self.activity_for_review_pairings = unit.discussion_review

        self.associations = [ ]

        self._initialize()

    def run(self, **kwargs):
        """
        Retrieves submitted reviews and sends themto the authors
        along with instructions for metareview
        only_new=False, rest_timeout=5
        :param rest_timeout:
        :param only_new:
        :return:
        """
        try:
            self._load_step( **kwargs)

            self._assign_step()

            self._message_step()

        except NoNewSubmissions:
            # Check if new submitters, bail if not
            print( "No new submissions" )
            # todo Log run failure
            RunLogger.log_no_submissions(self.activity)

        except Exception as e:
            print(e)

    def _message_step( self ):
        # Handle sending the results of the review to the original author
        self.messenger = FeedbackFromDiscussionReviewMessenger( self.unit, self.studentRepo, self.work_repo, self.notificationStatusRepo )
        self.messenger.notify( self.associations, self.send )

        # Log the run
        msg = "Sent {} peer review results \n {}".format( len( self.associations ), self.associations )
        # Note we are distributing the material for the metareview, that's
        # why we're using that activity_inviting_to_complete.
        RunLogger.log_review_feedback_distributed( self.unit.discussion_review, msg )

    def _assign_step( self ):
        """
        Do stuff with the review assignments
        :return:
        """
        # Filter the review pairs to just those in the work repo.
        for student_id in self.work_repo.submitter_ids:
            try:
                # Work repo contains submitted peer reviews. Thus we look up
                # review pairings where a student submitting the peer review assignment
                # is the assessor
                records = self.associationRepo.get_by_assessor( self.activity_for_review_pairings, student_id )

                if records is None:
                    raise NoReviewPairingFound(student_id)
                else:
                    self.associations.append( records )
            except NoReviewPairingFound:
                pass

        print( "Going to send review results for {} students".format( len( self.associations ) ) )

    def _load_step( self, **kwargs ):
        self.work_repo = WorkRepositoryLoaderFactory.make( self.activity, self.course, **kwargs )
        # self.work_repo = make_quiz_repo( self.course, self.unit.initial_work )
        prelen = len(self.work_repo.data)
        print("Loaded work by {} students from {}".format(prelen, self.activity.name))
        # Filter out students who have already been notified.
        # (NB, a step like this wasn't necessary in SendInitialWorkToReviewer
        # since we could filter by who doesn't have a review partner
        self.work_repo.remove_student_records( self.notificationStatusRepo.previously_notified_students )
        postlen = len(self.work_repo.data)
        print("Filtered out {} students who have already been notified".format(prelen - postlen))



if __name__ == '__main__':
    pass