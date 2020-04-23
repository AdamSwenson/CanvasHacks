"""
Created by adam on 3/12/20
"""
__author__ = 'adam'
from CanvasHacks import environment

from CanvasHacks.Files.FromDownloadFolder import file_reports
from CanvasHacks.Repositories.students import StudentRepository
from CanvasHacks.executables.run_discussion_on_multiple_units import RunDiscussionMultipleUnits
from CanvasHacks.executables.run_skaa_on_multiple_units import RunSkaaMultipleUnits
from CanvasHacks.executables.run_skaa_on_single_unit import run_all_steps

if __name__ == '__main__':
    pass

from ipywidgets import widgets
from IPython.display import display


def skaa_run_button( control_store, return_button=False, width='auto', **kwargs ):
    RUNNING = False

    def get_style( is_running=False ):
        return 'warning' if is_running else 'danger'

    def get_name( is_running=False ):
        return 'RUNNING' if is_running else 'RUN SKAA'

    # Create the button
    layout = widgets.Layout( width=width )
    b = widgets.Button( description=get_name( RUNNING ),
                        layout=layout,
                        button_style=get_style( RUNNING ) )

    def callback( change ):
        RUNNING = True
        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )

        steps = run_all_steps( SEND=True, download=True )

        RUNNING = False

        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )

        control_store[ 'skaa_steps' ] = steps

    b.on_click( callback )

    if return_button is True:
        # If putting inside a box or something else which will
        # call display
        return b
    else:
        display( b )


def multiple_unit_control( control_store, return_button=False, width='auto', **kwargs ):
    RUNNING = False

    def get_style( is_running=False ):
        return 'warning' if is_running else 'danger'

    def get_name( is_running=False ):
        return 'RUNNING' if is_running else 'RUN SKAA'

    # start unit
    start_unit_box = widgets.IntText(
        description='Start unit#',
        disabled=False
    )
    stop_unit_box = widgets.IntText(
        description='Stop unit#',
        disabled=False
    )
    # Create the button
    layout = widgets.Layout( width=width )
    b = widgets.Button( description=get_name( RUNNING ),
                        layout=layout,
                        button_style=get_style( RUNNING ) )

    tasks = widgets.ToggleButtons(
        options=[ 'Both', 'SKAA', 'Discussion' ],
        description='To Run',
        disabled=False,
        value='Both',
        button_style='',  # 'success', 'info', 'warning', 'danger' or ''
        # tooltips=[ 'Description of slow', 'Description of regular', 'Description of fast' ],
        #     icons=['check'] * 3
    )
    unit_nums = widgets.HBox([start_unit_box, stop_unit_box])
    task_box = widgets.HBox([tasks])

    out = widgets.Output( layout={ 'border': '1px solid black' } )

    button_box = widgets.HBox([b])
    container = widgets.VBox([unit_nums, task_box, button_box, out])


    @out.capture(clear_output=True)
    def callback( change ):
        RUNNING = True
        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )

        # todo very inefficient to have each thing load it's own unit definitions and students
        studentRepo = StudentRepository(environment.CONFIG.course)

        # Move any downloaded report files into the correct location
        file_reports(environment.DOWNLOAD_FOLDER,
                     unit_start=start_unit_box.value,
                     unit_stop=stop_unit_box.value)


        # Instantiate these in the callback in case values have changed
        discussion_runner = RunDiscussionMultipleUnits( start_unit=start_unit_box.value,
                                                        stop_unit=stop_unit_box.value,
                                                        studentRepo=studentRepo)
        skaa_runner = RunSkaaMultipleUnits( start_unit=start_unit_box.value,
                                            stop_unit=stop_unit_box.value,
                                            studentRepo=studentRepo)

        if tasks.value == 'Both':
            # control_store['all_steps'].append(skaa_runner.run(**kwargs))
            # control_store['all_steps'].append(discussion_runner.run(**kwargs))
            control_store.completed_steps = skaa_runner.run(**kwargs)
            control_store.completed_steps = discussion_runner.run(**kwargs)

        elif tasks.value == 'SKAA':
            control_store.completed_steps = skaa_runner.run(**kwargs)

            # control_store['all_steps'].append(skaa_runner.run(**kwargs))

        elif tasks.value == 'Discussion':
            control_store.completed_steps = discussion_runner.run(**kwargs)

            # control_store['all_steps'].append(discussion_runner.run(**kwargs))

        # Load dashboards to summarize student progress
        # will just load both kinds, regardless of what was run
        for unit_number in range(start_unit_box.value, stop_unit_box.value + 1):
            control_store.load_unit(unit_number)

        RUNNING = False

        b.description = get_name( RUNNING )
        b.button_style = get_style( RUNNING )


    b.on_click( callback )

    if return_button is True:
        # If putting inside a box or something else which will
        # call display
        return container
    else:
        display( container )
