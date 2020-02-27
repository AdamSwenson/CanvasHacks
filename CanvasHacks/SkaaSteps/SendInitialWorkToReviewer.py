"""
Created by adam on 2/23/20
"""
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions
from CanvasHacks.Errors.review_pairings import AllAssigned, NoAvailablePartner
from CanvasHacks.Logging.run_data import RunLogger
from CanvasHacks.Messaging.Messengers import StudentWorkForPeerReviewMessenger
# from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Logging.review_pairings import make_review_audit_file
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
        self._initialize()

    def run( self, only_new=False ):
        """
        Loads content assignments, assigns reviewers, and sends formatted
        work to reviewer
        :param only_new:
        :return:
        """
        try:
            self.work_repo = WorkRepositoryLoaderFactory.make( self.unit.initial_work, self.course, only_new )
            # self.work_repo = make_quiz_repo( self.course, self.unit.initial_work )

            # Assign reviewers to each submitter and store in db
            # NB, assocs will be
            self.new_assignments = self.associationRepo.assign_reviewers( self.work_repo.submitter_ids )

            if not self.is_test:
                # Save a more readable copy of all the assignments
                # to file
                make_review_audit_file( self.associationRepo, self.unit )

            # Send the work to the reviewers
            # Note that we still do this even if send is false because
            # the messenger will print out the messages rather than sending them
            self.messenger = StudentWorkForPeerReviewMessenger( self.unit.review, self.studentRepo, self.work_repo, self.statusRepo )

            # NB, we don't use associationRepo.data because we only
            # want to send to people who are newly assigned
            self.messenger.notify(self.new_assignments, self.send)
            # self.messenger.notify( self.associationRepo.data, self.send )
            #  todo Want some way of tracking if messages fail to send so can resend

            # Log the run
            msg = "Created {} peer review assignments \n {}".format(len(self.new_assignments), self.new_assignments)
            RunLogger.log_reviews_assigned(self.unit.review, msg)

        except NoNewSubmissions:
            # Check if new submitters, bail if not
            print( "No new submissions" )
            # todo Log run failure
            RunLogger.log_no_submissions(self.unit.initial_work)

        except AllAssigned as e:
            # Folks already assigned to review
            # have somehow gotten past the new submissions filter
            # This could be due to them resubmitting late
            print("New submitters but everyone already assigned")
            print(e.submitters)

        except NoAvailablePartner as e:
            # We will probably want to notify the student that they
            # have had their work noticed, but they are now waiting for
            # a partner
            # todo Notify student that they are waiting
            print("1 student has submitted and has no partner ", e.submitters)

    @property
    def audit_frame( self ):
        return self.associationRepo.audit_frame(self.studentRepo)



if __name__ == '__main__':
    pass
