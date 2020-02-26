"""
Created by adam on 2/23/20
"""
from CanvasHacks.Repositories.quizzes import WorkRepositoryLoaderFactory
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
        self._initialize()

    def run(self, only_new=True):
        # Get work
        self.work_repo = WorkRepositoryLoaderFactory.make( self.unit.initial_work, self.course, only_new )

        # self.work_repo = make_quiz_repo( self.course, self.unit.review )
        self.work_repo._fix_forgot_answers()

        # Send
        self.messenger = FeedbackFromMetareviewMessenger(self.unit.metareview, self.studentRepo, self.work_repo )
        self.messenger.notify(self.associationRepo.data, self.send)


if __name__ == '__main__':
    pass