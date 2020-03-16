"""
Created by adam on 3/11/20
"""
__author__ = 'adam'

from unittest import TestCase

from CanvasHacks.Processors.cleaners import UtfCleaner
from TestingBase import TestingBase

if __name__ == '__main__':
    pass

TEST_DATA =[ {'input': '¬†¬†¬†¬†¬†¬†¬†¬†¬†¬†¬†',
             'expect': ''
             },
             {'input': 'Good text that ïuh oh.',
              'expect': 'Good text that uh oh.'},
             {'input': "Dog breath is taco-like. Hmmm",
              'expect': "Dog breath is taco-like. Hmmm"
              }
]

class TestUtfCleaner( TestingBase ):

    def setUp(self) -> None:
        self.config_for_test()
        self.obj = UtfCleaner()

    def test_clean( self ):
        for t in TEST_DATA:
            self.assertEqual(t['expect'], self.obj.clean(t['input']))
