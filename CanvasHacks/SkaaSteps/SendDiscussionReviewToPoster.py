"""
Created by adam on 3/2/20
"""
__author__ = 'adam'


from CanvasHacks.Errors.review_pairings import NoReviewPairingFound
from CanvasHacks.Messaging.discussions import FeedbackFromDiscussionReviewMessenger
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.status import StatusRepository, FeedbackStatusRepository
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

        # The activity which we are sending feedback about
        self.activity_notifying_about = unit.discussion_review

        # The activity whose id is used to store review pairings for the whole SKAA
        # We use the discussion review so that the association repo records,
        # invite status records and feedback status records will have the same
        # id, which makes reasoning about them easier
        self.activity_for_review_pairings = unit.discussion_review

        # did it this way for unit 2; leaving commented version in case have to go back
        # self.activity_for_review_pairings = unit.discussion_forum

        self.associations = [ ]

        self._initialize()

        self.feedback_status_repo = FeedbackStatusRepository( self.dao, self.activity_notifying_about )
        self.statusRepos = [self.feedback_status_repo]

    def run(self, **kwargs):
        """
        Retrieves submitted reviews and sends them to the authors
        along with instructions for metareview
        Possible kwarg parameters include:
            only_new=False
            rest_timeout=5
        :return:
        """
        try:
            self._load_step( **kwargs)

            self._assign_step()

            self._message_step()

        except NoNewSubmissions:
            # Check if new submitters, bail if not
            print( "No new submissions" )
            RunLogger.log_no_submissions(self.activity)

        except Exception as e:
            print(e)

    def _message_step( self ):
        """
        Handle sending the results of the review to the original author
        :return:
        """
        self.messenger = FeedbackFromDiscussionReviewMessenger( self.unit, self.studentRepo, self.work_repo, self.statusRepos )

        sent = self.messenger.notify( self.associations, self.send )
        self.display_manager.number_sent = sent

        # Log the run
        msg = "Sent {} peer review results \n {}".format( len( self.associations ), self.associations )
        # Note we are distributing the material for the metareview, that's
        # why we're using that activity_inviting_to_complete.
        RunLogger.log_review_feedback_distributed( self.activity_notifying_about, msg )

    def _assign_step( self ):
        """
        Do stuff with the review assignments
        :return:
        """
        self._filter_notified()

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
                print("No review pairing fround for student id {} ".format(student_id))
                # todo Handler for this situation

        self.display_manager.number_to_send = self.associations

    def _load_step( self, **kwargs ):
        """
        Loads applicable data
        kwarg params may include
            download=True/False (default true): Whether to download or load from disk
        :param kwargs:
        :return:
        """
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