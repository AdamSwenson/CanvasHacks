"""
Created by adam on 12/24/19
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass

from faker import Faker

fake = Faker()
from CanvasHacks.PeerReviewed.Definitions import *

from CanvasHacks.PeerReviewed.Submissions import SubmissionFactory
from tests.factories.CanvasApiFactories import *


def activity_data_factory():
    return {
        'open_date': pd.to_datetime( fake.date_time_this_century( before_now=True, after_now=False, tzinfo=None ) ),
        'due_date': pd.to_datetime( fake.date_time_this_century( before_now=False, after_now=True, tzinfo=None ) ),
        'completion_points': random.randint( 0, 1000 ),
        'max_points': random.randint( 0, 1000 ),
    }


def test_data_factory():
    return {
        'initial': activity_data_factory(),
        'review': activity_data_factory(),
        'metareview': activity_data_factory()
    }


def assignment_factory():
    test_data = test_data_factory()
    initial = InitialWork( **test_data[ 'initial' ] )
    initial.id = random.randint( 0, 10000 )
    review = Review( **test_data[ 'review' ] )
    review.id = random.randint( 0, 10000 )
    meta = MetaReview( **test_data[ 'metareview' ] )
    meta.id = random.randint( 0, 10000 )
    return Assignment( initial, review, meta )


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
