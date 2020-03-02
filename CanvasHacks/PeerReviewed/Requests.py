"""
Functions and tools for making requests to the
canvas api specific to the peer reviewded assignments

Created by adam on 12/24/19
"""
from CanvasHacks.Models.student import Student
from CanvasHacks.PeerReviewed.Submissions import Submission, ReviewSubmission

__author__ = 'adam'

if __name__ == '__main__':
    pass


def get_all_submissions( course_id, quiz_id, per_page=42 ):
    """Downloads all initial submissions for the unit"""
    # todo: query to server goes here
    # Holds the results from the request to server
    results = [ ]
    # Submission objects to return
    subs = [ ]

    for r in results:
        # todo: check correct field names
        student = Student( r[ 'id' ], r[ 'name' ] )


def get_all_peer_reviews( review_activity, **kwargs ):
    """Returns objects with the format:
        {
      // The assessors user id
      "assessor_id": 23,
      // The id for the asset associated with this Peer Review
      "asset_id": 13,
      // The type of the asset
      "asset_type": "Submission",
      // The id of the Peer Review
      "id": 1,
      // The user id for the owner of the asset
      "user_id": 7,
      // The state of the Peer Review, either 'assigned' or 'completed'
      "workflow_state": "assigned",
      // the User object for the owner of the asset if the user include parameter is
      // provided (see user API) (optional)
      "user": "User",
      // The User object for the assessor if the user include parameter is provided
      // (see user API) (optional)
      "assessor": "User",
      // The submission comments associated with this Peer Review if the
      // submission_comment include parameter is provided (see submissions API)
      // (optional)
      "submission_comments": "SubmissionComment"
    }
    """
    # query happens
    # todo make query happen. Include 'user' parameter and 'submission_comment' param
    results = [ ]
    # Submission objects to return
    subs = [ ]

    for r in results:
        # todo: check correct field names
        submitter = Student( r[ 'user_id' ], **r[ 'user' ] )
        reviewer = Student( r[ 'assessor_id' ], **r[ 'assessor' ] )
        submission = ReviewSubmission( submitter, review_activity, **r )
        subs.append( submission )


def get_assignment_data_for_student( assignment, student ):
    pass

