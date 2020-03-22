"""
Created by adam on 3/1/20
"""
__author__ = 'adam'

import pandas as pd
from unittest.mock import patch, MagicMock
from CanvasHacks.Definitions.activity import Activity
from CanvasHacks.Definitions.unit import Unit
from CanvasHacks.PeerReviewed.SkaaMaker import UnitDefinitionsLoader
from tests.TestingBase import TestingBase
import CanvasHacks.environment as env
from faker import Faker
fake = Faker()
import pytz

if __name__ == '__main__':
    pass


class TestUnitDefinitionsLoader( TestingBase ):

    def setUp(self):
        self.test_datafile = "{}/Unit details.xlsx".format( env.TEST_DATA_PATH)
        self.obj = UnitDefinitionsLoader()
        self.obj.load( self.test_datafile )

    def test_load( self ):
        self.assertIsInstance( self.obj.unit_details, pd.DataFrame)
        self.assertIsInstance( self.obj.start_dates, pd.DataFrame)

    def test_make_unit( self ):
        unit_number = 3
        start = pd.to_datetime(fake.date_time_this_century( tzinfo=pytz.utc ))
        u = self.obj.make_unit(unit_number, start)

        # Check
        self.assertIsInstance(u, Unit)
        self.assertEqual(u.unit_number, unit_number)

    def test_create_units( self ):
        self.obj.create_units()

        self.assertTrue(len(self.obj.units) > 0)
        self.assertTrue(len(self.obj.units) == 5)

        for unit in self.obj.units:
            for tp in unit.components:
                self.assertIsInstance(tp, Activity)

    @patch('CanvasHacks.PeerReviewed.SkaaMaker.UnitDefinitionsLoader.CreationHandlerFactory')
    def test_run( self, makerMock ):
        self.obj.create_units()
        course = MagicMock()

        self.run(course)

        course.assert_called()
    #     obj = UnitDefinitionsLoader()
    #     obj.load( self.test_datafile )
    #
    #     obj.run()

