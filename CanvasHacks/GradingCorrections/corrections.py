"""
Determines whether a score needs to be corrected
for various reasons
Created by adam on 3/9/20
"""
__author__ = 'adam'

from CanvasHacks.Errors.grading import StudentUnableToComplete
from CanvasHacks.Errors.review_pairings import NoReviewPairingFound
from CanvasHacks.GradingCorrections.base import IGradeCorrection
from CanvasHacks.Repositories.mixins import ObjectHandlerMixin

if __name__ == '__main__':
    pass


class ForfeitedPointsCorrector(IGradeCorrection):
    """
    Boosts student's score by the points their non turning in
    reviewer forfeited
    """

    def analyze( self, *args, **kwargs ):
        """

        :param args:
        :param kwargs:
        :return:
        """
        pass


class NonSubmittingStudentCorrector(ObjectHandlerMixin):
    """
    For assignments where a student's ability to complete it depends
    on other students doing something, this determines whether a correction
    is needed, e.g., if we're on a metareview but the reviewer never turned it in
    """

    def __init__(self, submissions_repo, pairing_repo):
        """
        :param dependency_work_repo: The assignment a student's ability to complete depends on
        :param pairing_repo: Review pairings that create the dependency
        """
        self.submissions_repo = submissions_repo
        self.pairing_repo = pairing_repo

        # The field in the repo that we will check to determine
        # whether the student depended on did the work
        self.completion_field = 'workflow_state'
        # The value the completion field will have if completed
        self.complete_value = 'submitted'
        self.incomplete_value = 'unsubmitted'


    # def is_able_to_complete( self, student ):
    #     """
    #     Looks up whether the provided student is/was able to complete
    #     the assignment.
    #
    #     Will raise exceptions to make it easier to bubble
    #     them up to various handlers (e.g., one which notifies the blocked
    #     and blocking student)
    #
    #     :param student: Student object or int
    #     :return: boolean
    #     :raises StudentUnableToComplete, NoReviewPairingFound
    #     """
    #     student_id = self._handle_id(student)
    #
    #     ra = self.pairing_repo.get_by_author(student_id)
    #     depends_on = ra.assessor_id
    #
    #     if depends_on is None:
    #         # todo If this is true the student was never assigned a reviewer, what should be done?
    #         raise NoReviewPairingFound(student_id)
    #         # return False
    #
    #     dependency_student_row = self.dependency_work_repo.get_student_work(student_id)
    #
    #     if dependency_student_row[self.completion_field] == self.complete_value:
    #         return True
    #
    #     raise StudentUnableToComplete(blocked_student=student_id, blocking_student=depends_on)
    #
