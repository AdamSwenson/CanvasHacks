"""
Created by adam on 3/14/20
"""
__author__ = 'adam'

from CanvasHacks.SkaaSteps.SendDiscussionReviewToPoster import SendDiscussionReviewToPoster

if __name__ == '__main__':
    pass

from IPython.display import display
from ipywidgets import widgets

from CanvasHacks import environment
from CanvasHacks.SkaaSteps.SendForumPostsToReviewer import SendForumPostsToReviewer


def run_discussion_steps( SEND=True, download=True, **kwargs ):
    print( "\n====================== DISTRIBUTE DISCUSSION POSTS ======================" )
    step1 = SendForumPostsToReviewer( course=environment.CONFIG.course,
                                      unit=environment.CONFIG.unit,
                                      send=SEND )
    step1.run( rest_timeout=5 )

    print( "\n====================== DISTRIBUTE DISCUSSION REVIEWS ======================" )
    step2 = SendDiscussionReviewToPoster( environment.CONFIG.course, environment.CONFIG.unit, send=SEND )
    step2.run( rest_timeout=5, download=download )

    # Return in case need to check values on them
    return (step1, step2)


def discussion_run_button(control_store, return_button=False, width='auto', **kwargs):
    RUNNING = False

    def get_style( is_running=False ):
        return 'warning' if is_running else 'danger'

    def get_name( is_running=False ):
        return 'RUNNING' if is_running else 'RUN DISCUSSION'

    # Create the button
    layout = widgets.Layout( width=width )
    b = widgets.Button( description=get_name( RUNNING ),
                    layout=layout,
                    button_style=get_style( RUNNING ) )

    def callback( change ):
        RUNNING = True
        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )

        steps = run_discussion_steps( SEND=True, download=True )

        RUNNING = False

        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )

        control_store['discussion_steps'] = steps

    b.on_click( callback )

    if return_button is True:
        # If putting inside a box or something else which will
        # call display
        return b
    else:
        display( b )

