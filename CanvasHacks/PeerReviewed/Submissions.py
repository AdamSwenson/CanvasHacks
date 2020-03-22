"""
Created by adam on 12/24/19
"""
from CanvasHacks.Models.model import StoreMixin
from CanvasHacks.Models.student import Student
from CanvasHacks.Definitions.skaa import InitialWork, Review, MetaReview

__author__ = 'adam'

if __name__ == '__main__':
    pass


class Submission( StoreMixin ):
    """A student's completion of an activity_inviting_to_complete
    Parent class; not usually used
    """

    def __init__( self, activity, query_result, **kwargs ):
        self.activity = activity
        # Student who submitted the thing (or thing being reviewed)
        self.submitter = None
        # Student who reviewed the thing
        self.reviewer = None
        # Date the submission was submitted
        self.completion_date = None
        # Score assigned by the reviewer
        self.assigned_score = 0

        self.process( query_result )

        self.handle_kwargs( **kwargs )

    @property
    def on_time( self ):
        """Returns true if the student submitted the activity_inviting_to_complete
        on time.
        """
        return self.completion_date <= self.activity.due_at

    @property
    def submitter_points( self ):
        # todo: Consider adding test to make sure haven't exceeded max score
        # todo: Consider adding check for on time here
        raise NotImplementedError

    def process( self, result ):
        raise NotImplementedError


class InitialSubmission( Submission ):

    def __init__( self, activity, query_result, **kwargs ):
        super().__init__( activity, query_result, **kwargs )

    def process( self, result ):
        """Takes the return from a query getting a peer review
        object and sets values of submission"""
        self.submitter = Student( student_id=result[ 'user_id' ]) #, **result[ 'user' ] )
        self.completion_date = result['submitted_at']
        self.handle_kwargs( **result )

    @property
    def submitter_points( self ):
        # todo checks for minimum length etc
        # todo how to handle late assignments? should do here?
        return self.activity.completion_points


class ReviewSubmission( Submission ):
    def __init__( self, activity, query_result, **kwargs ):
        super().__init__( activity, query_result, **kwargs )

    def process( self, result ):
        """Takes the return from a query getting a peer review
        object and sets values of submission"""
        self.submitter = Student( student_id=result[ 'user_id' ]) #, **result[ 'user' ] )
        self.reviewer = Student( student_id=result[ 'assessor_id' ]) #, **result[ 'assessor' ] )
        self.handle_kwargs( **result )

    @property
    def is_complete( self ):
        return self.workflow_state == 'completed'

    @property
    def reviewer_points( self ):
        """The points the student doing the review should receive"""
        if self.is_complete:
            return self.activity.completion_points
        return 0

    @property
    def submitter_points( self ):
        """The points the student doing the original submission should receive"""
        if self.is_complete:
            # The points that the reviewer assigned
            # todo: make sure can't assign more than assignable points
            return self.assigned_score
        # If the reviewer did not complete the review, the
        # submitting student gets full credit
        # todo: think through the logic here
        return self.activity.assignable_points


class SubmissionFactory( StoreMixin ):
    """A student's completion of an activity_inviting_to_complete
    todo: refactor into factory """

    def __init__( self, activity, **kwargs ):
        self.activity = activity

    def make( self, query_result, **kwargs ):

        if isinstance( self.activity, InitialWork ):
            return InitialSubmission( self.activity, query_result, **kwargs )
        elif isinstance( self.activity, Review ):
            return ReviewSubmission( self.activity, query_result, **kwargs )
        elif isinstance( self.activity, MetaReview ):
            return ReviewSubmission( self.activity, query_result, **kwargs )
