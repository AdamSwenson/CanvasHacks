"""
Created by adam on 2/15/20
"""
from CanvasHacks.GradingTools.base import IGrader

__author__ = 'adam'

from CanvasHacks.GradingTools.nonempty import receives_credit


class DiscussionGrader(IGrader):

    def __init__( self, work_repo, num_posts_required=1, grade_func=None, **kwargs ):
        """
        :param grade_func: Function or method to use to determine grade
        """
        self.num_posts_required = num_posts_required
        self.grade_func = grade_func
        self.work_repo = work_repo
        super().__init__(**kwargs)

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
            pct_credit = self.credit_per_post if receives_credit( p[ 'text' ] ) else 0
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