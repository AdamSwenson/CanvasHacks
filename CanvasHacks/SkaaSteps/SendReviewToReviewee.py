"""
Created by adam on 2/23/20
"""
from CanvasHacks.SkaaSteps.ISkaaSteps import IStep

__author__ = 'adam'

if __name__ == '__main__':
    pass



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

    def run(self):
        pass