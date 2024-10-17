"""
Defines things which raise or lower a students' score
on one assignment by how they were rated by another
student on a different assignment

Created by adam on 3/16/20
"""
__author__ = 'adam'

from CanvasHacks.DAOs.mixins import DaoMixin
from CanvasHacks.GradingCorrections.base import IGradeCorrection
from CanvasHacks.GradingMethods.base import IGradingMethod, IGradingMethodPoints
from CanvasHacks.GradingMethods.errors import InvalidReviewPointValue, UngradableActivity, WaitingForReviewerToSubmit
from CanvasHacks.Models.model import StoreMixin
from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.Repositories.factories import WorkRepositoryLoaderFactory
from CanvasHacks.Repositories.reviewer_associations import AssociationRepository
from CanvasHacks import environment


class ReviewBasedLikert( IGradingMethodPoints, StoreMixin, DaoMixin ):
    """Provides the portion of an assignment grade determined by the reviewer's responses
    where the reviewer's responses were entered as a likert score."""


    LIKERT_VALMAP = {
        'strongly agree': 1,
        'agree': 0.9,
        'disagree': 0.5,
        'strongly disagree': 0.1
    }

    def __init__( self, graded_activity: Activity, review_activity: Activity, review_columns: list, pct_of_score=1, **kwargs ):
        """

        :param graded_activity: Activity whose grade depends on review
        :param review_activity: Activity where the reviewer gave scores
        :param review_columns: Columns in the review activity to use. todo Presently assumes only 1 value in list
        """
        super().__init__()

        self.pct_of_score = pct_of_score
        self.graded_activity = graded_activity
        self.activity = graded_activity
        self.review_columns = review_columns
        self.review_activity = review_activity


        # todo make this a param or variable...
        self.valmap = self.LIKERT_VALMAP

        self.handle_kwargs(**kwargs)

        self._initialize()


    def _initialize( self ):
        self._initialize_db()
        self.pairingsRepo = AssociationRepository(self.dao, self.graded_activity)
        self.review_repo = WorkRepositoryLoaderFactory.make(course=environment.CONFIG.course,
                                                            activity=self.review_activity,
                                                            rest_timeout=5)

    def grade( self, author_id ):
        """
        Returns grade based on peer review
        :param author_id: The author's canvas id
        :return:
        """
        # todo assume only one column for now
        col = self.review_columns[0]
        ra = self.pairingsRepo.get_by_author( author_id )
        reviewer_work = self.review_repo.get_student_work(ra.assessor_id)
        v = reviewer_work[col] #.value

        # reformat the likert response so don't blow up if i use different caps
        v = v.strip().lower()

        return self.valmap.get(v)



class ReviewBasedPoints( IGradingMethodPoints, StoreMixin, DaoMixin ):
    """Provides the portion of an assignment grade determined by the reviewer's responses
    where the reviewer's responses were entered in points."""

    # __name__ = 'reviewer_assigned'
    # METHOD_NAME = 'reviewer assigned'


    def __init__( self, graded_activity: Activity, review_activity: Activity, review_columns: list, max_possible_points=None, **kwargs ):
        """

        :param pct_of_score: Float of what percentage of the total score is contributed by the reviewer
        :param graded_activity: Activity whose grade depends on review
        :param review_activity: Activity where the reviewer gave scores
        :param review_columns: Columns in the review activity to use. todo Presently assumes only 1 value in list
        """
        self.max_possible_points = max_possible_points
        self.graded_activity = graded_activity
        self.activity = graded_activity
        self.review_columns = review_columns
        self.review_activity = review_activity

        if max_possible_points is not None:
            self.review_points_possible = self.max_possible_points
        else:
            self.review_points_possible = graded_activity.points_possible
            print("The reviewer is determining the entirety of the grade")

        # todo make this a param or variable...
        # self.valmap = self.LIKERT_VALMAP

        self.handle_kwargs(**kwargs)

        self._initialize()


    def _initialize( self ):
        self._initialize_db()
        self.pairingsRepo = AssociationRepository(self.dao, self.graded_activity)
        self.review_repo = WorkRepositoryLoaderFactory.make(course=environment.CONFIG.course,
                                                            activity=self.review_activity,
                                                            rest_timeout=5)

    def grade( self, author_id ):
        """
        Returns grade based on peer review
        :param author_id: The author's canvas id
        :return:
        """
        # todo assume only one column for now
        col = self.review_columns[0]

        # May raise NoReviewerAssigned
        ra = self.pairingsRepo.get_by_author( author_id )

        reviewer_work = self.review_repo.get_student_work(ra.assessor_id)

        if reviewer_work is None:
            raise WaitingForReviewerToSubmit

        review_points = reviewer_work[col]


        # todo check that reviewer has turned in

        # todo make sure we're dealing with the correct value type.

        # todo make sure reviewer isn't point injecting
        if review_points > self.max_possible_points:
            raise InvalidReviewPointValue

        return review_points

    # return self.valmap.get(v)

if __name__ == '__main__':
    pass
