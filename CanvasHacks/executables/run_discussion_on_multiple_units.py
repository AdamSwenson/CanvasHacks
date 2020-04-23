"""
Created by adam on 4/9/20
"""
__author__ = 'adam'

from CanvasHacks import environment
from CanvasHacks.Definitions.unit import Unit
from CanvasHacks.Errors.data_ingestion import NoStudentWorkDataLoaded
from CanvasHacks.executables.run_discussion_on_single_unit import run_discussion_steps


class RunDiscussionMultipleUnits:

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
            print( "\n~~~~~~~~~~~~~~~~~~~ Discussions ~~~~~~~~~~~~~~~~~~~")
            print( "\n~~~~~~~~~~~~~~~~~~~~~~ UNIT {} ~~~~~~~~~~~~~~~~~~~~~~".format(unit_number))

            # Set the unit on environment
            # As of CAN-68 we use the method which will check if the object
            # is already stored to save calls to the api
            environment.CONFIG.set_unit(unit_number)
            # environment.CONFIG.set_unit_number( unit_number)
            # environment.CONFIG.initialize_canvas_objs()
            # environment.CONFIG.unit = Unit( environment.CONFIG.course, unit_number )
            try:
                results[unit_number] = run_discussion_steps( **kwargs )
            except NoStudentWorkDataLoaded as e:
                print("Error: No student work data loaded")


        return results


if __name__ == '__main__':
    # todo Add stuff here to grab command line arguments and set the unit
    pass
