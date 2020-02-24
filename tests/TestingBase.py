"""
Created by adam on 2/22/20
"""
__author__ = 'adam'

import CanvasHacks.globals

CanvasHacks.globals.TEST = True
CanvasHacks.globals.use_api = False

from CanvasHacks import environment as env

import unittest


if __name__ == '__main__':
    pass


class TestingBase(unittest.TestCase):

    def config_for_test( self ):
        print('setting test')
        env.CONFIG.set_test()
