"""
Defines things which raise or lower a students' score
on one assignment by how they were rated by another
student on a different assignment

Created by adam on 3/16/20
"""
__author__ = 'adam'

from CanvasHacks.DAOs.mixins import DaoMixin
from CanvasHacks.GradingCorrections.base import IGradeCorrection
from CanvasHacks.GradingMethods.base import IGradingMethod
from CanvasHacks.Models.model import StoreMixin
from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from CanvasHacks import environment


class ReviewBased( IGradingMethod, StoreMixin, DaoMixin ):

    def __init__( self, graded_activity: Activity, review_activity: Activity, review_columns: list, pct_of_score=1, **kwargs ):
        """

        :param graded_activity: Activity whose grade depends on review
        :param review_activity: Activity where the reviewer gave scores
        :param review_columns: Columns in the review activity to use
        """
        self.pct_of_score = pct_of_score
        self.graded_activity = graded_activity
        self.activity = graded_activity
        self.review_columns = review_columns
        self.review_activity = review_activity


        # todo make this a param or variable...
        self.valmap = {
            'strongly agree' : 1,
            'agree' : 0.9,
            'disagree': 0.5,
            'strongly disagree': 0.1
        }

        self.handle_kwargs(**kwargs)

        self._initialize()


    def _initialize( self ):
        self._initialize_db()
        self.pairingsRepo = AssociationRepository(self.dao, self.graded_activity)
        self.review_repo = WorkRepositoryLoaderFactory.make(course=environment.CONFIG.course,
                                                            activity=self.review_activity,
                                                            rest_timeout=5)


    def grade( self, student_id ):
        # todo assume only one column for now
        col = self.review_columns[0]
        ra = self.pairingsRepo.get_by_author(student_id)
        reviewer_work = self.review_repo.get_student_work(ra.assessor_id)
        v = reviewer_work[col] #.value

        # reformat so don't blow up if i use different caps
        v = v.strip().lower()

        return self.valmap.get(v)


if __name__ == '__main__':
    pass
