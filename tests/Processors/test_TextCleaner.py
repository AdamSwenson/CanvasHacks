"""
Created by adam on 3/11/20
"""
__author__ = 'adam'

from CanvasHacks.Processors.cleaners import TextCleaner
from TestingBase import TestingBase

if __name__ == '__main__':
    pass

TEST_DATA = [ { 'input': '<div><span="dog">¬†¬†¬†¬†¬†¬†¬†¬†¬†¬†¬†</span></div>',
                'expect': ''
                },
              { 'input': 'Agree',
                'expect': 'Agree' },
              { 'input': 45,
                'expect': 45
                },
              { 'input': '<div><span="dog">Dog breath is taco-like.¬†¬† Hmmm¬†¬†¬†¬†¬†¬†¬†¬†¬†</span></div>',
                'expect': 'Dog breath is taco-like. Hmmm'
                },
              { 'input': "Dog breath is taco-like. Hmmm",
                'expect': "Dog breath is taco-like. Hmmm"
                }
              ]


class TestTextCleaner( TestingBase ):

    def setUp( self ) -> None:
        self.config_for_test()
        self.obj = TextCleaner()

    def test_clean( self ):
        for t in TEST_DATA:
            self.assertEqual( t[ 'expect' ], self.obj.clean( t[ 'input' ] ) )
