"""
Created by adam on 2/15/20
"""
__author__ = 'adam'

from CanvasHacks.GradingTools import grade_credit_no_credit

def assign_grades(discussion_repo, num_posts_required):
    """Assigns a provisional grade for the discussion assignment
    """
    credit_per_post = 100 / num_posts_required

    grades = [
        # ( sid, percent credit)
    ]

    for p in discussion_repo.data:
        #     print(post, grade_credit_no_credit(post))
        #         credit_per_post
        pct_credit = credit_per_post if grade_credit_no_credit(p['text']) else 0
        grades.append( (p['student_id'], pct_credit) )

    # sum them up and put in list for upload
    totals = []
    sids = list(set([s[0] for s in grades]))
    for sid in sids:
        t = sum([s[1] for s in grades])
        t = 100 if t > 100 else t
        totals.append( ( sid,  t))
    return totals


if __name__ == '__main__':
    pass