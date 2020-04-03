"""
Created by adam on 3/10/20
"""
__author__ = 'adam'

import pandas as pd
from canvasapi.quiz import QuizSubmission
from canvasapi.submission import Submission

if __name__ == '__main__':
    pass


class UncheckableDataProvidedError(Exception):
    """A filtration class has been provided with something
    it can't check"""
    pass


class IReadinessFilter:

    def is_ready( self, item ):
        raise NotImplementedError

    def _is_blocked_by_workflow_state( self, state ):
        """Given a value in a workflow_state field, returns
        what should do about it
        :return: Boolean or None if cannot determine
        """
        states = {
            # Workflow states found in attribute of canvas object
            'untaken': True,
            'pending_review': False,
            'complete': True,
            'settings_only': True,
            'preview': True
        }

        return states.get( state, None )

class ReadinessFilterFactory:

    @staticmethod
    def make( item ):
        """
        Determine what filter to return
        :param item:
        :return:
        """
        if isinstance(item, pd.Series):
            return FrameRowReadinessFilter()

        if isinstance( item, Submission ):
            return SubmissionReadinessFilter()

        if isinstance( item, QuizSubmission ):
            return QuizSubmissionReadinessFilter()

        raise UncheckableDataProvidedError(item)


class SubmissionReadinessFilter(IReadinessFilter):
    """
    Checks whether a Canvas api submission object
    represents something which is ready to be acted upon
    """

    def is_ready( self, item ):
        """
        Identifies assignments which have been previously graded
        :return: Boolean
        """
        try:
            # If the item is graded incomplete/complete
            # having the grade 'complete' means that
            # the item has been handled
            if item.grade == 'complete':
                return False
            # Other varients of grade should go here
            # or can we just check for none

            return not self._is_blocked_by_workflow_state( item.workflow_state )

        except AttributeError:
            # can't tell what to do
            raise UncheckableDataProvidedError(item)


class FrameRowReadinessFilter(IReadinessFilter):

    def is_ready( self, item, question_columns=None ):
        """
        If we've been given a data frame row,
        it will be a Series. Check whether it
        shows the person is unready
        :param item:
        :return:
        """
        if 'workflow_state' in item.index:
            if item.workflow_state == 'unsubmitted':
                return False
            # If the value is 'submitted' it could still be unready
            # so we continue

        # Any other column values based tests should go here.

        try:
            # Returning Boolean because assume that all other
            # possible conditions have been checked above

            if question_columns is not None:
                # If all the question columns are empty
                # it should be left alone
                for c in question_columns:
                    if len( item[ 0 ] ) > 0:
                        # Something contains at least one character
                        return True
                # All columns are empty
                return False

        except AttributeError:
            raise UncheckableDataProvidedError(item)


class QuizSubmissionReadinessFilter(IReadinessFilter):

    def is_ready( self, item ):
        return item.overdue_and_needs_submission



#
# class UnreadyFilterMixin:
#     """Tools for filtering out
#     previously graded and unsubmitted work from
#     any type of assignment.
#
#     These are for detecting based on server-side info; does not check my app. Detecting
#     whether they have been, e.g., assigned a reviewer is handled
#     elsewhere.
#
#     Private methods will return either True, False, or None
#     They will return None if the method is unable to make a determination
#
#     Public methods will return only True or False
#     """
#
#     # def check( self, item ):
#
#     def _is_blocked_by_workflow_state( self, state ):
#         """Given a value in a workflow_state field, returns
#         what should do about it
#         :return: Boolean or None if cannot determine
#         """
#         states = {
#             # Workflow states found in reports
#             'submitted': False,
#             'unsubmitted': True,
#
#             # Workflow states found in attribute of canvas object
#             'untaken': True,
#             'pending_review': False,
#             'complete': True,
#             'settings_only': True,
#             'preview': True
#         }
#
#         return states.get( state, None )
#
#
#
#     def is_ready( self, item ):
#         """
#         Main method which handles all they type checks
#         behind the scenes, to simply return a boolean of whether
#         the piece of work is ready to be acted on
#         :param item:
#         :return: Boolean
#         """
#         if isinstance(item, pd.Series):
#             return self._frame_row_blocks(item)
#
#         if isinstance( item, Submission ):
#             return self._submission_blocks( item )
#
#
#         #
#         # r = self._is_graded( item )
#         # if r is True:
#         #     return False
#         # # continue
#         #
#         # r2 = self._is_unsubmitted( item )
#         # if r2 is True:
#         #     return False
#         #
#         # r3 = self._is_blocked_by_workflow_state( item )
#         # if r3 is True:
#         #     return False
#
#         return not self._is_graded( item ) and not self._is_unsubmitted( item )
