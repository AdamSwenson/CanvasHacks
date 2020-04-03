"""
Created by adam on 3/24/20
"""
__author__ = 'adam'

from CanvasHacks.Definitions.groups import ReviewType
from CanvasHacks.Definitions.journal import Journal
from CanvasHacks.GradingHandlers.assignment import AssignmentGrader
from CanvasHacks.GradingHandlers.journal import JournalGrader

if __name__ == '__main__':
    pass

# todo Switch to quiz_new when ready
from CanvasHacks.GradingHandlers.quiz import QuizGrader
from CanvasHacks.GradingHandlers.review import ReviewGrader


class GradingHandlerFactory:
    """
    Determines which sort of class which handles grading
    is needed and returns it
    """

    @staticmethod
    def make(  *args, **kwargs ):
        """
        Will likely contain
         work_repo=self.workRepo,
         submission_repo=self.subRepo,
         association_repo=self.association_repo

        :param args:
        :param kwargs:
        :return:
        """
        try:
            if isinstance(kwargs['activity'], ReviewType):
                return ReviewGrader(*args, **kwargs)

            if isinstance(kwargs['activity'], Journal):
                return JournalGrader(*args, **kwargs)

            if not kwargs['activity'].is_quiz_type:
                return AssignmentGrader(*args, **kwargs)

            return QuizGrader( *args, **kwargs )
        except KeyError:
            return QuizGrader(*args, **kwargs)

