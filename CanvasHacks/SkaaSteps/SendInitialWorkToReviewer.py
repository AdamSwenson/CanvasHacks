"""
Created by adam on 2/23/20
"""
import pandas as pd

import CanvasHacks.testglobals
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions
from CanvasHacks.Errors.review_pairings import AllAssigned, NoAvailablePartner
# from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Logging.review_pairings import make_review_audit_file
from CanvasHacks.Logging.run_data import RunLogger
from CanvasHacks.Messaging.skaa import PeerReviewInvitationMessenger
from CanvasHacks.Repositories.status import InvitationStatusRepository
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep

__author__ = 'adam'

from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory


class SendInitialWorkToReviewer( IStep ):

    def __init__( self, course=None, unit=None, is_test=None, send=True, **kwargs ):
        """
        :param course:
        :param unit:
        :param is_test:
        :param send: Whether to actually send the messages
        """
        super().__init__( course, unit, is_test, send, **kwargs )

        # The activity whose results we are going to be doing something with
        self.activity = unit.initial_work

        # The activity which we are inviting the receiving student to complete
        self.activity_notifying_about = unit.review

        # The activity whose id is used to store review pairings for the whole SKAA
        self.activity_for_review_pairings = unit.initial_work

        self._initialize()

        # Initialize the relevant status repo
        self.invite_status_repo = InvitationStatusRepository( self.dao, self.activity_notifying_about )

        self.statusRepos = [ self.invite_status_repo]


    def run( self, **kwargs ):
        """
        Loads content assignments, assigns reviewers, and sends formatted
        work to reviewer
        Possible kwargs:
            only_new=False, Probably not used
            rest_timeout=5 Number of seconds to rest_timeout for canvas to generate report
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
            RunLogger.log_no_submissions( self.unit.initial_work )
            if CanvasHacks.testglobals.TEST:
                # Reraise so can see what happened for tests
                raise NoNewSubmissions

        except AllAssigned as e:
            # Folks already assigned to review
            # have somehow gotten past the new submissions filter
            # This could be due to them resubmitting late
            print( "New submitters but everyone already assigned" )
            # print( e.submitters )
            if CanvasHacks.testglobals.TEST:
                # Reraise so can see what happened for tests
                raise AllAssigned( e.submitters )

        except NoAvailablePartner as e:
            # We will probably want to notify the student that they
            # have had their work noticed, but they are now waiting for
            # a partner
            # todo Notify student that they are waiting
            print( "1 student has submitted and has no partner ") #, e.submitters )
            if CanvasHacks.testglobals.TEST:
                # Reraise so can see what happened for tests
                raise NoAvailablePartner( e.submitters )

    def _message_step( self ):
        # Send the work to the reviewers
        # Note that we still do this even if send is false because
        # the messenger will print out the messages rather than sending them
        self.messenger = PeerReviewInvitationMessenger( self.unit, self.studentRepo, self.work_repo, self.statusRepos )
        # NB, we don't use associationRepo.data because we only
        # want to send to people who are newly assigned
        self.messenger.notify( self.associations, self.send )
        # self.messenger.notify( self.associationRepo.data, self.send )
        #  todo Want some way of tracking if messages fail to send so can resend
        # Log the run
        msg = "Created {} peer review assignments \n {}".format( len( self.associations ), self.associations )
        RunLogger.log_reviews_assigned( self.activity_notifying_about, msg )

    def _assign_step( self ):
        # Assign reviewers to each submitter and store in db
        # NB, the repository will take care of removing already assigned
        # reviewers, so we just give them all submitters
        self.associations = self.associationRepo.assign_reviewers( self.work_repo.submitter_ids )
        if not self.is_test:
            # Save a more readable copy of all the assignments
            # to file
            make_review_audit_file( self.associationRepo, self.studentRepo, self.unit )

    def _load_step( self, **kwargs ):
        self.work_repo = WorkRepositoryLoaderFactory.make( self.activity, self.course, **kwargs )
        self.display_manager.initially_loaded = self.work_repo.data

        # hotfix needed to filter unsubmitted for non quiz ca
        self.work_repo.data = self.work_repo.data[ self.work_repo.data.workflow_state != 'unsubmitted' ]
        if isinstance( self.work_repo.data, pd.DataFrame ):
            self.work_repo.data = self.work_repo.data[ ~pd.isnull( self.work_repo.data.body ) ]

        self.display_manager.post_filter = self.work_repo.data

    @property
    def audit_frame( self ):
        return self.associationRepo.audit_frame( self.studentRepo )


if __name__ == '__main__':
    pass
