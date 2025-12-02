"""This replicates the control panel for running at the command line"""

import sys
import os

path = "/".join([a for a in os.path.abspath("").split('/') if a not in ['Notebooks', 'personal']])
sys.path.append(path)

from CanvasHacks.Displays.dashboard import ControlStore
from CanvasHacks.executables.easy_skaa_runner import run_multiple_units

START_UNIT = 1
STOP_UNIT = 7
# MINUTES_REST = 120
MINUTES_REST = 45


REPORT_GEN_TIMEOUT = 25#60
REPORT_ID_ATTEMPTS = 100


def main(start_unit=START_UNIT, stop_unit=STOP_UNIT, minutes_rest=MINUTES_REST):
    path = "/".join([a for a in os.path.abspath("").split('/') if a not in ['Notebooks', 'personal']])
    os.chdir(path)

    control_store = ControlStore()

    print(f"Running for unit {start_unit} to {stop_unit}...")

    try:
        run_multiple_units(control_store, start_unit, stop_unit, minutes_rest, rest_timeout=REPORT_GEN_TIMEOUT,
                           max_id_attempts=REPORT_ID_ATTEMPTS)
    except:
        run_multiple_units(control_store, start_unit, stop_unit, minutes_rest, rest_timeout=REPORT_GEN_TIMEOUT,
                           max_id_attempts=REPORT_ID_ATTEMPTS)


if __name__ == '__main__':
    print(sys.argv)
    try:
        start_unit = int(sys.argv[1]) if sys.argv[1] is not None else START_UNIT
        stop_unit = int(sys.argv[2]) if sys.argv[2] is not None else STOP_UNIT
        # minutes_rest = sys.argv[3] if sys.argv[3] is not None else MINUTES_REST
    except IndexError:
        pass

    main(start_unit, stop_unit)


