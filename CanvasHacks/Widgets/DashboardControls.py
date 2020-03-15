"""
Created by adam on 3/14/20
"""
__author__ = 'adam'

from IPython.display import display
from ipywidgets import Layout, widgets, HBox, VBox

from CanvasHacks import environment
from CanvasHacks.Displays.dashboard import SkaaDashboard, DiscussionDashboard
from CanvasHacks.Repositories.overview import SkaaOverviewRepository, DiscussionOverviewRepository
from CanvasHacks.Widgets.AssignmentSelection import make_unit_chooser
from CanvasHacks.Widgets.DiscussionControls import discussion_run_button
# from CanvasHacks.Widgets.NagControls import nag_no_essay
from CanvasHacks.Widgets.LiveSelection import make_test_selector
from CanvasHacks.Widgets.NagControls import nag_button_area
from CanvasHacks.Widgets.SkaaControls import skaa_run_button

if __name__ == '__main__':
    pass


def dashboards_load_button( control_store, return_button=False, width='auto' ):
    """
    :param control_store:
    :param return_button: Set to true if putting inside a box or something else which will call display
    :return:
    """

    RUNNING = False

    def get_style( is_running=False ):
        return 'warning' if is_running else 'primary'

    def get_name( is_running=False ):
        return 'RUNNING' if is_running else 'REFRESH DASHBOARDS'

    # Create the button
    layout = widgets.Layout( width=width )
    b = widgets.Button( description=get_name( RUNNING ),
                        layout=layout,
                        button_style=get_style( RUNNING ) )

    def callback( change ):
        RUNNING = True
        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )

        control_store[ 'skaa_repo' ].load( environment.CONFIG.unit )
        control_store[ 'skaa_dash' ].print_counts()
        control_store[ 'diss_repo' ].load( environment.CONFIG.unit )
        control_store[ 'diss_dash' ].print_counts()

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


def run_buttons( control_store, **kwargs ):
    box_layout = Layout(
        border='solid',
        **kwargs
        # width='50%'
    )

    box = widgets.VBox( [
        widgets.Label( value="Distribute work and results" ),
        skaa_run_button( control_store, return_button=True,  **kwargs),
        discussion_run_button( control_store, return_button=True, **kwargs )
    ], layout=box_layout )
    return box


def make_control_store():
    # Initialize these but do not load until a unit is selected
    sr = SkaaOverviewRepository()
    dr =  DiscussionOverviewRepository()
    return {
        'skaa_repo': sr,
        'diss_repo': dr,
        'skaa_dash' : SkaaDashboard(sr),
        'diss_dash' : DiscussionDashboard(dr)
    }


def button_area(control_store):
    """
    Displays all control buttons
    :param control_store:
    :return:
    """
    row_layout = Layout( width='100%', padding='10px' )

    row1 = HBox([make_test_selector(return_button=True)], layout=row_layout)

    row2 = VBox(make_unit_chooser(return_button=True, width='100%'), layout=row_layout)

    row3 = HBox([
        run_buttons(control_store=control_store, width='100%', padding='2px'),
        nag_button_area(control_store, width='100%', padding='2px')
    ], layout=row_layout)

    row4 = HBox(
        [
            dashboards_load_button(control_store, return_button=True, width='auto'),
        ],
        layout=row_layout)

    container = VBox(
        [row1, row2, row3, row4], layout=Layout(border='dashed', width='80%'))
    display(container)