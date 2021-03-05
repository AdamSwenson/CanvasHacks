"""
Created by adam on 3/5/21
"""
__author__ = 'adam'

import datetime
from time import sleep

from CanvasHacks import environment
from CanvasHacks.Displays.dashboard import ControlStore
from CanvasHacks.Files.FromDownloadFolder import file_reports
from CanvasHacks.Repositories.students import StudentRepository
from CanvasHacks.executables.run_skaa_on_multiple_units import RunSkaaMultipleUnits


def run_multiple_units( control_store, start_unit=0, stop_unit=8, rest_minutes=30, **kwargs ):
    """

    :param stop_unit:
    :param rest_minutes:
    :param start_unit:
    :param control_store:
    :param kwargs: these can include SEND. If want to do dry run, SEND=False should be passed in here. Association between author and reviewer will not be recorded.
    :return:
    """

    # todo very inefficient to have each thing load it's own unit definitions and students
    studentRepo = StudentRepository( environment.CONFIG.course )

    while True:
        print( datetime.datetime.isoformat( datetime.datetime.now() ) )
        print( 'RUNNING' )

        # Move any downloaded report files into the correct location
        file_reports( environment.DOWNLOAD_FOLDER,
                      unit_start=start_unit,
                      unit_stop=stop_unit )

        try:
            # Instantiate these in the callback in case values have changed
            # discussion_runner = RunDiscussionMultipleUnits( start_unit=start_unit,
            #                                                 stop_unit=stop_unit, studentRepo=studentRepo )

            skaa_runner = RunSkaaMultipleUnits( start_unit=start_unit,
                                                stop_unit=stop_unit,
                                                studentRepo=studentRepo )
            control_store.completed_steps = skaa_runner.run( **kwargs )

        except ConnectionError as e:
            print( e )
            # break

        stop_time = datetime.datetime.now()
        control_store.save_run_data( run_timestamp=stop_time )
        print( datetime.datetime.isoformat( stop_time ) )
        print( 'RESTING' )
        rest_seconds = rest_minutes * 60
        sleep( rest_seconds )



def main():
    control_store = ControlStore();
    run_multiple_units( control_store, start_unit=0, stop_unit=8, rest_minutes=30 )





if __name__ == '__main__':
    main()
