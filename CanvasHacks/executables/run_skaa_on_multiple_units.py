"""
Created by adam on 4/9/20
"""
__author__ = 'adam'

from CanvasHacks.Definitions.unit import Unit
from CanvasHacks.SkaaSteps.SendInitialWorkToReviewer import SendInitialWorkToReviewer
from CanvasHacks.SkaaSteps.SendMetareviewToReviewer import SendMetareviewToReviewer
from CanvasHacks.SkaaSteps.SendReviewToReviewee import SendReviewToReviewee

from CanvasHacks import environment
from CanvasHacks.executables.run_skaa_on_single_unit import run_all_steps


class RunSkaaMultipleUnits:

    def __init__(self, start_unit, stop_unit, **kwargs):

        self.stop_unit = stop_unit
        self.start_unit = start_unit

    def run( self, **kwargs ):
        """

        run all steps parameters include
            SEND=True,
            download=True
        :param kwargs:
        :return:
        """
        results = {}
        for unit_number in range(self.start_unit, self.stop_unit + 1):
            print( "\n~~~~~~~~~~~~~~~~~~~~~~ UNIT {} ~~~~~~~~~~~~~~~~~~~~~~".format(unit_number))

            # Set the unit on environment
            environment.CONFIG.set_unit_number( unit_number)
            environment.CONFIG.initialize_canvas_objs()
            environment.CONFIG.unit = Unit( environment.CONFIG.course, unit_number )

            results[unit_number] = run_all_steps( **kwargs )
        return results


if __name__ == '__main__':
    # todo Add stuff here to grab command line arguments and set the unit
    pass

