"""
Created by adam on 2/23/20
"""
from CanvasHacks.QuizReportFileTools import make_quiz_repo
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep
from CanvasHacks.PeerReviewed.Notifications import FeedbackFromMetareviewMessenger

__author__ = 'adam'



class SendMetareviewToReviewer(IStep):

    def __init__(self, course=None, unit=None, is_test=None, send=True, **kwargs):
        """
        :param course:
        :param unit:
        :param is_test:
        :param send: Whether to actually send the messages
        """
        super().__init__(**kwargs)
        self._initialize()

    def run(self):
        # Get work
        self.work_repo = make_quiz_repo( self.course, self.unit.review )
        self.work_repo._fix_forgot_answers()

        # Send
        msgr = FeedbackFromMetareviewMessenger(self.unit.metareview, self.studentRepo, self.work_repo )
        msgr.notify(self.associationRepo.data, self.send)


if __name__ == '__main__':
    pass