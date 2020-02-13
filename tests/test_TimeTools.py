"""
Created by adam on 2/10/20
"""
from unittest import TestCase
from CanvasHacks.TimeTools import *
import pandas as pd

__author__ = 'adam'

if __name__ == '__main__':
    pass


class TestTimeConverstions( TestCase ):
    def test_local_string_to_utc_dt( self ):
        v = '2020-02-14T23:59:00'
        e =  pd.to_datetime('2020-02-15 07:59:00').tz_localize('UTC')

        r = local_string_to_utc_dt(v)

        self.assertEqual(r, e)

    def test_utc_string_to_local_dt(self):
        pass
        # Timestamp('2020-02-15 07:59:00+0000', tz='UTC')