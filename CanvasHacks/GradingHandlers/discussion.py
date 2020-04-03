"""
Created by adam on 2/15/20
"""
from CanvasHacks.GradingHandlers.base import IGrader

__author__ = 'adam'

from CanvasHacks.GradingMethods.base import IGradingMethod
from CanvasHacks.GradingCorrections.penalities import IPenalizer


class DiscussionForumGrader( IGrader ):
    """
    Grades discussion forum posts
    """

    grade_method: IGradingMethod
    penalizer: IPenalizer

    def __init__( self, work_repo, num_posts_required=1,  **kwargs ):
        """

        :param work_repo:
        :param num_posts_required:
        :param kwargs:
        """
        self.num_posts_required = num_posts_required
        self.work_repo = work_repo

        super().__init__(**kwargs)

        self.corrections = self.activity.corrections

        self.penalizers = self.activity.penalizers

        self.grade_methods = self.activity.grade_methods
        # Todo Check that output of grading methods sums to 1?

        # self.grade_method = self.activity.grade_method
        # self.penalizer = self.activity.penalizer

        self.credit_per_post = 100 / self.num_posts_required

        # Internal store for in between grading steps
        self._raw = [
            # ( sid, percent credit)
        ]

        # Externally usable store
        self.graded = []

    def _calc_scores( self ):
        """Iterate through repo data and store individual
        student scores in _raw
        """
        for p in self.work_repo.data:
            # discussion repo data will look like:
            # [{'student_id', 'student_name', 'text'}]
            pct_credit = 0
            for method in self.grade_methods:
                # each method should return a float pct
                # all of which sum to 1
                pct_credit += method.grade( p['text'],
                                            on_credit=self.credit_per_post,
                                            on_no_credit=0)

            # pct_credit = self.grade_method.grade(p['text'], on_credit=self.credit_per_post, on_no_credit=0)
            # pct_credit = self.credit_per_post if receives_credit( p[ 'text' ] ) else 0
            self._raw.append( (p[ 'student_id' ], pct_credit) )

    def grade( self ):
        """Assigns a provisional grade for the discussion unit
        Will return as a list of tuples
        todo: Add logging of details of how grade assigned
        """
        self._calc_scores()

        self._prepare_results()

        return self.graded

    def _prepare_results( self ):
        """Takes the raw scores and prepares them for upload
        """
        # sum them up for each student
        sids = list( set( [ s[ 0 ] for s in self._raw ] ) )
        for sid in sids:
            t = sum( [ s[ 1 ] for s in self._raw if s[ 0 ] == sid ] )
            # todo Should this be rounded to ceiling?
            t = round(t)
            # Correct for more than required number
            t = 100 if t > 100 else t
            self.graded.append( (sid, t) )


#
# def assign_grades(discussion_repo, num_posts_required):
#     """Assigns a provisional grade for the discussion unit
#     """
#     credit_per_post = 100 / num_posts_required
#
#     grades = [
#         # ( sid, percent credit)
#     ]
#
#     for p in discussion_repo.data:
#         #     print(post, receives_credit(post))
#         #         credit_per_post
#         pct_credit = credit_per_post if receives_credit(p['text']) else 0
#         grades.append( (p['student_id'], pct_credit) )
#
#     # sum them up and put in list for upload
#     totals = []
#     sids = list(set([s[0] for s in grades]))
#     for sid in sids:
#         t = sum([s[1] for s in grades])
#         t = 100 if t > 100 else t
#         totals.append( ( sid,  t))
#     return totals
#

if __name__ == '__main__':
    pass