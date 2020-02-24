"""
Created by adam on 2/23/20
"""
from CanvasHacks.Repositories.quizzes import WorkRepositoryLoaderFactory
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep
from CanvasHacks.PeerReviewed.Notifications import FeedbackForMetareviewMessenger
__author__ = 'adam'




class SendReviewToReviewee(IStep):

    def __init__(self, course=None, unit=None, is_test=None, send=True, **kwargs):
        """
        :param course:
        :param unit:
        :param is_test:
        :param send: Whether to actually send the messages
        """
        super().__init__(**kwargs)
        self._initialize()

    def run(self, only_new=True):

        try:
            self.work_repo = WorkRepositoryLoaderFactory.make(self.unit.peer_review, self.course, only_new)
            # self.work_repo = make_quiz_repo( self.course, self.unit.initial_work )

            msgr = FeedbackForMetareviewMessenger(self.unit.metareview, self.studentRepo, self.work_repo )
            messages = msgr.notify(self.associationRepo.data, self.send)
            # todo logging of sent messages somewhere

        except Exception as e:
            print(e)



if __name__ == '__main__':
    pass