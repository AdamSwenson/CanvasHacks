"""
Created by adam on 2/23/20
"""
from CanvasHacks.Repositories.quizzes import WorkRepositoryLoaderFactory
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep
from CanvasHacks.Messaging.Messengers import FeedbackForMetareviewMessenger
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
        self._initialize()

    def run(self, only_new=False):
        """
        Retrieves submitted reviews and sends themto the authors
        along with instructions for metareview
        :param only_new:
        :return:
        """
        try:
            self.work_repo = WorkRepositoryLoaderFactory.make(self.unit.review, self.course, only_new)
            # self.work_repo = make_quiz_repo( self.course, self.unit.initial_work )

            self.messenger = FeedbackForMetareviewMessenger(self.unit.metareview, self.studentRepo, self.work_repo )

            # todo probably going to want to do something to filter the review pairs to just those in the work repo...
            self.associations = []
            for student_id in self.work_repo.submitter_ids:
                # Work repo contains submitted peer reviews. Thus we look up
                # review pairings where a student submitting the peer review assignment
                # is the assesor
                assoc = self.associationRepo.get_assessor(self.unit.initial_work, student_id)
                self.associations.append(assoc)
            print("Going to send review results for {} students".format(len(self.associations)))
            # get
            self.messenger.notify(self.associations, self.send)
            # messages = self.messenger.notify(self.associationRepo.data, self.send)

            # Log the run
            msg = "Sent {} peer review results \n {}".format(len(self.associations), self.associations)
            # Note we are distributing the material for the metareview, that's
            # why we're using that activity.
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