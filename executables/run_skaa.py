"""This replicates the control panel for running at the command line"""

import sys
import os

path = "/".join([a for a in os.path.abspath("").split('/') if a not in ['Notebooks', 'personal']])
sys.path.append(path)

from CanvasHacks.Displays.dashboard import ControlStore
from CanvasHacks.executables.easy_skaa_runner import run_multiple_units

# Default values that can be overwritten by args
START_UNIT = 1
STOP_UNIT = 7
MINUTES_REST = 45
REPORT_GEN_TIMEOUT = 25#60
REPORT_ID_ATTEMPTS = 100


def main(start_unit=START_UNIT, stop_unit=STOP_UNIT, minutes_rest=MINUTES_REST, report_gen_timeout=REPORT_GEN_TIMEOUT,):
    """
    Calls run_multiple_units for the provided values
    :param start_unit: First unit to run
    :param stop_unit: Last unit to run
    :param minutes_rest: Minutes to rest between cycles
    :param report_gen_timeout: Seconds to rest to allow API to generate reports
    :return:
    """
    path = "/".join([a for a in os.path.abspath("").split('/') if a not in ['Notebooks', 'personal']])
    os.chdir(path)

    control_store = ControlStore()
    print(f"Report generation time: {report_gen_timeout}")
    print(f"Minutes rest: {minutes_rest}")
    print(f"Running for unit {start_unit} to {stop_unit}...")

    run_multiple_units(control_store, start_unit, stop_unit, minutes_rest, rest_timeout=REPORT_GEN_TIMEOUT,
                       max_id_attempts=REPORT_ID_ATTEMPTS)

    # Exception catching makes it hard to shut down using control + c
    # try:
    #   run_multiple_units(control_store, start_unit, stop_unit, minutes_rest, rest_timeout=REPORT_GEN_TIMEOUT, max_id_attempts=REPORT_ID_ATTEMPTS)
    # except:
    #     run_multiple_units(control_store, start_unit, stop_unit, minutes_rest, rest_timeout=REPORT_GEN_TIMEOUT, max_id_attempts=REPORT_ID_ATTEMPTS)


if __name__ == '__main__':
    # Parse out the sys.argv to use as arguments to main
    args = {
        'start_unit' : START_UNIT,
        'stop_unit' : STOP_UNIT,
        'minutes_rest' : MINUTES_REST,
        'report_gen_timeout' : REPORT_GEN_TIMEOUT
    }

    keys = list(args)
    idx = 0
    for arg in sys.argv[ 1: ]:
        args[keys[idx]] = int(arg)
        idx += 1

    # Call the wrapper
    main(**args)
