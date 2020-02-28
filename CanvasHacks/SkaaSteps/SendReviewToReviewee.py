"""
Created by adam on 2/23/20
"""
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.status import StatusRepository
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep
from CanvasHacks.Messaging.Messengers import MetareviewInvitationMessenger
from CanvasHacks.Logging.run_data import RunLogger
from CanvasHacks.Errors.data_ingestion import NoNewSubmissions

__author__ = 'adam'


class SendReviewToReviewee(IStep):
    """Handles loading the submitted reviews and routing them to the authors'
    with instructions for completing the metareview
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
        self.activity = unit.review

        # The activity_inviting_to_complete which we are inviting the receiving student to complete
        self.activity_notifying_about = unit.metareview

        # The activity_inviting_to_complete whose id is used to store review pairings for the whole SKAA
        self.activity_for_review_pairings = unit.initial_work

        self._initialize()

    def run(self, only_new=False, rest_timeout=5):
        """
        Retrieves submitted reviews and sends themto the authors
        along with instructions for metareview
        :param rest_timeout:
        :param only_new:
        :return:
        """
        try:
            self.work_repo = WorkRepositoryLoaderFactory.make(self.activity, self.course, only_new=only_new, rest_timeout=rest_timeout)
            # self.work_repo = make_quiz_repo( self.course, self.unit.initial_work )

            # Filter out students who have already been notified.
            # (NB, a step like this wasn't necessary in SendInitialWorkToReviewer
            # since we could filter by who doesn't have a review partner
            self.work_repo.remove_student_records(self.notificationStatusRepo.previously_notified_students)

            # Filter the review pairs to just those in the work repo.
            self.associations = []
            for student_id in self.work_repo.submitter_ids:
                # Work repo contains submitted peer reviews. Thus we look up
                # review pairings where a student submitting the peer review assignment
                # is the assessor
                records = self.associationRepo.get_by_assessor(self.activity_for_review_pairings, student_id)

                # records = self.associationRepo.get_assessor_object(self.activity_for_review_pairings, student_id)
                self.associations.append(records)
            print("Going to send review results for {} students".format(len(self.associations)))

            # Handle sending the results of the review to the original author
            # so they can do the metareview
            self.messenger = MetareviewInvitationMessenger( self.unit, self.studentRepo, self.work_repo, self.notificationStatusRepo )

            self.messenger.notify(self.associations, self.send)
            # messages = self.messenger.notify(self.associationRepo.data, self.send)

            # Log the run
            msg = "Sent {} peer review results \n {}".format(len(self.associations), self.associations)
            # Note we are distributing the material for the metareview, that's
            # why we're using that activity_inviting_to_complete.
            RunLogger.log_review_feedback_distributed(self.unit.metareview, msg)

        except NoNewSubmissions:
            # Check if new submitters, bail if not
            print( "No new submissions" )
            # todo Log run failure
            RunLogger.log_no_submissions(self.unit.review)

        except Exception as e:
            print(e)



if __name__ == '__main__':
    pass