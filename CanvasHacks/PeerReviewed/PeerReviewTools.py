"""
Created by adam on 12/20/19
"""
from CanvasHacks.Definitions.skaa import InitialWork, Review, MetaReview
from CanvasHacks.Definitions.unit import Unit

__author__ = 'adam'

from CanvasHacks.Models.student import Student


def determine_overall_grade():
    """Just submitting: 1
        points assigned by reviewer: 1 , 2, 3
        points for just doing review: 1
        points for quality of review (assigned by submitter): 1, 2
        points for reviewing reviewer: 1
    """
    submission = {
        # Points get for just turning in something non-empty
        'automatic': 1
    }

    reviewing = {
        'automatic': 1
    }

    review_review = {
        'automatic': 1
    }


# -------------------------------- Elements of the unit


# ---------------------------------- Student work


class UnitScores( object ):
    """Holds all scores for one student"""

    def __init__( self, assignment: Unit, student: Student ):
        self.student = student
        self.assignment = assignment

        self.initial_complete = 0
        self.initial_assigned = 0

        self.review_complete = 0
        self.review_assigned = 0

        self.meta_complete = 0

    @property
    def total( self ):
        return sum( [
                self.initial_complete,
                self.initial_assigned,
                self.review_complete,
                self.review_assigned,
                self.meta_complete
            ] )


class UnitGradeCalculator( object ):
    """Calculates the unit grades for all students.
 """

    def __init__( self, unit: Unit, submissions ):
        self.assignment = unit
        self.submissions = submissions
        self.scores = []

    def add_submission( self, submission ):
        self.submissions.append( submission )

    def _get_submissions( self, submission_type, submission_list=None ):
        """Returns a list of all submissions of the provided type
        Will search all stored submissions unless pass in a particular list
        (which would normally be the submissions for a particular student)"""
        submission_list = submission_list if submission_list else self.submissions
        return list( filter( lambda x: isinstance( x.activity, submission_type ), submission_list ) )

    @property
    def intial_work_submissions( self ):
        return self._get_submissions( InitialWork )

    @property
    def review_submissions( self ):
        return self._get_submissions( Review )

    @property
    def meta_review_submissions( self ):
        return self._get_submissions( MetaReview )

    @property
    def students( self ):
        """Returns list of unique student objects.
        This is drawn from initial work since students only
        do reviews after they submit something
        todo: make unique ( using list(set(xxx)) stopped working when defined __eq__ on student
        """
        return [ s.submitter for s in self.intial_work_submissions ]

    def get_student_work( self, student: Student ):
        """Returns list containing submissions where the
        student is either the submtter or the reviewer
        """
        return self.get_work_as_submitter( student ) + self.get_work_as_reviewer( student )
        # def check(user, submission):
        #     if submission.submitter.student_id == user.student_id:
        #         return True
        #     if submission.reviewer is not None:
        #         return submission.reviewer.student_id == user.student_id
        #     return False
        # return list( filter( lambda x: check(student, x), self.submissions ))

    def get_work_as_submitter( self, student: Student ):
        """Returns all submissions where the student is the submitter"""
        return list( filter( lambda x: x.submitter == student, self.submissions ) )

    def get_work_as_reviewer( self, student: Student ):
        """Returns all submissions where the student is the reviewer"""

        def check( user, submission ):
            if submission.reviewer is not None:
                return submission.reviewer == user
            return False

        return list( filter( lambda x: check( student, x ), self.submissions ) )

    # def calc_orig_scores( self, student ):
    #     """Calculates the initial work portion of the
    #     score
    #     Includes:
    #         - Credit for submitting the unit
    #         - Credit assigned by the reviewer
    #     """
    #
    # def calc_review_scores( self, student ):
    #     """Calculates the review portion of the score.
    #     This includes:
    #         - credit for completing the review
    #         - credit assigned in the metareview
    #     """
    #     # Get the reviews for the submitter
    #     work = self.get_student_work( student )
    #     reviews = self._get_submissions( Review, work )
    #     for r in reviews:
    #         if r.submitter == student:
    #             # get points assigned by the reviewer
    #             scores[ 'review_assigned' ] = r.submitter_points
    #         elif r.reviewer == student:
    #             # Points for completing the review
    #             scores[ 'review_complete' ] = r.reviewer_points
    #
    # def calc_meta_scores( self, student ):
    #     """Calculates the meta review portion of the score
    #     This includes:
    #         - credit for completing the metareview
    #     """

    def calculate( self ):
        # Get a list of students and
        # populate our score data store
        for student in self.students:
            scores = UnitScores( self.assignment, student )

            work = self.get_student_work( student )

            # Get the points for initial submissions
            initial = self._get_submissions( InitialWork, work )
            # todo error handling if multiple initial subs
            #   self.scores[s.submitter.student_id]
            scores.initial_complete += initial[0].submitter_points

            reviews = self._get_submissions( Review, work )
            for r in reviews:
                if r.submitter == student:
                    # get points assigned by the reviewer
                    scores.review_assigned = r.submitter_points
                elif r.reviewer == student:
                    # Points for completing the review
                    scores.review_complete = r.reviewer_points

            # Metareviews
            meta = self._get_submissions( MetaReview, work )
            for r in meta:
                if r.submitter == student:
                    # todo: is this right?
                    # Points for completing the review
                    scores.meta_complete = r.reviewer_points

                elif r.reviewer == student:
                    # get points assigned to student as reviewer
                    scores.meta_assigned = r.submitter_points

            # Calculate total
            self.scores.append(scores)

            # self.scores[ student.student_id ] = scores
        # # Get the automatic credit/no-credit score
        # for sub in self.submissions:
        #     self.score += sub.points
        # return self.score

        # Now get the points assigned to them by the reviewer
        # self.review_submissions


# ---------------- queries and mechanics (move elsewhere)

if __name__ == '__main__':
    pass
