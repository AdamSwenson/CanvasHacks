"""
Simulating data from the canvas api

Created by adam on 12/24/19
"""

__author__ = 'adam'

from faker import Faker

fake = Faker()

import random

import pandas as pd


if __name__ == '__main__':
    pass


def submission_result_factory(activity, student, on_time=True):
    """"""
    return {
        # The submission's unit id
        "assignment_id": activity.id,
        # The submission's unit (see the assignments API) (optional)
        "unit": None,
        # The submission's course (see the course API) (optional)
        "course": None,
        # This is the submission attempt number.
        "attempt": 1,
        # The content of the submission, if it was submitted directly in a text field.
        "body": fake.paragraph(),
        # The grade for the submission, translated into the unit grading scheme
        # (so a letter grade, for example).
        "grade": "A-",
        # A boolean flag which is false if the student has re-submitted since the
        # submission was last graded.
        "grade_matches_current_submission": True,
        # URL to the submission. This will require the user to log in.
        "html_url": "http:#example.com/courses/255/assignments/543/submissions/134",
        # URL to the submission preview. This will require the user to log in.
        "preview_url": "http:#example.com/courses/255/assignments/543/submissions/134?preview=1",
        # The raw score
        "score": random.randint(1,1000),
        # Associated comments for a submission (optional)
        "submission_comments": None,
        # The types of submission ex:
        # ('online_text_entry'|'online_url'|'online_upload'|'media_recording')
        "submission_type": "online_text_entry",
        # The timestamp when the unit was submitted
        "submitted_at": activity.due_at - pd.Timedelta("1 Day") if on_time else activity.due_at + pd.Timedelta("1 Day") ,
        # The URL of the submission (for 'online_url' submissions).
        "url": None,
        # The id of the user who created the submission
        "user_id": student.student_id,
        # The id of the user who graded the submission. This will be None for
        # submissions that haven't been graded yet. It will be a positive number if a
        # real user has graded the submission and a negative number if the submission
        # was graded by a process (e.g. Quiz autograder and autograding LTI tools).
        # Specifically autograded quizzes set grader_id to the negative of the quiz id.
        # Submissions autograded by LTI tools set grader_id to the negative of the tool
        # id.
        "grader_id": 86,
        "graded_at": "2012-01-02T03:05:34Z",
        # The submissions user (see user API) (optional)
        "user": None,
        # Whether the submission was made after the applicable due date
        "late": False,
        # Whether the unit is visible to the user who submitted the unit.
        # Submissions where `assignment_visible` is false no longer count towards the
        # student's grade and the unit can no longer be accessed by the student.
        # `assignment_visible` becomes false for submissions that do not have a grade
        # and whose unit is no longer assigned to the student's section.
        "assignment_visible": True,
        # Whether the unit is excused.  Excused assignments have no impact on a
        # user's grade.
        "excused": True,
        # Whether the unit is missing.
        "missing": True,
        # The status of the submission in relation to the late policy. Can be late,
        # missing, none, or None.
        "late_policy_status": "missing",
        # The amount of points automatically deducted from the score by the
        # missing/late policy for a late or missing unit.
        "points_deducted": 12.3,
        # The amount of time, in seconds, that an submission is late by.
        "seconds_late": 300,
        # The current state of the submission
        "workflow_state": "submitted",
        # Extra submission attempts allowed for the given user and unit.
        "extra_attempts": 10,
        # A unique short ID identifying this submission without reference to the owning
        # user. Only included if the caller has administrator access for the current
        # account.
        "anonymous_id": "acJ4Q",
        # The date this submission was posted to the student, or nil if it has not been
        # posted.
        "posted_at": "2020-01-02T11:10:30Z"
    }


def peer_review_result_factory( submitter, reviewer, completed=True ):
    return {
        # The assessors user id
        "assessor_id": reviewer.student_id,
        # The id for the asset associated with this Peer Review
        "asset_id": 13,
        # The type of the asset
        "asset_type": "Submission",
        # The id of the Peer Review
        "id": 1,
        # The user id for the owner of the asset
        "user_id": submitter.student_id,
        # The state of the Peer Review, either 'assigned' or 'completed'
        "workflow_state": 'completed' if completed else "assigned",
        # the User object for the owner of the asset if the user include parameter is
        # provided (see user API) (optional)
        "user": "User",
        # The User object for the assessor if the user include parameter is provided
        # (see user API) (optional)
        "assessor": "User",
        # The submission comments associated with this Peer Review if the
        # submission_comment include parameter is provided (see submissions API)
        # (optional)
        "submission_comments": submission_comment_result_factory(reviewer)
    }


def submission_comment_result_factory( commentor ):
    """See https://canvas.instructure.com/doc/api/submissions.html#method.submissions_api.update"""
    return {
        "id": 37,
        "author_id": commentor.student_id,
        "author_name": commentor.name,
        # Abbreviated user object UserDisplay (see users API).
        "author": "{}",
        "comment": fake.paragraph(),
        "created_at": "2012-01-01T01:00:00Z",
        "edited_at": "2012-01-02T01:00:00Z",
        "media_comment": None
    }