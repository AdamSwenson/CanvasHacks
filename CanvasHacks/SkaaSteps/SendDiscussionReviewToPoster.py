"""
Created by adam on 3/2/20
"""
__author__ = 'adam'


from CanvasHacks.Errors.review_pairings import NoReviewPairingFound
from CanvasHacks.Messaging.discussions import FeedbackFromDiscussionReviewMessenger
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.status import StatusRepository, SentFeedbackStatusRepository
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

        # The activity which we are sending stuff about
        # NB, since both activity and activity_notifying_about are the discussion review
        # the initialization step will load the status repository which records when
        # people are sent feedback from their reviewer
        self.activity_notifying_about = unit.discussion_review

        # The activity whose id is used to store review pairings for the whole SKAA
        self.activity_for_review_pairings = unit.discussion_review
        # did it this way for unit 2; leaving commented version in case have to go back
        # self.activity_for_review_pairings = unit.discussion_forum

        self.associations = [ ]

        self._initialize()

        self.notificationStatusRepo = SentFeedbackStatusRepository( self.dao, self.activity_notifying_about )

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

        sent = self.messenger.notify( self.associations, self.send )
        self.display_manager.number_sent = sent

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
                # todo Handler for this situation
                pass

        self.display_manager.number_to_send = self.associations
        # print( "Going to send review results for {} students".format( len( self.associations ) ) )

    def _load_step( self, **kwargs ):
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
        records = self.notificationStatusRepo.reviewers_with_notified_authors
        # We can remove those from the repo
        self.work_repo.remove_student_records( records )
        self.display_manager.post_filter = self.work_repo.data

        # The load step has retrieved all submissions by reviewers
        # However, since the status repository records who has been sent
        # reviewer feedback, we need to get a list of submitters whose
        # work (feedback) has been sent to the author of the posts.
        # records = [ self.associationRepo.get_by_assessor( self.activity_for_review_pairings, sid ) for sid in self.work_repo.submitter_ids]
        #
        # # At this point, records contains a review pairing for everyone who has
        # # submitted the review (as the reviewer).
        #
        # # Now we make a list of reviewer ids whose feedback has already been sent out.
        # records = [r.assessor_id for r in records if self.notificationStatusRepo.has_received_message(r.assessee_id)]
        #
        # # Records now has the ids of reviewers whose assessee has previously
        # # received results.


        # NB, statusRepo.previously_sent_students contains a list of students
        # whose REVIEWS have been sent out. Thus we can use this directly
        # on the workRepo.data since that contains reviews
        # field has already been used when invited to do review
        # self.work_repo.remove_student_records( self.notificationStatusRepo.previously_sent_students )




if __name__ == '__main__':
    pass