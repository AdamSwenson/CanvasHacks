"""
Created by adam on 4/9/20
"""
__author__ = 'adam'

from CanvasHacks import environment
from CanvasHacks.SkaaSteps.SendDiscussionReviewToPoster import SendDiscussionReviewToPoster
from CanvasHacks.SkaaSteps.SendForumPostsToReviewer import SendForumPostsToReviewer


REQUIRED_MIN_POSTS = 2

def run_discussion_steps( SEND=True, download=True, post_threshold=REQUIRED_MIN_POSTS, **kwargs ):
    """
    Sends posts out for review and distributes feedback from the review

    :param SEND:
    :param download:
    :param post_threshold:
    :param kwargs:
    :return:
    """
    print( "\n====================== DISTRIBUTE DISCUSSION POSTS ======================" )
    step1 = SendForumPostsToReviewer( course=environment.CONFIG.course,
                                      unit=environment.CONFIG.unit,
                                      send=SEND,
                                      post_threshold=post_threshold )
    step1.run( rest_timeout=5 )

    print( "\n====================== DISTRIBUTE DISCUSSION REVIEWS ======================" )
    step2 = SendDiscussionReviewToPoster( environment.CONFIG.course, environment.CONFIG.unit, send=SEND )
    step2.run( rest_timeout=5, download=download )

    # Return in case need to check values on them
    return (step1, step2)


if __name__ == '__main__':
    # todo Add stuff here to grab command line arguments and set the unit

    pass
