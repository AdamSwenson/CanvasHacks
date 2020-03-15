"""
Created by adam on 2/23/20
"""
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions
from CanvasHacks.Errors.review_pairings import NoReviewPairingFound
from CanvasHacks.Logging.run_data import RunLogger
from CanvasHacks.Messaging.skaa import MetareviewInvitationMessenger
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.status import FeedbackStatusRepository, InvitationStatusRepository
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep

__author__ = 'adam'


class SendReviewToReviewee( IStep ):
    """Handles loading the submitted reviews and routing them to the authors'
    with instructions for completing the metareview
    """

    def __init__( self, course=None, unit=None, is_test=None, send=True, **kwargs ):
        """
        :param course:
        :param unit:
        :param is_test:
        :param send: Whether to actually send the messages
        """
        super().__init__( course, unit, is_test, send, **kwargs )
        # The activity whose results we are going to be doing something with
        self.activity = unit.review

        # The activity which we are inviting the receiving student to complete
        self.activity_notifying_about = unit.metareview

        # In sending the review results to the author we are
        # telling the about the feedback on the original assignment
        self.activity_feedback_on = unit.initial_work

        # The activity whose id is used to store review pairings for the whole SKAA
        self.activity_for_review_pairings = unit.initial_work

        self.associations = [ ]

        self._initialize()

        # Initialize the relevant status repos

        self.feedback_status_repo = FeedbackStatusRepository(self.dao, self.activity_feedback_on, self.activity_for_review_pairings)

        self.invite_status_repo = InvitationStatusRepository(self.dao, self.activity_notifying_about)

        self.statusRepos = [self.invite_status_repo, self.feedback_status_repo]

    def run( self, **kwargs ):
        """
        Retrieves submitted reviews and sends themto the authors
        along with instructions for metareview
        only_new=False, rest_timeout=5
        :param rest_timeout:
        :param only_new:
        :return:
        """
        try:
            self._load_step( **kwargs )

            self._assign_step()

            self._message_step()

        except NoNewSubmissions:
            # Check if new submitters, bail if not
            print( "No new submissions" )
            # todo Log run failure
            RunLogger.log_no_submissions( self.activity )

        except Exception as e:
            print( e )

    def _message_step( self ):
        # Handle sending the results of the review to the original author
        # so they can do the metareview
        self.messenger = MetareviewInvitationMessenger( self.unit, self.studentRepo, self.work_repo, self.statusRepos )

        self.messenger.notify( self.associations, self.send )

        # Log the run
        msg = "Sent {} peer review results to authors".format( len( self.associations ))
        print(msg)

        lmsg = "{} \n {}".format(msg, self.associations )
        # Note we are distributing the material for the metareview, that's
        # why we're using that activity_inviting_to_complete.
        RunLogger.log_review_feedback_distributed( self.unit.metareview, lmsg )

    def _assign_step( self ):
        self._filter_notified()

        # Filter the review pairs to just those in the work repo.
        for student_id in self.work_repo.submitter_ids:
            try:
                # Work repo contains submitted peer reviews. Thus we look up
                # review pairings where a student submitting the peer review assignment
                # is the assessor
                records = self.associationRepo.get_by_assessor( self.activity_for_review_pairings, student_id )

                if records is None:
                    raise NoReviewPairingFound( student_id )
                else:
                    self.associations.append( records )
            except NoReviewPairingFound:
                pass

        print( "Going to send review results for {} students".format( len( self.associations ) ) )

    def _load_step( self, **kwargs ):
        self.work_repo = WorkRepositoryLoaderFactory.make( self.activity, self.course, **kwargs )
        self.display_manager.initially_loaded = self.work_repo.data

    def _filter_notified( self ):
        """
        Filter out students who have already been invited to
        complete the metareview.
        (NB, a step like this wasn't necessary in SendInitialWorkToReviewer
        since we could filter by who doesn't have a review partner

        :return:
        """
        records = self.feedback_status_repo.reviewers_with_authors_sent_feedback
        self.work_repo.remove_student_records( records )
        self.display_manager.post_filter = self.work_repo.data



if __name__ == '__main__':
    pass
