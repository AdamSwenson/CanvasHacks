"""
Created by adam on 3/14/20
"""
__author__ = 'adam'

from IPython.display import display
from ipywidgets import Layout, VBox, widgets

from CanvasHacks.StudentNaggers.discussion import DiscussionNagger
from CanvasHacks.StudentNaggers.discussion_review import DiscussionReviewNagger
from CanvasHacks.StudentNaggers.essay import EssayNagger
from CanvasHacks.StudentNaggers.skaa_review import SkaaReviewNagger

if __name__ == '__main__':
    pass


def nag_button( label, nag_obj, return_button=False, width='auto', **kwargs ):
    """
    :param nag_obj:
    :param label:
    :param return_button: Set to true if putting inside a box or something else which will call display
    :return:
    """

    RUNNING = False

    def get_style( is_running=False ):
        return 'warning' if is_running else 'danger'

    def get_name( is_running=False ):
        return 'RUNNING' if is_running else label

    # Create the button
    layout = widgets.Layout( width=width )
    b = widgets.Button( description=get_name( RUNNING ),
                        button_style=get_style( RUNNING ),
                        layout=layout )

    def callback( change ):
        RUNNING = True
        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )

        nag_obj.run()

        RUNNING = False

        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )

    b.on_click( callback )
    if return_button is True:
        # If putting inside a box or something else which will
        # call display
        return b
    else:
        display( b )


def nag_button_area( control_store, **kwargs ):
    # items_layout = Layout( width='auto' )  # override the default width of the button to 'auto' to let the button grow

    controls = [ ('ESSAY', EssayNagger( control_store[ 'skaa_repo' ] )),
                 ('SKAA REVIEW', SkaaReviewNagger( control_store[ 'skaa_repo' ] )),
                 ('DISCUSSION', DiscussionNagger( control_store[ 'diss_repo' ] )),
                 ('DISCUSSION REVIEW', DiscussionReviewNagger( control_store[ 'diss_repo' ] ))
                 ]

    box_layout = Layout(
        border='solid',
        **kwargs
    )
    buttons = [ widgets.Label( value="Nag students" ) ]
    buttons += [ nag_button( label, obj, return_button=True, **kwargs ) for label, obj in controls ]
    return VBox( buttons, layout=box_layout )
