"""
Created by adam on 12/24/19
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass
from unittest.mock import MagicMock, patch

from faker import Faker
import random
import pandas as pd
import pytz
fake = Faker()
from CanvasHacks.PeerReviewed.Definitions import InitialWork, Review, MetaReview, Unit

from CanvasHacks.PeerReviewed.Submissions import SubmissionFactory
from tests.factories.CanvasApiFactories import peer_review_result_factory, submission_comment_result_factory, submission_result_factory


def activity_data_factory(name=None):
    return {
        'name' : fake.word() if name is None else name,
        'access_code' : fake.word(),
        'email_intro': fake.text(),
        'email_subject': fake.text(),
        'html_url': fake.url(),
        'open_at': pd.to_datetime( fake.date_time_this_century( before_now=True, after_now=False, tzinfo=pytz.utc ) ),
        'due_at': pd.to_datetime( fake.date_time_this_century( before_now=False, after_now=True, tzinfo=pytz.utc ) ),
        'completion_points': random.randint( 0, 1000 ),
        'max_points': random.randint( 0, 1000 ),
    }


def test_data_factory():
    return {
        'initial': activity_data_factory(),
        'review': activity_data_factory(),
        'metareview': activity_data_factory()
    }


def unit_factory(course=None, unit_number=None, initial_is_quiz_type=True):
    """Creates a Unit object with fake data for all assignments"""
    course = course if course is not None else MagicMock()
    unit_number = unit_number if unit_number is not None else random.randint(1, 22222)
    test_data = test_data_factory()
    initial = InitialWork( **test_data[ 'initial' ] )
    initial.id = random.randint( 0, 10000 )
    if initial_is_quiz_type:
        initial.quiz_id = initial.id
    review = Review( **test_data[ 'review' ] )
    review.id = random.randint( 0, 10000 )
    review.quiz_id = review.id
    review.access_code = fake.ean8()
    review.activity_link = fake.uri()
    meta = MetaReview( **test_data[ 'metareview' ] )
    meta.id = random.randint( 0, 10000 )
    meta.quiz_id = meta.id
    unit = Unit( course, unit_number )
    unit.components = [initial, review, meta]
    return unit


def submissions_factory( student1, student2, assignment ):
    submissions = [ ]
    # initial work
    sfac1 = SubmissionFactory( assignment.initial_work )
    r1 = submission_result_factory( assignment.initial_work, student1 )
    submissions.append( sfac1.make( r1 ) )

    r2 = submission_result_factory( assignment.initial_work, student2 )
    submissions.append( sfac1.make( r2 ) )

    # reviews
    sfac2 = SubmissionFactory( assignment.review )
    pr1 = peer_review_result_factory( student1, student2 )
    submissions.append( sfac2.make( pr1 ) )

    pr2 = peer_review_result_factory( student2, student1 )
    submissions.append( sfac2.make( pr2 ) )

    # meta reviews
    sfac3 = SubmissionFactory( assignment.meta_review )
    mr1 = peer_review_result_factory( student1, student2 )
    submissions.append( sfac3.make( mr1 ) )

    mr2 = peer_review_result_factory( student2, student1 )
    submissions.append( sfac3.make( mr2 ) )

    return submissions


def discussion_entry_factory( **kwargs ):
    """ Returns something like:
    {'id': 2132485, 'user_id': 169155,
    'parent_id': None, 'created_at': '2020-01-16T23:01:53Z',
    'updated_at': '2020-01-16T23:01:53Z', 'rating_count': None,
    'rating_sum': None, 'user_name': 'Test Student',
    'message': '<p>got em</p>', 'user': {'id': 169155,
    'display_name': 'Test Student',
    'avatar_image_url': 'https://canvas.csun.edu/images/messages/avatar-50.png',
    'html_url': 'https://canvas.csun.edu/courses/85210/users/169155',
    'pronouns': None, 'fake_student': True},
    'read_state': 'unread', 'forced_read_state': False,
    'discussion_id': 737847, 'course_id': 85210}
    """
    dummy = { 'id': random.randint( 0, 100000 ),
             'user_id': random.randint( 0, 10000 ),
             'parent_id': None,
             'created_at': pd.to_datetime(fake.date_time_this_century( before_now=False, after_now=True, tzinfo=None )),
             'updated_at': pd.to_datetime(fake.date_time_this_century( before_now=False, after_now=True, tzinfo=None )),
             'rating_count': None,
             'rating_sum': None,
             'user_name': fake.name(),
             'message': '<p>{}</p>'.format(fake.paragraph()),
             'read_state': 'unread', 'forced_read_state': False,
             'discussion_id': random.randint( 0, 10000 ),
             'course_id': random.randint( 0, 10000 )
             }

    # if stuff passed in, replace
    for k in kwargs.keys():
        dummy[k] = kwargs[k]
    return dummy

